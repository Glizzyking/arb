from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import datetime
import pytz
import asyncio
import json
from contextlib import asynccontextmanager
import requests


# Import from new tracker module
from tracker.config import CRYPTO_CONFIGS, CryptoConfig, KALSHI_API_BASE
from tracker.market_generator import MarketURLGenerator
from tracker.api_clients import KalshiClient, PolymarketClient

# Import WebSocket components
from websocket.manager import ws_manager
from websocket.polymarket_stream import polymarket_stream
from websocket.kalshi_stream import kalshi_stream

# Import historical EV service
from services.historical_ev import historical_ev_service
# Import spreads service
from services.spreads import spreads_service

# Global cache for Positive EV opportunities
PEV_CACHE = {
    "opportunities": [],
    "last_updated": None
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start all streams
    # Initialize historical data once at startup
    asyncio.create_task(update_historical_data_task())
    
    
    # 2. Start Poly & Kalshi (need discovery first)
    # We'll initialize these correctly in a background task that periodically checks for new markets
    asyncio.create_task(background_aggregator())
    
    # 3. Start Positive EV background aggregator
    asyncio.create_task(background_positive_ev_aggregator())
    
    logger.info("Real-time streams initialized")
    yield
    # Shutdown
    polymarket_stream.stop()
    kalshi_stream.stop()

async def update_historical_data_task():
    """Periodically updates historical hit rates"""
    while True:
        try:
            # Run in a thread pool since it's blocking I/O
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, historical_ev_service.update_hit_rates)
            logger.info("Historical EV hit rates updated successfully")
            
            # Update once every 24 hours
            await asyncio.sleep(24 * 3600)
        except Exception as e:
            logger.error(f"Error in historical data update task: {e}")
            await asyncio.sleep(3600) # Retry in an hour on error

app = FastAPI(lifespan=lifespan)

# Initialize tracker components
generator = MarketURLGenerator()
kalshi_client = KalshiClient()
polymarket_client = PolymarketClient()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Assets to monitor
MONITORED_ASSETS = {"BTC", "ETH", "XRP", "SOL", "NFL", "NBA"}

import time

# Import the independent price fetcher service
# This module handles Polymarket scraping with Binance.US fallback
from services.price_fetcher import price_fetcher


async def background_aggregator():
    """Periodically refreshes market discovery and broadcasts latest data for active assets"""
    market_info_cache = {}
    last_discovery_time = 0
    
    while True:
        try:
            now = time.time()
            # 1. Discovery Phase (Every 5 minutes or if cache empty)
            if now - last_discovery_time > 300 or not market_info_cache:
                logger.info("Refreshing market discovery cache...")
                # Smart Rollover: Target current hour closing unless near the end
                current_offset = 1 if datetime.datetime.now().minute >= 55 else 0
                
                for asset_code in list(MONITORED_ASSETS):
                    config = CRYPTO_CONFIGS.get(asset_code)
                    if config:
                        try:
                            info = generator.get_market_pair(config, kalshi_client, hours_offset=current_offset)
                            market_info_cache[asset_code] = info
                            # Update Poly (Token IDs)
                            polymarket_stream.add_market(asset_code, info["polymarket"]["slug"])
                            # Update Kalshi (Ticker)
                            kalshi_stream.add_ticker(asset_code, info["kalshi"]["ticker"])
                        except Exception as e:
                            logger.error(f"Discovery failed for {asset_code}: {e}")
                
                last_discovery_time = now
                
                last_discovery_time = now
                
                # Ensure streams are running
                if not polymarket_stream.is_running:
                    asyncio.create_task(polymarket_stream.start())
                if not kalshi_stream.is_running:
                    asyncio.create_task(kalshi_stream.start())

            # 2. Update & Broadcast Phase (Every second)
            for asset_code, info in market_info_cache.items():
                config = CRYPTO_CONFIGS.get(asset_code)
                if not config: continue
                
                # Get latest data from streams
                poly_prices = polymarket_stream.get_latest_prices(asset_code)
                kalshi_markets_raw = kalshi_stream.get_latest_markets(asset_code)
                
                # Get Polymarket's "Price to Beat" using the independent price fetcher
                # Primary: Polymarket scrape, Fallback: Binance.US
                price_result = price_fetcher.get_price_to_beat(asset_code, info["polymarket"]["slug"])
                price_to_beat = price_result.price
                
                kalshi_markets = []
                for m in kalshi_markets_raw:
                    strike = float(m.get("floor_strike", 0) or 0)
                    yes_ask = int(m.get("yes_ask", 0))
                    no_ask = int(m.get("no_ask", 0))
                    yes_qty = int(m.get("yes_ask_quantity", 0))
                    no_qty = int(m.get("no_ask_quantity", 0))
                    
                    if strike > 0:
                        kalshi_markets.append({
                            "strike": strike,
                            "yes_ask": yes_ask,
                            "no_ask": no_ask,
                            "yes_count": yes_qty,
                            "no_count": no_qty,
                            "subtitle": m.get("subtitle", f"Above ${strike:,.2f}")
                        })
                
                # Use real depth from the new stream structure
                up_outcome_data = poly_prices.get("Up", {})
                down_outcome_data = poly_prices.get("Down", {})
                
                poly_data = {
                    "price_to_beat": price_to_beat,
                    "current_price": 0.0,
                    "prices": poly_prices, # Now returns {outcome: {ask, bid, size}}
                    "up_count": int(up_outcome_data.get("size", 0) if isinstance(up_outcome_data, dict) else 0),
                    "down_count": int(down_outcome_data.get("size", 0) if isinstance(down_outcome_data, dict) else 0),
                    "slug": info["polymarket"]["slug"],
                    "url": info["polymarket"]["url"],
                    "asset": asset_code
                }
                
                kalshi_data = {
                    "event_ticker": info["kalshi"]["ticker"],
                    "current_price": 0.0,  # Not used for arbitrage calculation
                    "markets": sorted(kalshi_markets, key=lambda x: x["strike"]),
                    "url": info["kalshi"]["url"],
                    "asset": asset_code
                }
                
                full_response = calculate_arbitrage_logic(poly_data, kalshi_data)
                full_response["asset"] = asset_code
                
                # Skip broadcasting if Kalshi markets are empty (stream not ready yet)
                if not kalshi_markets:
                    continue
                
                # Broadcast
                await ws_manager.broadcast(full_response)
                
        except Exception as e:
            logger.error(f"Aggregator error: {e}")
            
        await asyncio.sleep(1) # Broadcast cycle

@app.websocket("/ws/arbitrage")
async def websocket_endpoint(websocket: WebSocket):
    logger.info(f"Incoming WebSocket connection from {websocket.client}")
    await ws_manager.connect(websocket)
    logger.info("WebSocket connection established and accepted")
    try:
        while True:
            try:
                # Use timeout to allow checking for closed connection
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                try:
                    msg = json.loads(data)
                    if msg.get("type") == "subscribe":
                        asset = msg.get("asset")
                        logger.info(f"Client subscribed to {asset}")
                        if asset in CRYPTO_CONFIGS:
                            MONITORED_ASSETS.add(asset)
                except json.JSONDecodeError:
                    pass
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                try:
                    await websocket.send_json({"type": "ping"})
                except:
                    break
    except WebSocketDisconnect:
        pass
    finally:
        ws_manager.disconnect(websocket)


class CustomTokenConfig(BaseModel):
    """Request body for custom token arbitrage check"""
    name: str
    kalshi_series: str
    polymarket_slug_prefix: str
    binance_symbol: Optional[str] = "BTCUSD"


from tracker.config import CRYPTO_CONFIGS, CryptoConfig, KALSHI_API_BASE, GLOBAL_SETTINGS
from tracker.kelly_service import KellyService

kelly_service = KellyService()

import json
import os

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")

def load_settings():
    """Load settings from JSON file if it exists"""
    global GLOBAL_SETTINGS
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                if "bankroll" in data:
                    GLOBAL_SETTINGS["total_bankroll"] = float(data["bankroll"])
                if "assets" in data:
                    for symbol, cfg in data["assets"].items():
                        if symbol in CRYPTO_CONFIGS:
                            if "max_gap" in cfg:
                                CRYPTO_CONFIGS[symbol].max_gap = float(cfg["max_gap"])
            logger.info(f"Loaded persistent settings from {SETTINGS_FILE}")
        except Exception as e:
            logger.error(f"Error loading settings: {e}")

def save_settings():
    """Save current settings to JSON file"""
    try:
        data = {
            "bankroll": GLOBAL_SETTINGS["total_bankroll"],
            "assets": {k: {"max_gap": v.max_gap} for k, v in CRYPTO_CONFIGS.items()}
        }
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f, indent=4)
        logger.info(f"Saved settings to {SETTINGS_FILE}")
    except Exception as e:
        logger.error(f"Error saving settings: {e}")

# Initial load on startup
load_settings()

@app.get("/api/settings")
def get_settings():
    return {
        "bankroll": GLOBAL_SETTINGS["total_bankroll"],
        "assets": {k: {"max_gap": v.max_gap} for k, v in CRYPTO_CONFIGS.items()}
    }

@app.post("/api/settings")
def update_settings(data: Dict[str, Any]):
    global GLOBAL_SETTINGS
    if "bankroll" in data:
        GLOBAL_SETTINGS["total_bankroll"] = float(data["bankroll"])
    
    if "assets" in data:
        for symbol, cfg in data["assets"].items():
            if symbol in CRYPTO_CONFIGS:
                if "max_gap" in cfg:
                    CRYPTO_CONFIGS[symbol].max_gap = float(cfg["max_gap"])
    
    save_settings()
    return {"status": "success", "settings": get_settings()}


def calculate_arbitrage_logic(poly_data, kalshi_data):
    """Common arbitrage calculation logic - Enhanced with Kelly & Depth"""
    asset_code = poly_data.get('asset', 'BTC')
    config = CRYPTO_CONFIGS.get(asset_code)
    min_gap = config.min_gap if config else 0
    max_gap = config.max_gap if config else float('inf')
    
    response = {
        "timestamp": datetime.datetime.now().isoformat(),
        "polymarket": poly_data,
        "kalshi": kalshi_data,
        "checks": [],
        "opportunities": [],
        "errors": []
    }
    
    if not poly_data or not kalshi_data:
        return response

    poly_strike = poly_data.get('price_to_beat')
    # Robust Price Extraction for Polymarket
    prices = poly_data.get('prices', {})
    
    # Try getting UP price dictionary
    up_dict = prices.get('Up', prices.get('Yes', prices.get('up', prices.get('yes', {}))))
    # Fix: Use 'ask' instead of 'price_ask' to match tracker/api_clients.py
    poly_up_cost = up_dict.get('ask', 0.0) if isinstance(up_dict, dict) else float(up_dict or 0)
    
    # Try getting DOWN price dictionary
    down_dict = prices.get('Down', prices.get('No', prices.get('down', prices.get('no', {}))))
    # Fix: Use 'ask' instead of 'price_ask' to match tracker/api_clients.py
    poly_down_cost = down_dict.get('ask', 0.0) if isinstance(down_dict, dict) else float(down_dict or 0)
    
    # Extract depth from Poly
    poly_up_count = poly_data.get('up_count', 0)
    poly_down_count = poly_data.get('down_count', 0)
    
    polymarket_url = poly_data.get('url', '')
    kalshi_url = kalshi_data.get('url', '')
    
    if poly_strike is None:
        response["errors"].append("Polymarket Strike is None")
        return response

    kalshi_markets = kalshi_data.get('markets', [])
    if not kalshi_markets:
        response["errors"].append("No Kalshi markets found")
        return response
    
    kalshi_markets.sort(key=lambda x: x['strike'])
    
    print(f"\n--- Simulation for {asset_code} ---")
    print(f"Polymarket Strike: {poly_strike}")
    
    # Matching logic
    for km in kalshi_markets:
        kalshi_strike = km['strike']
        k_yes = float(km.get('yes_ask', 0))
        k_no = float(km.get('no_ask', 0))
        gap = abs(poly_strike - kalshi_strike)
        
        # Simulation Status (Visual Filter)
        # Filter out anything with zeros as per user: "filter out anything that has zeros because that doesn't mean there's a market"
        is_valid_price = (k_yes > 0 and k_no > 0 and k_yes < 100 and k_no < 100)
        is_in_gap = gap <= max_gap
        
        # Determine status for logging
        status = "✅ PASS" if (is_valid_price and is_in_gap) else "❌ FAIL"
        
        # Log nearby strikes for visual verification (up to 2x max_gap)
        if gap < max_gap * 2.0 or gap < 500: # Ensure we show context for smaller assets too
            print(f"Strike: {kalshi_strike:10.2f} | Gap: {gap:10.2f} | Yes: {k_yes:5.1f} | No: {k_no:5.1f} | {status}")
            if not is_in_gap:
                print(f"   -> Fail Reason: Gap {gap:.2f} > Max {max_gap}")
            elif not is_valid_price:
                print(f"   -> Fail Reason: Market Dead (Has Zero/100 Prices)")

        # SKIP IF INVALID (User request: "filter out anything that has zeros")
        if not is_valid_price:
            continue
        
        # Access depth from Kalshi
        k_yes_count = km.get('yes_count', 0)
        k_no_count = km.get('no_count', 0)


        kalshi_yes_cost = km['yes_ask'] / 100.0
        kalshi_no_cost = km['no_ask'] / 100.0
        
        # Access depth from Kalshi
        k_yes_count = km.get('yes_count', 0)
        k_no_count = km.get('no_count', 0)
            
        check_data = {
            "kalshi_strike": kalshi_strike,
            "kalshi_yes": kalshi_yes_cost,
            "kalshi_no": kalshi_no_cost,
            "gap": abs(poly_strike - kalshi_strike),
            "type": "",
            "poly_leg": "",
            "kalshi_leg": "",
            "poly_cost": 0,
            "kalshi_cost": 0,
            "total_cost": 0,
            "is_arbitrage": False,
            "margin": 0,
            "available_contracts": 0,
            "kelly": {},
            "polymarket_url": polymarket_url,
            "kalshi_url": kalshi_url
        }

        # Determine which leg combination we are checking
        if poly_strike > kalshi_strike:
            check_data["type"] = "Poly > Kalshi"
            check_data["poly_leg"] = "Down"
            check_data["kalshi_leg"] = "Yes"
            check_data["poly_cost"] = poly_down_cost
            check_data["kalshi_cost"] = kalshi_yes_cost
            check_data["available_contracts"] = min(poly_down_count, k_yes_count)
            
        elif poly_strike < kalshi_strike:
            check_data["type"] = "Poly < Kalshi"
            check_data["poly_leg"] = "Up"
            check_data["kalshi_leg"] = "No"
            check_data["poly_cost"] = poly_up_cost
            check_data["kalshi_cost"] = kalshi_no_cost
            check_data["available_contracts"] = min(poly_up_count, k_no_count)
            
        else: # Equal
             check_data["type"] = "Equal"
             # For equal strikes, we just check YES/NO cross
             check_data["total_cost"] = poly_down_cost + kalshi_yes_cost
             check_data["available_contracts"] = min(poly_down_count, k_yes_count)

        check_data["total_cost"] = check_data["poly_cost"] + check_data["kalshi_cost"]
        
        # Determine if it's a valid profitable arb
        # We allow 0 liquidity through to the UI if it passed the Gap/Price check above
        is_profitable = 0 < check_data["total_cost"] < 1.00
        is_valid_poly = 0 < check_data["poly_cost"] < 1.00
        is_valid_kalshi = 0 < check_data["kalshi_cost"] < 1.00
        has_liquidity = check_data["available_contracts"] > 0

        
        # DEBUG: Log profitability check values
        logger.info(f"[Profitability] {asset_code} strike {kalshi_strike}: total={check_data['total_cost']:.3f}, poly={check_data['poly_cost']:.3f}, kalshi={check_data['kalshi_cost']:.3f}")

        # Profitable gap check & Price Guards
        # price > 0 AND price < 1.0 (valid sellers) for both sides
        # We ignore quantities for the "theoretical" arbitrage view
        is_profitable = 0 < check_data["total_cost"] < 1.00
        is_valid_poly = 0 < check_data["poly_cost"] < 1.00
        is_valid_kalshi = 0 < check_data["kalshi_cost"] < 1.00
        
        # DEBUG: Log boolean values
        if 65000 < kalshi_strike < 66000:  # Only log strikes near poly strike
            logger.info(f"[Booleans] {asset_code} strike {kalshi_strike}: profitable={is_profitable}, valid_poly={is_valid_poly}, valid_kalshi={is_valid_kalshi}, combined={is_profitable and is_valid_poly and is_valid_kalshi}")

        # Apply GAP Range filter FIRST (show opportunities regardless of profitability)
        gap_abs = abs(check_data["gap"])
        logger.info(f"[Gap Check] {asset_code} strike {kalshi_strike}: gap_abs={gap_abs:.2f}, min={min_gap}, max={max_gap}, passes={min_gap <= gap_abs <= max_gap}")
        
        if min_gap <= gap_abs <= max_gap:
            # Only set profitability flags if it's actually profitable AND has liquidity
            if is_profitable and is_valid_poly and is_valid_kalshi and has_liquidity:
                # KELLY CALCULATION
                odds_b = (1.0 / check_data["total_cost"]) - 1.0
                kelly_res = kelly_service.calculate_kelly(odds_b, 0.99)
                check_data["kelly"] = kelly_res
                check_data["is_arbitrage"] = True
                check_data["margin"] = 1.00 - check_data["total_cost"]
                logger.info(f"[Arb Found - Profitable] {asset_code} strike {kalshi_strike} (Gap: {gap_abs:.2f}, Cost: {check_data['total_cost']:.3f})")
            else:
                # Mark as theoretical/non-profitable arb within gap range
                check_data["is_arbitrage"] = False
                check_data["margin"] = 1.00 - check_data["total_cost"]
                check_data["kelly"] = {"kelly_fraction": 0, "f_star_raw": 0, "recommendation": "THEORETICAL"}
                
                # Dynamic log message based on reason
                reason = "NON-PROFITABLE" if not is_profitable else "ZERO-LIQUIDITY"
                logger.info(f"[Arb Found - {reason}] {asset_code} strike {kalshi_strike} (Gap: {gap_abs:.2f}, Cost: {check_data['total_cost']:.3f})")
            
            response["opportunities"].append(check_data)
        else:
            logger.info(f"[Gap Skip] {asset_code} strike {kalshi_strike} (Gap {gap_abs:.2f} outside [{min_gap}, {max_gap}])")

        
        response["checks"].append(check_data)
        
    return response

@app.get("/assets")
def get_assets():
    """Return list of supported assets from CRYPTO_CONFIGS"""
    return {
        "assets": list(CRYPTO_CONFIGS.keys()),
        "config": {k: v.__dict__ for k, v in CRYPTO_CONFIGS.items()}
    }

@app.get("/arbitrage")
def get_arbitrage_data(asset: str = Query(default="BTC", description="Asset symbol (BTC, ETH, XRP, SOL)")):
    """Get arbitrage data for a specific asset using tracker module with real discovery"""
    asset = asset.upper()
    if asset not in CRYPTO_CONFIGS:
        return {"errors": [f"Unsupported asset: {asset}"]}
    
    config = CRYPTO_CONFIGS[asset]
    
    # Calculate hour offset dynamically (match background aggregator logic)
    # Use the minute from the configured timezone
    current_time_et = generator.get_current_time()
    target_offset = 1 if current_time_et.minute >= 55 else 0
    
    # 1. Generate Identifiers with Real Discovery
    market_info = generator.get_market_pair(config, kalshi_client, hours_offset=target_offset)
    real_ticker = market_info["kalshi"]["ticker"]
    polymarket_slug = market_info["polymarket"]["slug"]
    
    # 2. Fetch Data (Binance removed, using placeholders)
    current_price = 0.0
    
    # Polymarket prices (LIVE BETTING DATA)
    poly_prices = polymarket_client.get_market_prices(polymarket_slug)
    if poly_prices and poly_prices.get("outcomes"):
        up_data = poly_prices["outcomes"].get("Up", {})
        down_data = poly_prices["outcomes"].get("Down", {})
        # Consistently use 'ask' as per tracker/api_clients.py
        up_price = up_data.get("ask", 0) if isinstance(up_data, dict) else up_data
        down_price = down_data.get("ask", 0) if isinstance(down_data, dict) else down_data
        logger.info(f"[{asset}] Polymarket LIVE: UP=${up_price:.3f}, DOWN=${down_price:.3f}")
    
    # Kalshi Event (LIVE BETTING DATA)
    kalshi_event = kalshi_client.get_event(real_ticker)
    if kalshi_event and kalshi_event.get("markets"):
        num_markets = len(kalshi_event["markets"])
        logger.info(f"[{asset}] Kalshi LIVE: {num_markets} strike markets for {real_ticker}")
    
    
    # 3. Process Kalshi Data
    kalshi_markets = []
    
    # Get Polymarket's "Price to Beat" from Binance open price cache
    # Get Polymarket's "Price to Beat" using the independent price fetcher
    price_result = price_fetcher.get_price_to_beat(asset, market_info["polymarket"]["slug"])
    price_to_beat = price_result.price
    
    if kalshi_event and kalshi_event.get("markets"):
        for m in kalshi_event["markets"]:
            strike = float(m.get("floor_strike", 0) or 0)
            if strike > 0:
                kalshi_markets.append({
                    "strike": strike,
                    "yes_ask": int(m.get("yes_ask", 0)),
                    "no_ask": int(m.get("no_ask", 0)),
                    "yes_count": int(m.get("yes_ask_quantity", 0)), # LIQUIDITY DEPTH
                    "no_count": int(m.get("no_ask_quantity", 0)),   # LIQUIDITY DEPTH
                    "subtitle": m.get("subtitle", f"Above ${strike:,.2f}")
                })
        
        # Sort by strike
        kalshi_markets.sort(key=lambda x: x["strike"])
            
    # 4. Map to old format
    poly_data = None
    if poly_prices:
        # Depth is returned as 'ask_count' from the CLOB API in api_clients.py
        up_data = poly_prices["outcomes"].get("Up", {})
        down_data = poly_prices["outcomes"].get("Down", {})
        
        up_count = up_data.get("ask_count", 0) if isinstance(up_data, dict) else 0
        down_count = down_data.get("ask_count", 0) if isinstance(down_data, dict) else 0

        poly_data = {
            "price_to_beat": price_to_beat,
            "current_price": current_price,
            "prices": poly_prices["outcomes"],
            "up_count": int(up_count),
            "down_count": int(down_count),
            "slug": polymarket_slug,
            "url": market_info["polymarket"]["url"],
            "asset": asset
        }
    
    kalshi_data = None
    if kalshi_markets:
        kalshi_data = {
            "event_ticker": real_ticker,
            "current_price": current_price,
            "markets": kalshi_markets,
            "url": market_info["kalshi"]["url"],
            "asset": asset
        }
    
    response = calculate_arbitrage_logic(poly_data, kalshi_data)
    response["asset"] = asset
    return response


# Import Systematic Filter agent
from services.systematic_filter import systematic_filter_service

def refresh_pev_cache_sync():
    """Synchronous discovery logic to be run in a thread"""
    global PEV_CACHE
    try:
        logger.info("Executing periodic Positive EV discovery...")
        live_markets = {}
        
        # Fetch live markets for all monitored assets
        for asset in MONITORED_ASSETS:
            try:
                # Check if asset is crypto (in configs) or sports
                config = CRYPTO_CONFIGS.get(asset)
                if config:
                    # For crypto, use existing generator
                    logger.info(f"[PEV Discovery] Scanning Crypto: {asset}")
                    market_info = generator.get_market_pair(config, kalshi_client, hours_offset=1)
                    ticker = market_info["kalshi"]["ticker"]
                    slug = market_info["polymarket"]["slug"]
                    
                    # Fetch Kalshi event
                    event = kalshi_client.get_event(ticker)
                    
                    # Fetch Polymarket price (critical for Crypto PEV)
                    poly_prices = polymarket_client.get_market_prices(slug)
                    
                    if event and event.get("markets"):
                        markets_with_poly = []
                        for fm in event["markets"]:
                            fm['strike_label'] = None
                            fm['url'] = generator.generate_kalshi_url(config, fm.get('ticker', ''))
                            
                            # Inject Polymarket data into the market object if available
                            if poly_prices and poly_prices.get("outcomes"):
                                fm['poly_ask'] = poly_prices["outcomes"].get("Down" if asset == 'BTC' else "No", 0) * 100
                            
                            markets_with_poly.append(fm)
                        live_markets[asset] = markets_with_poly
                    time.sleep(1.0) # Rate limit protection
                elif asset in ['NFL', 'NBA']:
                    # Sports Discovery Logic
                    try:
                        # 1. Discovery via Kalshi "Multi-Game" Markets
                        all_markets_url = f"{KALSHI_API_BASE}/markets"
                        res = requests.get(all_markets_url, params={'status': 'open', 'limit': 100}, timeout=10)
                        if res.status_code == 200:
                            all_m = res.json().get('markets', [])
                            sports_containers = [
                                m for m in all_m 
                                if 'KXMVESPORTS' in m.get('ticker', '') or 
                                asset in m.get('ticker', '') or 
                                asset in m.get('title', '').upper()
                            ][:50]
                            
                            leg_cache = {}
                            for container in sports_containers:
                                container_ticker = container.get('ticker')
                                det_url = f"{KALSHI_API_BASE}/markets/{container_ticker}"
                                time.sleep(0.05)
                                det_res = requests.get(det_url, timeout=5)
                                
                                if det_res.status_code == 200:
                                    detailed_market = det_res.json().get('market', {})
                                    legs = detailed_market.get('mve_selected_legs', [])
                                    for leg in legs:
                                        leg_ticker = leg.get('market_ticker')
                                        if not leg_ticker or asset not in leg_ticker: continue
                                        if leg_ticker in leg_cache:
                                            if asset not in live_markets: live_markets[asset] = []
                                            live_markets[asset].append(leg_cache[leg_ticker])
                                            continue
                                        
                                        time.sleep(0.05)
                                        leg_url = f"{KALSHI_API_BASE}/markets/{leg_ticker}"
                                        leg_res = requests.get(leg_url, timeout=5)
                                        if leg_res.status_code == 200:
                                            lm = leg_res.json().get('market', {})
                                            strike_label = "WIN" if "win" in lm.get('title', '').lower() else "MATCH"
                                            if any(k in lm.get('title', '').lower() for k in ["point", "three"]):
                                                strike_label = "PROP"
                                            
                                            # Construct slugged URL for sports
                                            # Pattern: /markets/{series_ticker}/{series_title_slug}/{event_ticker}
                                            series_ticker = lm.get('series_ticker', asset).lower()
                                            series_slug = generator.slugify(container.get('title', ''))
                                            event_ticker = lm.get('event_ticker', lm.get('ticker', '')).lower()
                                            sports_url = f"https://kalshi.com/markets/{series_ticker}/{series_slug}/{event_ticker}"

                                            normalized_market = {
                                                'ticker': lm.get('ticker'),
                                                'title': lm.get('title'),
                                                'subtitle': lm.get('subtitle', container.get('title')),
                                                'parent_event_title': lm.get('title'),
                                                'yes_ask': lm.get('yes_ask'),
                                                'yes_bid': lm.get('yes_bid'),
                                                'floor_strike': 0.5,
                                                'strike_label': strike_label,
                                                'expiration_time': lm.get('expiration_time'),
                                                'url': sports_url
                                            }
                                            leg_cache[leg_ticker] = normalized_market
                                            if asset not in live_markets: live_markets[asset] = []
                                            live_markets[asset].append(normalized_market)
                    except Exception as e:
                        logger.error(f"Error in Kalshi Sports Discovery for {asset}: {e}")
                        
                    # 2. Discovery via Polymarket
                    try:
                        poly_url = "https://clob.polymarket.com/sampling-markets"
                        poly_res = requests.get(poly_url, timeout=10)
                        if poly_res.status_code == 200:
                            poly_data = poly_res.json()
                            for pm in poly_data.get('data', []):
                                desc = pm.get('description', '').upper()
                                if asset in desc:
                                    normalized_pm = {
                                        'ticker': pm.get('condition_id'),
                                        'subtitle': pm.get('description'),
                                        'parent_event_title': f"{asset} Game",
                                        'yes_ask': float(pm.get('price', 0)) * 100,
                                        'floor_strike': 0.1,
                                    }
                                    if asset not in live_markets: live_markets[asset] = []
                                    live_markets[asset].append(normalized_pm)
                    except Exception as pe:
                        logger.error(f"Error fetching Polymarket {asset} markets: {pe}")
            except Exception as e:
                logger.error(f"Error fetching live markets for {asset}: {e}")
        
        if live_markets:
            PEV_CACHE["opportunities"] = systematic_filter_service.get_all_opportunities(live_markets, min_edge=0.0)
            PEV_CACHE["last_updated"] = datetime.datetime.now().isoformat()
            logger.info(f"Positive EV discovery complete. Found {len(PEV_CACHE['opportunities'])} opportunities.")
        else:
            logger.warning("Positive EV discovery found 0 live markets!")

    except Exception as e:
        logger.error(f"Critical error in discovery thread: {e}")
        
async def background_positive_ev_aggregator():
    """Background task to periodically refresh Positive EV opportunities using a thread"""
    while True:
        try:
            # Run the blocking discovery logic in a thread to keep the event loop responsive
            await asyncio.to_thread(refresh_pev_cache_sync)
        except Exception as e:
            logger.error(f"Error in background_positive_ev_aggregator: {e}")
        
        # Refresh every 5 minutes (slower to avoid Kalshi rate limits)
        await asyncio.sleep(300)

@app.get("/api/positive-ev")
def get_positive_ev(min_edge: float = Query(default=0.02, description="Minimum EV edge threshold")):
    """Get positive EV opportunities from the background cache"""
    if not PEV_CACHE["last_updated"]:
        return {"opportunities": [], "message": "Cache warming up (Discovery in progress)...", "status": "loading"}
        
    # Filter cached opportunities by requested min_edge
    filtered_opps = [opp for opp in PEV_CACHE["opportunities"] if opp["edge"] >= min_edge]
    
    return {
        "opportunities": filtered_opps,
        "last_updated": PEV_CACHE["last_updated"],
        "count": len(filtered_opps)
    }

@app.get("/api/spreads")
async def get_spreads():
    """Get all profitable spreads across all assets"""
    try:
        # We run this in an executor/thread because it performs multiple I/O requests
        spreads = await asyncio.to_thread(spreads_service.get_all_profitable_spreads)
        return {"spreads": spreads}
    except Exception as e:
        logger.error(f"Error fetching spreads: {e}")
        return {"spreads": [], "error": str(e)}


@app.post("/arbitrage/custom")
def get_custom_arbitrage_data(config: CustomTokenConfig):
    """Get arbitrage data for a custom token configuration"""
    # Create temporary CryptoConfig
    custom_crypto = CryptoConfig(
        name=config.name,
        symbol="CUSTOM",
        kalshi_series=config.kalshi_series,
        kalshi_market_base=config.kalshi_series.lower(),
        polymarket_slug_prefix=config.polymarket_slug_prefix,
        binance_symbol=config.binance_symbol or "BTCUSD"
    )
    
    # Reuse the same logic
    # (In a real refactor we'd split the logic into a service, but for this task we can inline or repeat)
    market_info = generator.get_market_pair(custom_crypto, kalshi_client, hours_offset=1)
    real_ticker = market_info["kalshi"]["ticker"]
    polymarket_slug = market_info["polymarket"]["slug"]
    
    current_price = 0.0
    price_to_beat = 0.0
    
    poly_prices = polymarket_client.get_market_prices(polymarket_slug)
    kalshi_event = kalshi_client.get_event(real_ticker)
    
    poly_data = None
    if poly_prices:
        poly_data = {
            "price_to_beat": price_to_beat,
            "current_price": current_price,
            "prices": poly_prices["outcomes"],
            "slug": polymarket_slug,
            "url": market_info["polymarket"]["url"]
        }
    
    kalshi_data = None
    if kalshi_event and kalshi_event.get("markets"):
        markets = []
        for m in kalshi_event["markets"]:
            strike = float(m.get("floor_strike", 0) or 0)
            if strike > 0:
                markets.append({
                    "strike": strike,
                    "yes_ask": int(m.get("yes_ask", 0)),
                    "no_ask": int(m.get("no_ask", 0)),
                    "subtitle": m.get("subtitle", f"Above ${strike:,.2f}")
                })
        kalshi_data = {
            "event_ticker": real_ticker,
            "current_price": current_price,
            "markets": sorted(markets, key=lambda x: x["strike"]),
            "url": market_info["kalshi"]["url"]
        }
    
    response = calculate_arbitrage_logic(poly_data, kalshi_data)
    response["asset"] = config.name
    response["custom"] = True
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

@app.get("/simulate")
def simulate_arbitrage(asset: str = Query(default="BTC", description="Asset symbol")):
    """Simulation endpoint - shows ALL opportunities like diagnostic script"""
    asset = asset.upper()
    if asset not in CRYPTO_CONFIGS:
        return {"error": f"Unsupported asset: {asset}"}
    
    config = CRYPTO_CONFIGS[asset]
    
    # Get market data
    market_info = generator.get_market_pair(config, kalshi_client, hours_offset=1)
    poly_prices = polymarket_client.get_market_prices(market_info["polymarket"]["slug"])
    kalshi_event = kalshi_client.get_event(market_info["kalshi"]["ticker"])
    price_result = price_fetcher.get_price_to_beat(asset, market_info["polymarket"]["slug"])
    
    poly_strike = price_result.price
    poly_down = poly_prices.get("outcomes", {}).get("Down", 0)
    poly_up = poly_prices.get("outcomes", {}).get("Up", 0)
    
    results = []
    
    if kalshi_event and kalshi_event.get("markets"):
        for m in kalshi_event["markets"]:
            strike = float(m.get("floor_strike", 0) or 0)
            if strike == 0:
                continue
                
            yes_ask = int(m.get("yes_ask", 0))
            no_ask = int(m.get("no_ask", 0))
            
            # Calculate gap
            gap = abs(poly_strike - strike)
            
            # Determine leg and cost
            if poly_strike > strike:
                cost = (yes_ask / 100.0) + poly_down
                leg_type = "YES/DOWN"
            else:
                cost = (no_ask / 100.0) + poly_up
                leg_type = "NO/UP"
            
            # Gap filter check
            passes_gap = config.min_gap <= gap <= config.max_gap
            fail_reason = None if passes_gap else f"Gap {gap:.2f} > Max {config.max_gap}"
            
            results.append({
                "strike": strike,
                "gap": gap,
                "yes": yes_ask,
                "no": no_ask,
                "cost": cost,
                "passes": passes_gap,
                "fail_reason": fail_reason,
                "leg_type": leg_type
            })
    
    # Sort by strike
    results.sort(key=lambda x: x["strike"])
    
    return {
        "asset": asset,
        "poly_strike": poly_strike,
        "poly_up": poly_up,
        "poly_down": poly_down,
        "min_gap": config.min_gap,
        "max_gap": config.max_gap,
        "results": results
    }
