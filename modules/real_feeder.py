
import asyncio
import websockets
import json
import time

class RealFundingFeeder:
    def __init__(self, callback):
        self.callback = callback

    async def start(self):
        await asyncio.gather(
            self._connect_bybit(),
            self._connect_dydx()
        )

    async def _connect_bybit(self):
        url = "wss://stream.bybit.com/v5/public/linear"
        async with websockets.connect(url) as ws:
            sub_msg = {
                "op": "subscribe",
                "args": ["funding.rate.BTCUSDT"]
            }
            await ws.send(json.dumps(sub_msg))

            while True:
                try:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    if 'data' in data:
                        funding = float(data['data']['fundingRate'])
                        update = {
                            "exchange": "bybit",
                            "coin": "BTC",
                            "funding_rate": funding,
                            "spread": 0.02,  # Mock spread
                            "timestamp": time.time()
                        }
                        self.callback(update)
                except Exception as e:
                    print(f"[BYBIT ERROR] {e}")
                    await asyncio.sleep(5)

    async def _connect_dydx(self):
        url = "wss://api.dydx.exchange/v3/ws"
        async with websockets.connect(url) as ws:
            sub_msg = {
                "type": "subscribe",
                "channel": "v3_markets"
            }
            await ws.send(json.dumps(sub_msg))

            while True:
                try:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    if data.get("type") == "channel_data" and "markets" in data["contents"]:
                        eth = data["contents"]["markets"].get("ETH-USD", {})
                        funding = float(eth.get("nextFundingRate", 0))
                        update = {
                            "exchange": "dydx",
                            "coin": "ETH",
                            "funding_rate": funding,
                            "spread": 0.015,
                            "timestamp": time.time()
                        }
                        self.callback(update)
                except Exception as e:
                    print(f"[DYDX ERROR] {e}")
                    await asyncio.sleep(5)
