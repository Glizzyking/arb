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
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "CryptoArbTracker/1.0"
        })
        # Discovery cache to avoid constant market querying
        self._discovery_cache = {}
        self._cache_ttl = 300 # 5 minutes
    
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
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
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
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
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
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
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
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
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
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
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
    
    def search_crypto_events(
        self, 
        crypto_slug_prefix: str, 
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search for all crypto hourly events matching prefix.
        
        Args:
            crypto_slug_prefix: Like "bitcoin-up-or-down"
            active_only: Only return active (not closed) events
        
        Returns:
            List of matching event dicts
        """
        url = f"{self.gamma_url}/events"
        params = {
            "limit": 100,
            "active": "true" if active_only else "false"
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                events = response.json() or []
                # Filter by slug prefix
                return [
                    e for e in events 
                    if e.get("slug", "").startswith(crypto_slug_prefix)
                ]
            return []
        except Exception as e:
            print(f"Polymarket search request failed: {e}")
            return []
    
    def get_market_prices(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Get current prices for a market by slug.
        
        For binary up/down markets, returns Up and Down prices.
        
        Returns:
            Dict with outcome prices and volumes
        """
        markets = self.get_markets_by_event_slug(slug)
        
        if not markets:
            return None
        
        results = {
            "outcomes": {},
            "total_volume": 0,
            "liquidity": 0
        }
        
        for market in markets:
            outcome_prices = market.get("outcomePrices", "")
            
            # Parse outcome prices (stored as JSON string like '["0.52","0.48"]')
            try:
                if outcome_prices:
                    prices = json.loads(outcome_prices) if isinstance(outcome_prices, str) else outcome_prices
                    
                    outcomes = market.get("outcomes", "")
                    if outcomes:
                        outcomes_list = json.loads(outcomes) if isinstance(outcomes, str) else outcomes
                        
                        for i, outcome in enumerate(outcomes_list):
                            if i < len(prices):
                                results["outcomes"][outcome] = float(prices[i])
            except Exception as e:
                print(f"Failed to parse prices for market {market.get('id')}: {e}")
            
            # Aggregate volume/liquidity
            results["total_volume"] += float(market.get("volume", 0) or 0)
            results["liquidity"] += float(market.get("liquidity", 0) or 0)
        
        return results if results["outcomes"] else None


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
            up_price = poly_data["outcomes"].get("Up", poly_data["outcomes"].get("Yes", 0))
            down_price = poly_data["outcomes"].get("Down", poly_data["outcomes"].get("No", 0))
            
            result["polymarket"] = {
                "slug": polymarket_slug,
                "up_price": up_price,  # Equivalent to "Yes" on Kalshi
                "down_price": down_price,  # Equivalent to "No" on Kalshi
                "volume": poly_data["total_volume"],
                "liquidity": poly_data["liquidity"]
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
        if kalshi["yes_ask"] > 0 and poly["down_price"] > 0:
            total_cost = kalshi["yes_ask"] + poly["down_price"]
            if total_cost < 1.0:
                profit_pct = ((1.0 - total_cost) / total_cost) * 100
                opportunities.append({
                    "strategy": "Kalshi YES + Polymarket DOWN",
                    "kalshi_side": "YES",
                    "kalshi_price": kalshi["yes_ask"],
                    "poly_side": "DOWN",
                    "poly_price": poly["down_price"],
                    "total_cost": total_cost,
                    "profit_per_dollar": 1.0 - total_cost,
                    "profit_percent": profit_pct
                })
        
        # Strategy 2: Buy NO on Kalshi, Buy UP (YES) on Polymarket
        if kalshi["no_ask"] > 0 and poly["up_price"] > 0:
            total_cost = kalshi["no_ask"] + poly["up_price"]
            if total_cost < 1.0:
                profit_pct = ((1.0 - total_cost) / total_cost) * 100
                opportunities.append({
                    "strategy": "Kalshi NO + Polymarket UP",
                    "kalshi_side": "NO",
                    "kalshi_price": kalshi["no_ask"],
                    "poly_side": "UP",
                    "poly_price": poly["up_price"],
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
