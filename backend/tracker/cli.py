"""
Main Entry Point for Crypto Hourly Market Tracker

Uses market_generator and api_clients to monitor for arbitrage opportunities.
"""

import time
import argparse
import json
from datetime import datetime
from typing import List, Dict, Any

from tracker.config import CRYPTO_CONFIGS, DEFAULT_SETTINGS
from tracker.market_generator import MarketURLGenerator
from tracker.api_clients import CombinedMarketFetcher


class CryptoMarketTracker:
    """
    Continuous monitoring service for crypto market arbitrage.
    """
    
    def __init__(self):
        self.generator = MarketURLGenerator()
        self.fetcher = CombinedMarketFetcher()
        self.cryptos = CRYPTO_CONFIGS
    
    def get_current_market_status(self) -> Dict[str, Any]:
        """
        Get info about current and next hour markets for all cryptos.
        """
        return self.generator.get_all_active_markets(self.cryptos, self.fetcher.kalshi)
    
    def scan_for_arbitrage(self, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Perform a single scan across all cryptos for a specific hour.
        
        Args:
            offset: 0=current hour, 1=next hour
        
        Returns:
            List of results with arbitrage data
        """
        results = []
        
        for symbol, crypto in self.cryptos.items():
            # Get identifiers with real discovery
            market_pair = self.generator.get_market_pair(crypto, self.fetcher.kalshi, hours_offset=offset)
            
            # Fetch data using series-based discovery for Kalshi
            data = self.fetcher.fetch_market_pair(
                kalshi_ticker=market_pair["kalshi"]["ticker"],
                polymarket_slug=market_pair["polymarket"]["slug"],
                kalshi_series=market_pair["kalshi"]["series"],
                target_close_time=market_pair["kalshi"]["close_time_utc"]
            )
            
            # Add metadata
            data["symbol"] = symbol
            data["name"] = crypto.name
            data["market_window"] = market_pair["market_window"]
            
            results.append(data)
            
        return results

    def report_status(self, results: List[Dict]):
        """Print a pretty status report to console"""
        print(f"\n{'='*70}")
        print(f"📡 SCAN RESULTS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}")
        
        for res in results:
            symbol = res["symbol"]
            window = res["market_window"]
            print(f"\n🪙 {res['name']} ({symbol}) [{window}]")
            
            if res["kalshi"] and res["polymarket"]:
                k = res["kalshi"]
                p = res["polymarket"]
                print(f"   Kalshi:     YES Ask ${k['yes_ask']:.2f} | NO Ask ${k['no_ask']:.2f}")
                print(f"   Polymarket: UP ${p['up_price']:.2f} | DOWN ${p['down_price']:.2f}")
                
                arb = res["arbitrage"]
                if arb and arb["has_opportunity"]:
                    best = arb["best"]
                    print(f"   💰 ARB: {best['profit_percent']:.1f}% ({best['strategy']})")
                else:
                    print("   🔍 No opportunity")
            else:
                missing = []
                if not res["kalshi"]: missing.append("Kalshi")
                if not res["polymarket"]: missing.append("Polymarket")
                print(f"   ⚠️  Market missing on: {', '.join(missing)}")

    def run_continuous(self, interval: int = None):
        """Run scanning in a loop"""
        interval = interval or DEFAULT_SETTINGS["scan_interval_seconds"]
        
        print(f"🚀 Starting continuous scan every {interval}s...")
        print("Press Ctrl+C to stop.")
        
        try:
            while True:
                # 1. Determine best hour to scan
                # If we're at minute 58, the current market might be closing,
                # so we might want to look at next hour.
                target_offset = 0
                now = datetime.now()
                if now.minute >= 56:
                    print(f"\n🕒 Closing time for current hour. Switching focus to next hour...")
                    target_offset = 1
                
                # 2. Scan
                results = self.scan_for_arbitrage(offset=target_offset)
                
                # 3. Report
                self.report_status(results)
                
                # 4. Wait
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n👋 Stopping tracker...")


def main():
    parser = argparse.ArgumentParser(description="Crypto Hourly Market Tracker")
    parser.add_argument("--list", action="store_true", help="List current market identifiers and URLs")
    parser.add_argument("--once", action="store_true", help="Perform a single scan and exit")
    parser.add_argument("--interval", type=int, help="Scan interval in seconds (default: 60)")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--add", metavar="SYMBOL", help="Show instructions to add a new crypto")
    
    args = parser.parse_args()
    tracker = CryptoMarketTracker()
    
    if args.list:
        status = tracker.get_current_market_status()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print("\n📋 CURRENT MARKET IDENTIFIERS")
            for symbol, markets in status.items():
                print(f"\n🪙 {symbol}")
                for hour, info in markets.items():
                    print(f"  {hour.upper()} ({info['market_window']}):")
                    print(f"    Kalshi: {info['kalshi']['ticker']}")
                    print(f"    Poly:   {info['polymarket']['slug']}")
    
    elif args.add:
        print(f"\n🛠️  HOW TO ADD {args.add}:")
        print("1. Find the Kalshi series ticker (e.g., KXBTCD)")
        print("2. Find the Polymarket slug prefix (e.g., bitcoin-up-or-down)")
        print(f"3. Add a new entry to CRYPTO_CONFIGS in tracker/config.py:")
        print(f"   \"{args.add}\": CryptoConfig(")
        print(f"       name=\"YourName\",")
        print(f"       symbol=\"{args.add}\",")
        print(f"       kalshi_series=\"...\",")
        print(f"       kalshi_market_base=\"...\",")
        print(f"       polymarket_slug_prefix=\"...\"")
        print(f"   )")
        
    elif args.once:
        results = tracker.scan_for_arbitrage()
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            tracker.report_status(results)
            
    else:
        tracker.run_continuous(interval=args.interval)


if __name__ == "__main__":
    main()
