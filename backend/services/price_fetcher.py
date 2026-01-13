"""
Price Fetcher Module - Binance.US Open Price with Polymarket Scraping (Future)

This module fetches the "Price to Beat" (opening price) for crypto markets.
It operates independently from the main data streaming system.

Current: Uses Binance.US API for the hourly open price
Future: Will attempt to scrape Polymarket's website first, with Binance.US fallback
"""

import requests
import re
import logging
import datetime
from typing import Dict, Optional
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PriceResult:
    """Result from price fetch attempt"""
    price: float
    source: str  # "polymarket" or "binance_us"
    asset: str
    timestamp: datetime.datetime


class PriceFetcher:
    """
    Fetches the "Price to Beat" for crypto assets.
    
    This is a separate service that doesn't interfere with real-time data streaming.
    Currently uses Binance.US as the primary source (this is what Polymarket uses for resolution).
    
    TODO: Add Playwright-based Polymarket scraping when needed.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Origin": "https://polymarket.com",
            "Referer": "https://polymarket.com/"
        })
        
        # Cache to avoid repeated fetches within the same hour
        self._cache: Dict[str, PriceResult] = {}
        self._last_hour = -1
        
        # Asset to Binance International symbol mapping (USDT pairs match Polymarket resolution)
        self.binance_symbols = {
            "BTC": "BTCUSDT",
            "ETH": "ETHUSDT",
            "XRP": "XRPUSDT",
            "SOL": "SOLUSDT",
        }
    
    def get_price_to_beat(self, asset: str, market_slug: Optional[str] = None) -> PriceResult:
        """
        Get the "Price to Beat" for an asset with multi-source fallback.
        
        Order of attempt:
        1. Polymarket Data API (Internal)
        2. Binance International API (Resolution Source)
        3. CryptoCompare API (Reliable Fallback)
        """
        current_hour_dt = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
        current_hour = current_hour_dt.hour
        timestamp = int(current_hour_dt.timestamp())
        
        # Clear cache if hour changed
        if current_hour != self._last_hour:
            self._cache.clear()
            self._last_hour = current_hour
        
        # Return cached if available
        if asset in self._cache:
            return self._cache[asset]
        
        price = 0.0
        source = "unknown"
        
        # 1. Try Polymarket Data API (As requested by user)
        price = self._fetch_polymarket_data_api(asset, timestamp)
        if price > 0:
            source = "polymarket_data_api"
        else:
            # 2. Try Binance International (Official Resolution Source)
            price = self._fetch_binance_intl(asset)
            if price > 0:
                source = "binance_intl"
            else:
                # 3. Try CryptoCompare (Mirror of Binance, works in restricted regions)
                price = self._fetch_cryptocompare(asset)
                if price > 0:
                    source = "cryptocompare_binance"
        
        if price <= 0:
            logger.error(f"[{asset}] FAILED to fetch Price to Beat from ALL sources")
        
        result = PriceResult(
            price=price,
            source=source,
            asset=asset,
            timestamp=datetime.datetime.now()
        )
        
        logger.info(f"[{asset}] Price to Beat from {source}: ${price:,.2f}")
        
        self._cache[asset] = result
        return result
    
    def _fetch_polymarket_data_api(self, asset: str, timestamp: int) -> float:
        """Fetch price directly from Polymarket's internal data API"""
        symbol = self.binance_symbols.get(asset, "BTCUSDT")
        try:
            # Note: This is an internal API discovered via web scraping
            url = f"https://data-api.polymarket.com/price?symbol={symbol}&timestamp={timestamp}"
            response = self.session.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                # Assuming the format is a float or a dict with price
                if isinstance(data, (int, float)):
                    return float(data)
                elif isinstance(data, dict) and "price" in data:
                    return float(data["price"])
        except Exception as e:
            logger.debug(f"Polymarket Data API unavailable: {e}")
        return 0.0

    def _fetch_binance_intl(self, asset: str) -> float:
        """Fetch the current hour's open price from Binance International"""
        symbol = self.binance_symbols.get(asset, "BTCUSDT")
        try:
            url = "https://api.binance.com/api/v3/klines"
            params = {"symbol": symbol, "interval": "1h", "limit": 1}
            response = self.session.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    return float(data[0][1]) # Open price
        except Exception as e:
            logger.debug(f"Binance International API error: {e}")
        return 0.0

    def _fetch_cryptocompare(self, asset: str) -> float:
        """Fetch Binance-specific price from CryptoCompare (fallback)"""
        try:
            # Maps BTC to BTCUSDT on Binance
            symbol = "BTC" if asset == "BTC" else asset
            # Use USDT as target symbol to match Binance International trading pairs
            url = f"https://min-api.cryptocompare.com/data/v2/histohour?fsym={symbol}&tsym=USDT&limit=1&e=Binance"
            response = self.session.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("Response") == "Success":
                    points = data.get("Data", {}).get("Data", [])
                    if points:
                        # Return the open price of the current hour (last entry)
                        return float(points[-1].get("open", 0))
        except Exception as e:
            logger.debug(f"CryptoCompare fallback error: {e}")
        return 0.0
    
    def refresh_all(self) -> Dict[str, PriceResult]:
        """
        Refresh prices for all configured assets.
        
        Returns:
            Dictionary of asset -> PriceResult
        """
        results = {}
        for asset in self.binance_symbols.keys():
            results[asset] = self.get_price_to_beat(asset)
        return results


# Singleton instance for use across the application
price_fetcher = PriceFetcher()


# =============================================================================
# TEST
# =============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("Testing Price Fetcher Module")
    print("=" * 60)
    
    fetcher = PriceFetcher()
    
    for asset in ["BTC", "ETH", "XRP", "SOL"]:
        print(f"\n📊 {asset}:")
        result = fetcher.get_price_to_beat(asset)
        print(f"   Price: ${result.price:,.2f}")
        print(f"   Source: {result.source}")
        print(f"   Time: {result.timestamp}")
