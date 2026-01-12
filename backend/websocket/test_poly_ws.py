import asyncio
import json
import websockets

async def test_poly_ws():
    url = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
    # Example token ID for a BTC market (Up/Down)
    # I'll need to get a real one, but let's test connection first
    try:
        async with websockets.connect(url) as ws:
            print("Connected to Poly WS!")
            # Just wait a bit and close
            await asyncio.sleep(2)
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_poly_ws())
