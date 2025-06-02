import random
import asyncio
import websockets
import json

# Mock fallback data
def fetch_mock_funding_data():
    exchanges = ["Bybit", "Hyperliquid", "Dydx", "Drift", "GMX", "Derive", "Lighter", "Mexc"]
    data = {}
    for ex in exchanges:
        data[ex] = {
            "price": round(1000 + random.uniform(-20, 20), 2),
            "funding_rate": round(random.uniform(-0.01, 0.01), 4)
        }
    return data

# Real-time funding data using Hyperliquid WebSocket
async def fetch_realtime_funding_data():
    url = "wss://api.hyperliquid.xyz/ws"  # Replace with actual endpoint if needed
    funding_data = fetch_mock_funding_data()  # Default to mock data

    try:
        async with websockets.connect(url) as websocket:
            subscribe_message = {
                "type": "subscribe",
                "channels": [{"name": "funding"}]
            }
            await websocket.send(json.dumps(subscribe_message))

            while True:
                msg = await websocket.recv()
                parsed = json.loads(msg)
                if parsed.get("channel") == "funding":
                    for item in parsed.get("data", []):
                        coin = item.get("coin", "Unknown")
                        funding = float(item.get("fundingRate", 0.0))
                        price = float(item.get("markPrice", 1000.0))
                        funding_data["Hyperliquid"] = {
                            "price": price,
                            "funding_rate": funding
                        }
                        break  # Only fetch first entry for simplicity
                return funding_data
    except Exception as e:
        print(f"[WebSocket Error] {e}")
        return funding_data