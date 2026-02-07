"""
API Clients for Kalshi and Polymarket

Handles fetching market data, orderbook, and prices from both platforms.
"""

import requests
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import time

from tracker.config import (
    KALSHI_API_BASE, 
    POLYMARKET_GAMMA_API, 
    POLYMARKET_CLOB_API, 
    CryptoConfig
)


class KalshiClient:
    """Client for Kalshi's public API (no auth needed for market data)"""
    
    def __init__(self):
        self.base_url = KALSHI_API_BASE
        self.session = requests.Session()
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
        ]
        self._set_random_headers()
        # Discovery cache to avoid constant market querying
        self._discovery_cache = {}
        self._cache_ttl = 300 # 5 minutes

    def _set_random_headers(self):
        import random
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": random.choice(self.user_agents),
            "Referer": "https://kalshi.com/",
            "Origin": "https://kalshi.com"
        })

    def _request_with_retry(self, method, url, **kwargs):
        """Request wrapper with exponential backoff for 429s"""
        import random
        max_retries = 5
        base_delay = 1.0 # seconds
        
        for i in range(max_retries):
            try:
                # Rotate headers on each retry for better evasion
                if i > 0: self._set_random_headers()
                
                response = self.session.request(method, url, **kwargs)
                
                if response.status_code == 429:
                    delay = (base_delay * (2 ** i)) + (random.random() * 0.5)
                    print(f"⚠️ Kalshi 429 Rate Limit. Retrying in {delay:.2f}s... (Attempt {i+1}/{max_retries})")
                    time.sleep(delay)
                    continue
                
                return response
            except Exception as e:
                if i == max_retries - 1: raise e
                time.sleep(base_delay * (2 ** i))
        
        return None
    
    def get_market(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch market data by ticker.
        
        Args:
            ticker: Market ticker like "KXBTCD-26JAN0921-T93500.00"
        
        Returns:
            Market data dict or None if not found
        """
        url = f"{self.base_url}/markets/{ticker}"
        
        try:
            response = self._request_with_retry("GET", url, timeout=10)
            if response and response.status_code == 200:
                return response.json().get("market")
            elif response.status_code == 404:
                return None
            else:
                print(f"Kalshi API error: {response.status_code}")
                return None
        except Exception as e:
            print(f"Kalshi request failed: {e}")
            return None
    
    def get_event(self, event_ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch event data and all associated markets by event ticker.
        
        Args:
            event_ticker: Event ticker like "KXBTCD-26JAN0922" (uppercase)
        
        Returns:
            Dict with 'event' info and 'markets' list, or None if not found
        """
        url = f"{self.base_url}/events/{event_ticker}"
        
        try:
            response = self._request_with_retry("GET", url, timeout=10)
            if response and response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                print(f"Kalshi event API error: {response.status_code}")
                return None
        except Exception as e:
            print(f"Kalshi event request failed: {e}")
            return None
    
    def get_markets_by_series(
        self, 
        series_ticker: str, 
        status: List[str] = ["active", "open", "initialized"]
    ) -> List[Dict[str, Any]]:
        """
        Fetch all markets in a series (e.g., all Bitcoin hourly markets).
        """
        url = f"{self.base_url}/markets"
        params = {
            "series_ticker": series_ticker,
            "limit": 100
        }
        
        try:
            response = self._request_with_retry("GET", url, params=params, timeout=10)
            if response and response.status_code == 200:
                markets = response.json().get("markets", [])
                if status:
                    markets = [m for m in markets if m.get("status") in status]
                return markets
            return []
        except Exception as e:
            print(f"Kalshi series request failed: {e}")
            return []

    def get_markets_by_event(self, event_ticker: str) -> List[Dict[str, Any]]:
        """
        Query /markets with event_ticker (date-only) to discover new hourly pools.
        Includes 5-minute caching.
        """
        now = time.time()
        if event_ticker in self._discovery_cache:
            ts, data = self._discovery_cache[event_ticker]
            if now - ts < self._cache_ttl:
                return data

        url = f"{self.base_url}/markets"
        params = {"event_ticker": event_ticker}
        
        try:
            response = self._request_with_retry("GET", url, params=params, timeout=10)
            if response and response.status_code == 200:
                markets = response.json().get("markets", [])
                self._discovery_cache[event_ticker] = (now, markets)
                return markets
            return []
        except Exception as e:
            print(f"Kalshi discovery request failed for {event_ticker}: {e}")
            return []
    
    def get_orderbook(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch orderbook for a market.
        
        Returns:
            Dict with 'yes' and 'no' arrays of [price, quantity] pairs
        """
        url = f"{self.base_url}/markets/{ticker}/orderbook"
        
        try:
            response = self._request_with_retry("GET", url, timeout=10)
            if response and response.status_code == 200:
                return response.json().get("orderbook")
            return None
        except Exception as e:
            print(f"Kalshi orderbook request failed: {e}")
            return None
    
    def get_best_prices(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Get best bid/ask for YES and NO.
        
        Returns:
            Dict with yes_bid, yes_ask, no_bid, no_ask (in dollars)
        """
        market = self.get_market(ticker)
        if not market:
            return None
        
        return {
            "yes_bid": float(market.get("yes_bid_dollars", "0") or "0"),
            "yes_ask": float(market.get("yes_ask_dollars", "0") or "0"),
            "no_bid": float(market.get("no_bid_dollars", "0") or "0"),
            "no_ask": float(market.get("no_ask_dollars", "0") or "0"),
            "status": market.get("status"),
            "close_time": market.get("close_time"),
            "volume_24h": float(market.get("volume_24h", 0) or 0),
            "ticker": market.get("ticker"),
            "strike": market.get("floor_strike")
        }
    
    def get_markets_for_hour(
        self, 
        series_ticker: str,
        target_close_time: str
    ) -> List[Dict[str, Any]]:
        """
        Get all markets in a series that close at a specific time.
        
        Args:
            series_ticker: Series like "KXBTCD"
            target_close_time: ISO format close time like "2026-01-10T03:00:00Z"
        
        Returns:
            List of markets matching the close time
        """
        all_markets = self.get_markets_by_series(series_ticker)
        
        # Filter by close time
        matching = [
            m for m in all_markets 
            if m.get("close_time", "").startswith(target_close_time[:16])  # Match up to minute
        ]
        
        return matching
    
    def get_best_market_for_hour(
        self,
        series_ticker: str,
        target_close_time: str,
        reference_price: float = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get the best market to trade for a specific hour.
        
        Strategy: If reference_price provided, pick strike closest to it.
                  Otherwise, pick the market with highest volume/liquidity.
        
        Args:
            series_ticker: Series like "KXBTCD"
            target_close_time: ISO close time
            reference_price: Current asset price (e.g., 93500 for BTC)
        
        Returns:
            Best market dict with prices, or None
        """
        markets = self.get_markets_for_hour(series_ticker, target_close_time)
        
        if not markets:
            return None
        
        if reference_price:
            # Pick strike closest to reference price
            markets.sort(key=lambda m: abs(float(m.get("floor_strike", 0) or 0) - reference_price))
            best_market = markets[0]
        else:
            # Pick market with most activity (volume or liquidity)
            markets.sort(key=lambda m: float(m.get("volume_24h", 0) or 0), reverse=True)
            best_market = markets[0] if markets else None
        
        if not best_market:
            return None
        
        return {
            "ticker": best_market.get("ticker"),
            "strike": float(best_market.get("floor_strike", 0) or 0),
            "yes_bid": float(best_market.get("yes_bid_dollars", "0") or "0"),
            "yes_ask": float(best_market.get("yes_ask_dollars", "0") or "0"),
            "no_bid": float(best_market.get("no_bid_dollars", "0") or "0"),
            "no_ask": float(best_market.get("no_ask_dollars", "0") or "0"),
            "status": best_market.get("status"),
            "close_time": best_market.get("close_time"),
            "volume_24h": float(best_market.get("volume_24h", 0) or 0),
            "title": best_market.get("title"),
            "all_strikes_count": len(markets)
        }



class PolymarketClient:
    """Client for Polymarket's Gamma and CLOB APIs"""
    
    def __init__(self):
        self.gamma_url = POLYMARKET_GAMMA_API
        self.clob_url = POLYMARKET_CLOB_API
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "CryptoArbTracker/1.0"
        })
    
    def get_event_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Fetch event data by slug.
        
        Args:
            slug: Event slug like "bitcoin-up-or-down-january-9-8pm-et"
        
        Returns:
            Event data dict or None if not found
        """
        url = f"{self.gamma_url}/events"
        params = {"slug": slug}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                events = response.json()
                if events and len(events) > 0:
                    return events[0]
            return None
        except Exception as e:
            print(f"Polymarket event request failed: {e}")
            return None
    
    def get_markets_by_event_slug(self, slug: str) -> List[Dict[str, Any]]:
        """
        Fetch all markets for an event.
        
        Bitcoin up/down events typically have 2 markets: "Up" and "Down"
        
        Returns:
            List of market dicts with token IDs needed for CLOB
        """
        url = f"{self.gamma_url}/markets"
        params = {"slug": slug}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json() or []
            return []
        except Exception as e:
            print(f"Polymarket markets request failed: {e}")
            return []
    
    def find_ladder_events(self, asset: str) -> List[Dict[str, Any]]:
        """
        Find active ladder events for an asset (e.g. BTC, ETH).
        Search for titles like 'Bitcoin above ___' or 'What will the price of Bitcoin be'.
        """
        # 1. Search for asset name
        url = f"{self.gamma_url}/events"
        params = {"limit": 100, "active": "true", "q": asset}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                events = response.json() or []
                # Filter for ladder-like titles
                ladder_events = []
                for e in events:
                    title = e.get("title", "").lower()
                    slug = e.get("slug", "").lower()
                    # Look for "above", "hit", or "price of"
                    if any(x in title or x in slug for x in ["above", "hit", "price of"]):
                        ladder_events.append(e)
                return ladder_events
            return []
        except Exception as e:
            print(f"Polymarket ladder search failed: {e}")
            return []

    def get_market_matching_strike(self, event_id: str, target_strike: float) -> Optional[Dict[str, Any]]:
        """
        Find a specific market within a ladder event that matches a strike.
        """
        url = f"{self.gamma_url}/markets"
        params = {"event_id": event_id}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                markets = response.json() or []
                for m in markets:
                    question = m.get("question", "")
                    # Extract number from question like "Bitcoin above $95,000?"
                    import re
                    match = re.search(r'\$(\d{1,3}(?:,\d{3})*)', question)
                    if match:
                        strike_val = float(match.group(1).replace(',', ''))
                        if abs(strike_val - target_strike) < 0.1:
                            return m
            return None
        except Exception as e:
            print(f"Polymarket strike match failed: {e}")
            return []
    
    def get_market_prices(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Get current prices and depth for a market by slug using both Gamma and CLOB APIs.
        
        Returns:
        Dict with outcome prices (bid/ask) and real liquidity depth.
        """
        markets = self.get_markets_by_event_slug(slug)
        
        if not markets:
            return None
        
        results = {
            "outcomes": {},
            "total_volume": 0,
            "liquidity": 0,
            "clob_active": False
        }
        
        for market in markets:
            # 1. Basic metrics from Gamma
            results["total_volume"] += float(market.get("volume", 0) or 0)
            results["liquidity"] += float(market.get("liquidity", 0) or 0)
            results["raw_market"] = market
            
            # 2. Extract outcome info
            try:
                outcomes_list = json.loads(market.get("outcomes", "[]")) if isinstance(market.get("outcomes"), str) else market.get("outcomes", [])
                clob_token_ids = json.loads(market.get("clobTokenIds", "[]")) if isinstance(market.get("clobTokenIds"), str) else market.get("clobTokenIds", [])
                
                # Fetch CLOB orderbook for each outcome if available
                for i, (outcome, token_id) in enumerate(zip(outcomes_list, clob_token_ids)):
                    clob_data = self.get_clob_orderbook(token_id)
                    if clob_data:
                        results["clob_active"] = True
                        results["outcomes"][outcome] = {
                            "bid": clob_data.get("bid"),
                            "ask": clob_data.get("ask"),
                            "bid_count": clob_data.get("bid_count"),
                            "ask_count": clob_data.get("ask_count"),
                            "mid": (clob_data.get("bid") + clob_data.get("ask")) / 2 if clob_data.get("bid") and clob_data.get("ask") else None
                        }
                    else:
                        # Fallback to Gamma prices if CLOB fails
                        outcome_prices = market.get("outcomePrices", [])
                        if isinstance(outcome_prices, str):
                            outcome_prices = json.loads(outcome_prices)
                        
                        price = float(outcome_prices[i]) if i < len(outcome_prices) else 0
                        results["outcomes"][outcome] = {
                            "bid": price, # Approximate
                            "ask": price, # Approximate
                            "bid_count": int(results["liquidity"] / (price or 1)) / 10,
                            "ask_count": int(results["liquidity"] / (price or 1)) / 10,
                            "mid": price
                        }
            except Exception as e:
                print(f"Failed to process CLOB/Gamma for market {market.get('id')}: {e}")
        
        return results if results["outcomes"] else None

    def get_clob_orderbook(self, token_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch the top of the book for a specific token from CLOB API.
        """
        if not token_id:
            return None
            
        url = f"{self.clob_url}/book"
        params = {"token_id": token_id}
        
        try:
            response = self.session.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                bids = data.get("bids", [])
                asks = data.get("asks", [])
                
                # CRITICAL: Sort bids descending (highest first), asks ascending (lowest first)
                sorted_bids = sorted(bids, key=lambda x: float(x["price"]), reverse=True)
                sorted_asks = sorted(asks, key=lambda x: float(x["price"]), reverse=False)
                
                # Extract best bid (highest) and best ask (lowest)
                best_bid = float(sorted_bids[0]["price"]) if sorted_bids else None
                bid_qty = float(sorted_bids[0]["size"]) if sorted_bids else 0
                
                best_ask = float(sorted_asks[0]["price"]) if sorted_asks else None
                ask_qty = float(sorted_asks[0]["size"]) if sorted_asks else 0
                
                return {
                    "bid": best_bid,
                    "ask": best_ask,
                    "bid_count": int(bid_qty),
                    "ask_count": int(ask_qty)
                }
            return None
        except Exception as e:
            print(f"Polymarket CLOB book request failed for {token_id}: {e}")
            return None




class CombinedMarketFetcher:
    """
    Combined fetcher that gets data from both platforms for comparison.
    """
    
    def __init__(self):
        self.kalshi = KalshiClient()
        self.polymarket = PolymarketClient()
    
    def fetch_market_pair(
        self, 
        kalshi_ticker: str, 
        polymarket_slug: str,
        kalshi_series: str = None,
        target_close_time: str = None,
        reference_price: float = None
    ) -> Dict[str, Any]:
        """
        Fetch market data from both platforms.
        
        Args:
            kalshi_ticker: Like "kxbtcd-26jan0921" (fallback if series not provided)
            polymarket_slug: Like "bitcoin-up-or-down-january-9-8pm-et"
            kalshi_series: Series ticker like "KXBTCD" (preferred for discovery)
            target_close_time: ISO close time for filtering Kalshi markets
            reference_price: Current asset price for strike selection
        
        Returns:
            Combined market data with arbitrage calculations
        """
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "kalshi": None,
            "polymarket": None,
            "arbitrage": None
        }
        
        # Fetch Kalshi - use event endpoint (kalshi_ticker is now the event ticker)
        kalshi_data = None
        event_data = self.kalshi.get_event(kalshi_ticker)
        
        if event_data and event_data.get("markets"):
            markets = event_data["markets"]
            
            # Select best market (highest liquidity or closest to reference price)
            if reference_price:
                # Pick strike closest to reference price
                markets.sort(key=lambda m: abs(float(m.get("floor_strike", 0) or 0) - reference_price))
                best_market = markets[0]
            else:
                # Pick market with most liquidity
                markets.sort(key=lambda m: float(m.get("liquidity", 0) or 0), reverse=True)
                best_market = markets[0]
            
            kalshi_data = {
                "ticker": best_market.get("ticker"),
                "yes_bid": float(best_market.get("yes_bid_dollars", "0") or "0"),
                "yes_ask": float(best_market.get("yes_ask_dollars", "0") or "0"),
                "no_bid": float(best_market.get("no_bid_dollars", "0") or "0"),
                "no_ask": float(best_market.get("no_ask_dollars", "0") or "0"),
                "yes_ask_count": int(best_market.get("yes_ask_quantity", 0)), # LIQUIDITY DEPTH
                "no_ask_count": int(best_market.get("no_ask_quantity", 0)),   # LIQUIDITY DEPTH
                "status": best_market.get("status"),
                "volume_24h": float(best_market.get("volume_24h", 0) or 0),
                "strike": float(best_market.get("floor_strike", 0) or 0),
                "all_strikes_count": len(markets),
                "event_title": event_data.get("event", {}).get("title", "")
            }
        
        if kalshi_data:
            result["kalshi"] = {
                "ticker": kalshi_data.get("ticker", kalshi_ticker),
                "yes_bid": kalshi_data["yes_bid"],
                "yes_ask": kalshi_data["yes_ask"],
                "no_bid": kalshi_data["no_bid"],
                "no_ask": kalshi_data["no_ask"],
                "yes_count": kalshi_data["yes_ask_count"],
                "no_count": kalshi_data["no_ask_count"],
                "status": kalshi_data.get("status"),
                "volume_24h": kalshi_data.get("volume_24h", 0),
                "strike": kalshi_data.get("strike"),
                "all_strikes_count": kalshi_data.get("all_strikes_count", 1),
                "event_title": kalshi_data.get("event_title", "")
            }
        
        # Fetch Polymarket
        poly_data = self.polymarket.get_market_prices(polymarket_slug)
        if poly_data:
            # Map Up/Down to Yes/No
            up_data = poly_data["outcomes"].get("Up", poly_data["outcomes"].get("Yes", {}))
            down_data = poly_data["outcomes"].get("Down", poly_data["outcomes"].get("No", {}))
            
            # Use real depth if available, fallback to 0
            up_count = up_data.get("ask_count", 0) if isinstance(up_data, dict) else 0
            down_count = down_data.get("ask_count", 0) if isinstance(down_data, dict) else 0
            
            result["polymarket"] = {
                "slug": polymarket_slug,
                "up_price_ask": up_data.get("ask") if isinstance(up_data, dict) else up_data,
                "up_price_bid": up_data.get("bid") if isinstance(up_data, dict) else up_data,
                "down_price_ask": down_data.get("ask") if isinstance(down_data, dict) else down_data,
                "down_price_bid": down_data.get("bid") if isinstance(down_data, dict) else down_data,
                "up_count": int(up_count),
                "down_count": int(down_count),
                "volume": poly_data["total_volume"],
                "liquidity": poly_data["liquidity"],
                "clob_active": poly_data.get("clob_active", False)
            }
        
        # Calculate arbitrage opportunities
        if result["kalshi"] and result["polymarket"]:
            result["arbitrage"] = self._calculate_arbitrage(
                result["kalshi"], 
                result["polymarket"]
            )

        
        return result

    
    def _calculate_arbitrage(
        self, 
        kalshi: Dict, 
        poly: Dict
    ) -> Dict[str, Any]:
        """
        Calculate potential arbitrage between the two platforms.
        
        Arbitrage exists when:
        - Buy YES on one + Buy NO on other < $1.00
        
        Returns:
            Dict with arbitrage opportunities and expected profits
        """
        opportunities = []
        
        # Strategy 1: Buy YES on Kalshi, Buy DOWN (NO) on Polymarket
        poly_down_ask = poly.get("down_price_ask", 0)
        if kalshi["yes_ask"] > 0 and poly_down_ask > 0:
            total_cost = kalshi["yes_ask"] + poly_down_ask
            if total_cost < 1.0:
                profit_pct = ((1.0 - total_cost) / total_cost) * 100
                opportunities.append({
                    "strategy": "Kalshi YES + Polymarket DOWN",
                    "kalshi_side": "YES",
                    "kalshi_price": kalshi["yes_ask"],
                    "poly_side": "DOWN",
                    "poly_price": poly_down_ask,
                    "total_cost": total_cost,
                    "profit_per_dollar": 1.0 - total_cost,
                    "profit_percent": profit_pct
                })
        
        # Strategy 2: Buy NO on Kalshi, Buy UP (YES) on Polymarket
        poly_up_ask = poly.get("up_price_ask", 0)
        if kalshi["no_ask"] > 0 and poly_up_ask > 0:
            total_cost = kalshi["no_ask"] + poly_up_ask
            if total_cost < 1.0:
                profit_pct = ((1.0 - total_cost) / total_cost) * 100
                opportunities.append({
                    "strategy": "Kalshi NO + Polymarket UP",
                    "kalshi_side": "NO",
                    "kalshi_price": kalshi["no_ask"],
                    "poly_side": "UP",
                    "poly_price": poly_up_ask,
                    "total_cost": total_cost,
                    "profit_per_dollar": 1.0 - total_cost,
                    "profit_percent": profit_pct
                })

        
        best_opportunity = max(
            opportunities, 
            key=lambda x: x["profit_percent"],
            default=None
        )
        
        return {
            "has_opportunity": len(opportunities) > 0,
            "opportunities": opportunities,
            "best": best_opportunity
        }


# =============================================================================
# TEST
# =============================================================================
if __name__ == "__main__":
    import os
    import sys
    # Add parent directory to path to allow relative imports
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from tracker.config import CRYPTO_CONFIGS
    from tracker.market_generator import MarketURLGenerator
    
    generator = MarketURLGenerator()
    fetcher = CombinedMarketFetcher()
    
    print("=" * 70)
    print("Testing API Clients")
    print("=" * 70)
    
    for symbol, crypto in CRYPTO_CONFIGS.items():
        print(f"\n🪙 {crypto.name}")
        print("-" * 50)
        
        # Get current hour's market identifiers
        market_info = generator.get_market_pair(crypto, hours_offset=0)
        
        kalshi_ticker = market_info["kalshi"]["ticker"]
        poly_slug = market_info["polymarket"]["slug"]
        
        print(f"Kalshi ticker: {kalshi_ticker}")
        print(f"Polymarket slug: {poly_slug}")
        
        # Fetch combined data
        data = fetcher.fetch_market_pair(kalshi_ticker, poly_slug)
        
        if data["kalshi"]:
            k = data["kalshi"]
            print(f"\n📊 Kalshi: YES bid=${k['yes_bid']:.2f} ask=${k['yes_ask']:.2f}")
        else:
            print("\n❌ Kalshi: Market not found (may not be open yet)")
        
        if data["polymarket"]:
            p = data["polymarket"]
            print(f"📊 Polymarket: UP=${p['up_price']:.2f} DOWN=${p['down_price']:.2f}")
        else:
            print("❌ Polymarket: Market not found")
        
        if data["arbitrage"] and data["arbitrage"]["has_opportunity"]:
            best = data["arbitrage"]["best"]
            print(f"\n💰 ARB OPPORTUNITY: {best['profit_percent']:.2f}%")
            print(f"   Strategy: {best['strategy']}")
            print(f"   Cost: ${best['total_cost']:.2f} → Profit: ${best['profit_per_dollar']:.4f}")
        else:
            print("\n🔍 No arbitrage opportunity at current prices")
