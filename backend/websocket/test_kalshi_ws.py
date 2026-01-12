import asyncio
import json
import websockets

async def test_kalshi_ws():
    url = "wss://trading-api.kalshi.com/trade-api/v2/ws"
    try:
        async with websockets.connect(url) as ws:
            print("Connected to Kalshi WS!")
            await asyncio.sleep(2)
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_kalshi_ws())
