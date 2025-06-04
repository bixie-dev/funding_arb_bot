
import requests
from exchanges.hyperliquid import HyperliquidExchange
from exchanges.bybit import BybitExchange

def fetch_from_hyperliquid():
    try:
        client = HyperliquidExchange()
        result = client.get_open_positions()
        if(result):
            return {}
        url = "https://api.hyperliquid.xyz/info"
        payload = {"type": "meta"}
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

        funding_info = {}
        for coin_data in data.get("universe", []):
            coin = coin_data.get("name")
            rate = coin_data.get("fundingRateHourly", 0)
            funding_info[coin] = round(float(rate), 6)
        return funding_info
    except Exception as e:
        print(f"Hyperliquid error: {e}")
        return {}

def fetch_from_bybit():
    try:
        client = BybitExchange()
        result = client.get_open_positions()
        if(result):
            return {}
        url = "https://api-testnet.bybit.com/v2/public/tickers"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        funding_info = {}
        for item in data.get("result", []):
            symbol = item.get("symbol", "")
            if "USDT" in symbol:
                funding_info[symbol] = 0.0001  # Placeholder (actual rate needs auth call)
        return funding_info
    except Exception as e:
        print(f"Bybit error: {e}")
        return {}

def fetch_funding_data():
    funding_data = {}
    funding_data.update(fetch_from_hyperliquid())
    funding_data.update(fetch_from_bybit())  # will overwrite Hyperliquid coins if symbol matches
    return funding_data
