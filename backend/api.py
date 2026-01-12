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
from tracker.config import CRYPTO_CONFIGS, CryptoConfig
from tracker.market_generator import MarketURLGenerator
from tracker.api_clients import KalshiClient, PolymarketClient

# Import WebSocket components
from websocket.manager import ws_manager
from websocket.polymarket_stream import polymarket_stream
from websocket.kalshi_stream import kalshi_stream

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start all streams
    # 2. Start Poly & Kalshi (need discovery first)
    # We'll initialize these correctly in a background task that periodically checks for new markets
    asyncio.create_task(background_aggregator())
    
    logger.info("Real-time streams initialized")
    yield
    # Shutdown
    polymarket_stream.stop()
    kalshi_stream.stop()

app = FastAPI(lifespan=lifespan)

# Initialize tracker components
generator = MarketURLGenerator()
kalshi_client = KalshiClient()
polymarket_client = PolymarketClient()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Assets to monitor
MONITORED_ASSETS = {"BTC", "ETH", "XRP", "SOL"}

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
                for asset_code in list(MONITORED_ASSETS):
                    config = CRYPTO_CONFIGS.get(asset_code)
                    if config:
                        try:
                            info = generator.get_market_pair(config, kalshi_client, hours_offset=1)
                            market_info_cache[asset_code] = info
                            # Update Poly (Token IDs)
                            polymarket_stream.add_market(asset_code, info["polymarket"]["slug"])
                            # Update Kalshi (Ticker)
                            kalshi_stream.add_ticker(asset_code, info["kalshi"]["ticker"])
                        except Exception as e:
                            logger.error(f"Discovery failed for {asset_code}: {e}")
                
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
                    if strike > 0:
                        kalshi_markets.append({
                            "strike": strike,
                            "yes_ask": int(m.get("yes_ask", 0)),
                            "no_ask": int(m.get("no_ask", 0)),
                            "subtitle": m.get("subtitle", f"Above ${strike:,.2f}")
                        })
                
                poly_data = {
                    "price_to_beat": price_to_beat,
                    "current_price": 0.0,  # Not used for arbitrage calculation
                    "prices": poly_prices,
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
    await ws_manager.connect(websocket)
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


def calculate_arbitrage_logic(poly_data, kalshi_data):
    """Common arbitrage calculation logic - Adapted to keep same format"""
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
    poly_up_cost = poly_data.get('prices', {}).get('Up', 0.0)
    poly_down_cost = poly_data.get('prices', {}).get('Down', 0.0)
    
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
    
    # Matching logic
    for km in kalshi_markets:
        kalshi_strike = km['strike']
        kalshi_yes_cost = km['yes_ask'] / 100.0
        kalshi_no_cost = km['no_ask'] / 100.0
            
        check_data = {
            "kalshi_strike": kalshi_strike,
            "kalshi_yes": kalshi_yes_cost,
            "kalshi_no": kalshi_no_cost,
            "type": "",
            "poly_leg": "",
            "kalshi_leg": "",
            "poly_cost": 0,
            "kalshi_cost": 0,
            "total_cost": 0,
            "is_arbitrage": False,
            "margin": 0,
            "polymarket_url": polymarket_url,
            "kalshi_url": kalshi_url
        }

        if poly_strike > kalshi_strike:
            check_data["type"] = "Poly > Kalshi"
            check_data["poly_leg"] = "Down"
            check_data["kalshi_leg"] = "Yes"
            check_data["poly_cost"] = poly_down_cost
            check_data["kalshi_cost"] = kalshi_yes_cost
            check_data["total_cost"] = poly_down_cost + kalshi_yes_cost
            
        elif poly_strike < kalshi_strike:
            check_data["type"] = "Poly < Kalshi"
            check_data["poly_leg"] = "Up"
            check_data["kalshi_leg"] = "No"
            check_data["poly_cost"] = poly_up_cost
            check_data["kalshi_cost"] = kalshi_no_cost
            check_data["total_cost"] = poly_up_cost + kalshi_no_cost
            
        elif poly_strike == kalshi_strike:
            # Check both directions for equal strikes
            for p_leg, k_leg, p_cost, k_cost in [("Down", "Yes", poly_down_cost, kalshi_yes_cost), ("Up", "No", poly_up_cost, kalshi_no_cost)]:
                c = check_data.copy()
                c["type"] = "Equal"
                c["poly_leg"] = p_leg
                c["kalshi_leg"] = k_leg
                c["poly_cost"] = p_cost
                c["kalshi_cost"] = k_cost
                c["total_cost"] = p_cost + k_cost
                if c["total_cost"] < 1.00:
                    c["is_arbitrage"] = True
                    c["margin"] = 1.00 - c["total_cost"]
                    response["opportunities"].append(c)
                response["checks"].append(c)
            continue

        if check_data["total_cost"] < 1.00:
            check_data["is_arbitrage"] = True
            check_data["margin"] = 1.00 - check_data["total_cost"]
            response["opportunities"].append(check_data)
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
    
    # 1. Generate Identifiers with Real Discovery
    market_info = generator.get_market_pair(config, kalshi_client, hours_offset=1)
    real_ticker = market_info["kalshi"]["ticker"]
    polymarket_slug = market_info["polymarket"]["slug"]
    
    # 2. Fetch Data (Binance removed, using placeholders)
    current_price = 0.0
    
    # Polymarket prices (LIVE BETTING DATA)
    poly_prices = polymarket_client.get_market_prices(polymarket_slug)
    if poly_prices and poly_prices.get("outcomes"):
        up_price = poly_prices["outcomes"].get("Up", 0)
        down_price = poly_prices["outcomes"].get("Down", 0)
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
                    "subtitle": m.get("subtitle", f"Above ${strike:,.2f}")
                })
        
        # Sort by strike
        kalshi_markets.sort(key=lambda x: x["strike"])
            
    # 4. Map to old format
    poly_data = None
    if poly_prices:
        poly_data = {
            "price_to_beat": price_to_beat,
            "current_price": current_price,
            "prices": poly_prices["outcomes"],
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

