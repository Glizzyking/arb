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
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        
        # Cache to avoid repeated fetches within the same hour
        self._cache: Dict[str, PriceResult] = {}
        self._last_hour = -1
        
        # Asset to Binance.US symbol mapping
        self.binance_symbols = {
            "BTC": "BTCUSD",
            "ETH": "ETHUSD",
            "XRP": "XRPUSD",
            "SOL": "SOLUSD",
        }
    
    def get_price_to_beat(self, asset: str, market_slug: Optional[str] = None) -> PriceResult:
        """
        Get the "Price to Beat" for an asset.
        
        Args:
            asset: Asset code (BTC, ETH, XRP, SOL)
            market_slug: Optional Polymarket slug (reserved for future scraping)
            
        Returns:
            PriceResult with price, source, and metadata
        """
        current_hour = datetime.datetime.now().hour
        
        # Clear cache if hour changed
        if current_hour != self._last_hour:
            self._cache.clear()
            self._last_hour = current_hour
        
        # Return cached if available
        if asset in self._cache:
            return self._cache[asset]
        
        # NOTE: Polymarket renders "Price to Beat" via client-side JavaScript
        # Static HTML scraping doesn't reliably find it, so we use Binance.US directly
        # This is actually the same source Polymarket uses for resolution anyway.
        
        # Primary source: Binance.US
        price = self._fetch_binance_us(asset)
        source = "binance_us"
        
        if price <= 0:
            logger.warning(f"[{asset}] Failed to get price from Binance.US")
        
        result = PriceResult(
            price=price,
            source=source,
            asset=asset,
            timestamp=datetime.datetime.now()
        )
        
        logger.info(f"[{asset}] Price to Beat from {source}: ${price:,.2f}")
        
        self._cache[asset] = result
        return result
    
    def _fetch_binance_us(self, asset: str) -> float:
        """
        Fetch the current hour's open price from Binance.US
        
        This is the reliable source since Binance.US (specifically BTC/USDT) is the
        resolution source for Polymarket hourly markets.
        """
        symbol = self.binance_symbols.get(asset, "BTCUSD")
        
        try:
            url = "https://api.binance.us/api/v3/klines"
            params = {
                "symbol": symbol,
                "interval": "1h",
                "limit": 1
            }
            
            response = self.session.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    # Kline format: [open_time, open, high, low, close, ...]
                    return float(data[0][1])
                    
        except Exception as e:
            logger.error(f"Binance.US API error for {asset}: {e}")
        
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
