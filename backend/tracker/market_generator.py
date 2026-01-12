"""
Market URL and Ticker Generator for Hourly Crypto Markets

This module handles the tricky part: generating the correct market identifiers
for both Kalshi and Polymarket based on the current time.

KEY INSIGHT:
- Kalshi uses 24-hour format: kxbtcd-26jan0921 (year + monthday + hour24)
- Polymarket uses 12-hour format with month name: bitcoin-up-or-down-january-9-8pm-et

Both platforms run hourly markets that close at the top of the hour.
"""

from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict, Any
import pytz

from tracker.config import CryptoConfig, DEFAULT_SETTINGS


class MarketURLGenerator:
    """
    Generates correct market URLs/tickers for Kalshi and Polymarket
    based on target hour.
    """
    
    def __init__(self, timezone: str = None):
        self.tz = pytz.timezone(timezone or DEFAULT_SETTINGS["timezone"])
        
        # Month name mappings
        self.month_abbr = {
            1: "jan", 2: "feb", 3: "mar", 4: "apr",
            5: "may", 6: "jun", 7: "jul", 8: "aug",
            9: "sep", 10: "oct", 11: "nov", 12: "dec"
        }
        self.month_full = {
            1: "january", 2: "february", 3: "march", 4: "april",
            5: "may", 6: "june", 7: "july", 8: "august",
            9: "september", 10: "october", 11: "november", 12: "december"
        }
    
    def get_current_time(self) -> datetime:
        """Get current time in configured timezone"""
        return datetime.now(self.tz)
    
    def get_target_hours(self, current_hour_offset: int = 0) -> Dict[str, datetime]:
        """
        Get target market hours.
        
        Args:
            current_hour_offset: 0 = current hour's market (if still open)
                                 1 = next hour's market
                                 -1 = previous hour's market
        
        Returns:
            Dict with 'start' and 'end' datetimes for the market window
        """
        now = self.get_current_time()
        
        # Round to the start of current hour
        current_hour_start = now.replace(minute=0, second=0, microsecond=0)
        
        # Apply offset
        target_start = current_hour_start + timedelta(hours=current_hour_offset)
        target_end = target_start + timedelta(hours=1)
        
        return {
            "start": target_start,
            "end": target_end,
            "display_hour": target_start.hour
        }
    
    def get_next_tradeable_market(self) -> Dict[str, datetime]:
        """
        Get the next market that can still be traded.
        
        Logic: If we're past minute 55 of current hour, target next hour
               (most markets stop accepting bets ~5 min before close)
        """
        now = self.get_current_time()
        
        # If past minute 55, target next hour
        if now.minute >= 55:
            return self.get_target_hours(current_hour_offset=1)
        else:
            return self.get_target_hours(current_hour_offset=0)
    
    # =========================================================================
    # KALSHI TICKER GENERATION
    # =========================================================================
    
    def generate_event_ticker(self, crypto: CryptoConfig, target_time: datetime) -> str:
        """
        Generate Kalshi date-only event ticker for discovery.
        Format: {SERIES}-{YY}{MON}{DD}
        Example: KXBTCD-26JAN09
        """
        year_short = target_time.strftime("%y")
        month = self.month_abbr[target_time.month].upper()
        day = f"{target_time.day:02d}"
        return f"{crypto.kalshi_series}-{year_short}{month}{day}"

    def generate_kalshi_ticker(self, crypto: CryptoConfig, target_time: datetime) -> str:
        """
        [DEPRECATED] Use the ticker returned by discovery API instead.
        """
        year_short = target_time.strftime("%y")
        month = self.month_abbr[target_time.month].upper()
        day = f"{target_time.day:02d}"
        hour = f"{target_time.hour:02d}"
        return f"{crypto.kalshi_series}-{year_short}{month}{day}{hour}"
    
    def generate_kalshi_url(self, crypto: CryptoConfig, real_ticker: str) -> str:
        """
        Generate Kalshi market URL using the REAL ticker from discovery.
        """
        slug_map = {
            "BTC": "bitcoin-price-abovebelow",
            "ETH": "ethereum-price-abovebelow",
            "XRP": "xrp-price-abovebelow",
            "SOL": "solana-price-abovebelow",
        }
        slug = slug_map.get(crypto.symbol, f"{crypto.name.lower()}-price-abovebelow")
        return f"https://kalshi.com/markets/{crypto.kalshi_market_base}/{slug}/{real_ticker.lower()}"
    
    # =========================================================================
    # POLYMARKET SLUG GENERATION
    # =========================================================================
    
    def generate_polymarket_slug(self, crypto: CryptoConfig, target_time: datetime) -> str:
        """
        Generate Polymarket event slug for a specific hour.
        
        Format: {prefix}-{month-name}-{day}-{hour}pm-et  (or am)
        Example: bitcoin-up-or-down-january-9-8pm-et
        
        Note: Polymarket uses 12-hour format with am/pm
        
        Args:
            crypto: CryptoConfig for the cryptocurrency
            target_time: The hour to generate slug for
        
        Returns:
            Polymarket slug string like "bitcoin-up-or-down-january-9-8pm-et"
        """
        month = self.month_full[target_time.month]  # "january"
        day = target_time.day  # 9 (no leading zero)
        
        # Convert to 12-hour format
        hour_24 = target_time.hour
        if hour_24 == 0:
            hour_12 = 12
            period = "am"
        elif hour_24 < 12:
            hour_12 = hour_24
            period = "am"
        elif hour_24 == 12:
            hour_12 = 12
            period = "pm"
        else:
            hour_12 = hour_24 - 12
            period = "pm"
        
        return f"{crypto.polymarket_slug_prefix}-{month}-{day}-{hour_12}{period}-et"
    
    def generate_polymarket_url(self, crypto: CryptoConfig, target_time: datetime) -> str:
        """
        Generate full Polymarket event URL.
        
        Example: https://polymarket.com/event/bitcoin-up-or-down-january-9-8pm-et
        """
        slug = self.generate_polymarket_slug(crypto, target_time)
        return f"https://polymarket.com/event/{slug}"
    
    # =========================================================================
    # COMBINED HELPERS
    # =========================================================================
    
    def get_market_pair(
        self, 
        crypto: CryptoConfig, 
        kalshi_client: Any,  # KalshiClient instance for discovery
        hours_offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get both Kalshi and Polymarket market info for a crypto at target hour.
        Uses real Kalshi discovery.
        
        IMPORTANT: The offsets work differently for each platform:
        - Kalshi: Named by CLOSE time. hours_offset=1 means "market closing next hour"
        - Polymarket: Named by OPEN time. The same market that closes next hour
                      opened THIS hour, so we use hours_offset=0 for the same window.
        
        When hours_offset=1 is passed (target next hour's close):
        - Kalshi gets offset=1 (4pm close at 3:30pm)
        - Polymarket gets offset=0 (3pm open = same market, closes 4pm)
        """
        # Kalshi uses the provided offset (close time based)
        kalshi_target = self.get_target_hours(hours_offset)
        kalshi_target_time = kalshi_target["start"]
        close_time = kalshi_target["end"]
        
        # Polymarket uses offset-1 because it's named by OPEN time
        # When hours_offset=1 (next hour close), Poly needs offset=0 (current hour open)
        poly_offset = hours_offset - 1 if hours_offset > 0 else 0
        poly_target = self.get_target_hours(poly_offset)
        poly_target_time = poly_target["start"]
        
        # 1. Discover Real Kalshi Ticker
        event_ticker = self.generate_event_ticker(crypto, kalshi_target_time)
        markets = kalshi_client.get_markets_by_event(event_ticker)
        
        real_ticker = None
        close_time_iso = close_time.astimezone(pytz.UTC).strftime("%Y-%m-%dT%H:00:00Z")
        
        for m in markets:
            if m.get("close_time") == close_time_iso:
                real_ticker = m["ticker"]
                break
        
        # Fallback to generated if API fails (as a safety measure)
        if not real_ticker:
            real_ticker = self.generate_kalshi_ticker(crypto, kalshi_target_time)

        close_time_utc = close_time.astimezone(pytz.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        return {
            "crypto": crypto.symbol,
            "target_hour": kalshi_target_time.strftime("%Y-%m-%d %H:00 %Z"),
            "market_window": f"{poly_target_time.strftime('%I%p').lstrip('0')} - {close_time.strftime('%I%p').lstrip('0')} ET",
            "kalshi": {
                "ticker": real_ticker,
                "url": self.generate_kalshi_url(crypto, real_ticker),
                "series": crypto.kalshi_series,
                "close_time_utc": close_time_utc
            },
            "polymarket": {
                "slug": self.generate_polymarket_slug(crypto, poly_target_time),
                "url": self.generate_polymarket_url(crypto, poly_target_time)
            }
        }

    def get_all_active_markets(
        self, 
        cryptos: Dict[str, CryptoConfig],
        kalshi_client: Any,
        include_current: bool = True,
        include_next: bool = True
    ) -> Dict[str, Dict]:
        """
        Get market info for all configured cryptocurrencies.
        """
        results = {}
        for symbol, crypto in cryptos.items():
            results[symbol] = {}
            if include_current:
                results[symbol]["current"] = self.get_market_pair(crypto, kalshi_client, hours_offset=0)
            if include_next:
                results[symbol]["next"] = self.get_market_pair(crypto, kalshi_client, hours_offset=1)
        return results


# =============================================================================
# QUICK TEST
# =============================================================================
if __name__ == "__main__":
    import os
    import sys
    # Add parent directory to path to allow relative imports
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from tracker.config import CRYPTO_CONFIGS
    
    generator = MarketURLGenerator()
    
    print("=" * 70)
    print(f"Current Time: {generator.get_current_time().strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print("=" * 70)
    
    for symbol, crypto in CRYPTO_CONFIGS.items():
        print(f"\n🪙 {crypto.name} ({symbol})")
        print("-" * 50)
        
        # Current hour market
        current = generator.get_market_pair(crypto, hours_offset=0)
        print(f"\n📍 CURRENT HOUR: {current['market_window']}")
        print(f"   Kalshi:     {current['kalshi']['ticker']}")
        print(f"   Kalshi URL: {current['kalshi']['url']}")
        print(f"   Poly Slug:  {current['polymarket']['slug']}")
        print(f"   Poly URL:   {current['polymarket']['url']}")
        
        # Next hour market  
        next_hr = generator.get_market_pair(crypto, hours_offset=1)
        print(f"\n⏭️  NEXT HOUR: {next_hr['market_window']}")
        print(f"   Kalshi:     {next_hr['kalshi']['ticker']}")
        print(f"   Kalshi URL: {next_hr['kalshi']['url']}")
        print(f"   Poly Slug:  {next_hr['polymarket']['slug']}")
        print(f"   Poly URL:   {next_hr['polymarket']['url']}")
