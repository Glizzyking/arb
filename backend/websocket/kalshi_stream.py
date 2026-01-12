import asyncio
import logging
import requests
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KalshiStream:
    """Simulates a stream for Kalshi using aggressive polling (fallback) for multiple assets"""
    
    def __init__(self, interval=1.0):
        self.interval = interval
        self.tickers = {} # {asset_code: ticker}
        self.latest_data = {} # {asset_code: [markets]}
        self.is_running = False
        self.base_url = "https://trading-api.kalshi.com/trade-api/v2/events"
    
    def add_ticker(self, asset_code: str, ticker: str):
        """Add a ticker to monitor for a specific asset"""
        self.tickers[asset_code] = ticker
        logger.info(f"Added Kalshi ticker {ticker} for {asset_code}")

    async def start(self):
        """Starts the aggressive polling loop"""
        self.is_running = True
        while self.is_running:
            try:
                # Poll all active tickers
                for asset_code, ticker in list(self.tickers.items()):
                    url = f"{self.base_url}/{ticker}"
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        # Markets are at root level: {"event": {...}, "markets": [...]}
                        if "markets" in data:
                            self.latest_data[asset_code] = data["markets"]
                            # logger.info(f"Kalshi fetched {len(data['markets'])} markets for {asset_code}")
                
                await asyncio.sleep(self.interval)
            except Exception as e:
                logger.error(f"Kalshi polling error: {e}")
                await asyncio.sleep(5)
    
    def get_latest_markets(self, asset_code: str) -> List[Dict[str, Any]]:
        return self.latest_data.get(asset_code, [])

    def stop(self):
        self.is_running = False

# Singleton
kalshi_stream = KalshiStream()
