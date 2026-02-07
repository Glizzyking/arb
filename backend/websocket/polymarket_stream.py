import asyncio
import json
import logging
import websockets
import requests
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PolymarketStream:
    """Streams live trade data from Polymarket CLOB API for multiple assets"""
    
    def __init__(self):
        self.url = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
        self.prices = {} # {token_id: price}
        self.token_to_outcome = {} # {token_id: (outcome_name, asset_code)}
        self.is_running = False
        self.token_ids = []
        self.current_subscribed_tokens = set()
        self.monitored_slugs = set()
    
    def add_market(self, asset_code: str, slug: str):
        """Fetch token IDs for a given event slug and add to monitoring"""
        if slug in self.monitored_slugs:
            return
            
        try:
            url = f"https://gamma-api.polymarket.com/markets?slug={slug}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                markets = response.json()
                for m in markets:
                    t_ids = json.loads(m.get("clobTokenIds", "[]"))
                    outcomes = json.loads(m.get("outcomes", "[]"))
                    for i, t_id in enumerate(t_ids):
                        if t_id not in self.token_ids:
                            self.token_ids.append(t_id)
                        if i < len(outcomes):
                            self.token_to_outcome[t_id] = (outcomes[i], asset_code)
                
                self.monitored_slugs.add(slug)
                logger.info(f"Added Polymarket market {slug} for {asset_code}")
        except Exception as e:
            logger.error(f"Failed to add Poly market {slug}: {e}")

    async def start(self):
        """Starts the WebSocket stream"""
        self.is_running = True
        
        while self.is_running:
            if not self.token_ids:
                await asyncio.sleep(1)
                continue

            try:
                self.current_subscribed_tokens = set(self.token_ids)
                async with websockets.connect(self.url) as ws:
                    # Subscribe to market channel
                    subscribe_msg = {
                        "type": "subscribe",
                        "assets_ids": list(self.token_ids),
                        "channel": "market"
                    }
                    await ws.send(json.dumps(subscribe_msg))
                    logger.info(f"Subscribed to Poly WS for {len(self.token_ids)} tokens")
                    
                    while self.is_running:
                        # Check if token IDs changed
                        if set(self.token_ids) != self.current_subscribed_tokens:
                            logger.info("Token IDs changed, reconnecting Poly WS...")
                            break 
                            
                        try:
                            # Use timeout to allow checking if token_ids changed
                            message = await asyncio.wait_for(ws.recv(), timeout=1.0)
                            data = json.loads(message)
                            
                            if isinstance(data, dict):
                                # The 'market' channel emits 'book' and 'price_change' events
                                # 'price_change' has 'best_ask' and 'size'
                                if data.get("event_type") == "price_change":
                                    changes = data.get("price_changes", [])
                                    for change in changes:
                                        t_id = change.get("asset_id")
                                        if t_id:
                                            self.prices[t_id] = {
                                                "ask": float(change.get("best_ask", 0)),
                                                "bid": float(change.get("best_bid", 0)),
                                                "size": float(change.get("size", 0))
                                            }
                                # Fallback/Initial for legacy/other events
                                else:
                                    asset_id = data.get("asset_id")
                                    price = data.get("price")
                                    if asset_id and price:
                                        self.prices[asset_id] = {
                                            "ask": float(price),
                                            "bid": float(price),
                                            "size": float(data.get("size", 0))
                                        }
                        except asyncio.TimeoutError:
                            continue
                            
            except Exception as e:
                logger.error(f"Polymarket WebSocket error: {e}")
                if self.is_running:
                    await asyncio.sleep(5)
    
    def get_latest_prices(self, asset_code: str) -> Dict[str, Any]:
        """Map token prices back to outcomes for a specific asset"""
        results = {}
        for t_id, data in self.prices.items():
            outcome_info = self.token_to_outcome.get(t_id)
            if outcome_info and outcome_info[1] == asset_code:
                # return the full data dict {ask, bid, size}
                results[outcome_info[0]] = data
        return results

    def stop(self):
        self.is_running = False

# Singleton
polymarket_stream = PolymarketStream()
