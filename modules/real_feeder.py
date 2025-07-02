import aiohttp
import requests
from config.config_loader import get_config
from lighter.lighter_client import Client
import ccxt
from ccxt import ExchangeError
import nest_asyncio
import gate_api
from gate_api.exceptions import ApiException, GateApiException
import time
import random
from websocket import create_connection
from exchanges.drift import Drift
import asyncio

nest_asyncio.apply()

# Rate limiting for all exchanges
last_fetch_all_exchanges_time = 0
ALL_EXCHANGES_RATE_LIMIT_SECONDS = 30 # increased seconds between overall fetches to be more conservative

async def fetch_from_hyperliquid():
    try:
        url = "https://api.hyperliquid.xyz/info"
        payload = {"type": "metaAndAssetCtxs"}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                data = await response.json()
        meta = data[0]['universe']
        assets = data[1]
        result = {}
        result['Hyperliquid'] = []
        for i, asset in enumerate(meta):
            coin = asset['name']
            price = float(assets[i]["markPx"]) if assets[i]["markPx"] else 0.0
            funding = float(assets[i]["funding"]) if assets[i]["funding"] else 0.0
            result["Hyperliquid"].append({
                'coin': coin,
                'price': round(price, 4),
                'funding_rate': round(funding, 8)
            })
        return result
    except Exception as e:
        # print(f"Hyperliquid error: {e}")
        return {}

async def fetch_from_bybit():
    try:
        url = f"https://api.bybit.com/v5/market/tickers?category=linear"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                assets = await response.json()
        result = {}
        result['Bybit'] = []
        for coin in assets['result']['list']:
            name = coin['symbol']
            price = float(coin['lastPrice'])
            funding = float(coin['fundingRate']) if coin['fundingRate'] != "" else 0.0
            result['Bybit'].append({
                'coin': name,
                'price': round(price, 4),
                'funding_rate': round(funding, 8)
            })
        return result
    except Exception as e:
        # print(f"Bybit error: {e}")
        return {}

async def fetch_from_dydx():
    try:
        url = "https://indexer.dydx.trade/v4/perpetualMarkets"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={"Accept": "application/json"}) as resp:
                assets = await resp.json()
        result = {}
        result['Dydx'] = []
        for symbol, data in assets['markets'].items():
            coin = symbol
            price = float(data['oraclePrice'])
            funding_rate = float(data['nextFundingRate']) if data['nextFundingRate'] != "" else 0.0
            result['Dydx'].append({
                'coin': coin,
                'price': round(price, 4),
                'funding_rate': round(funding_rate, 8)
            })
        return result
    except Exception as e:
        # print(f"Dydx error: {e}")
        return {}
    
async def fetch_from_gmx():
    try:
        # config = get_config()
        # API_KEY = str(config['gmx']['private_key'])
        # url = "https://gmx-integration-cg.vercel.app/api/arbitrum/pairs"
        # query = """
        # { ... }
        # """
        # headers = {"Content-Type": "application/json"}
        # async with aiohttp.ClientSession() as session:
        #     async with session.post(url, headers=headers, json={'query': query}) as response:
        #         data = await response.json()
        return {}
    except Exception as e:
        # print(f"GMX error: {e}")
        return []

async def fetch_from_drift():
    try:
        url = "https://data.api.drift.trade/contracts"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                contracts = (await resp.json())["contracts"]
        result = {}
        result['Drift'] = []
        for c in contracts:
            name = c["index_name"]
            try:
                oracle_price = float(c["index_price"])
            except (ValueError, TypeError):
                oracle_price = 0
            try:
                funding_long = float(c["funding_rate"])
            except (ValueError, TypeError):
                funding_long = 0
            result["Drift"].append({
                'coin': name,
                'price': round(oracle_price, 4),
                'funding_rate': round(funding_long, 8)
            })
        return result
    except Exception as e:
        # print(f"Drift error: {e}")
        return {}
    
async def fetch_from_lighter():
    try:
        config = get_config()
        api_auth = config['lighter']['api_auth']
        web3_provider_url = "https://rpc.ankr.com/eth_holesky/36b79a7b8bd777b5b5494df71ac1ad07d2d1c68d117764088a58726bb8cd3856"
        
        url = f"{web3_provider_url}/markets"  # Adjust endpoint as needed
        headers = {
            "Authorization": f"Bearer {api_auth}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    result = {'Lighter': []}
                    if isinstance(data, list):
                        for market in data:
                            if isinstance(market, dict):
                                coin = market.get('symbol', market.get('name', 'UNKNOWN'))
                                price = float(market.get('mark_price', market.get('price', 0)))
                                funding_rate = float(market.get('funding_rate', 0))
                                result['Lighter'].append({
                                    'coin': coin,
                                    'price': round(price, 4),
                                    'funding_rate': round(funding_rate, 8)
                                })
                    return result
                else:
                    print(f"Lighter API error: {response.status}")
                    return {}
    except Exception as e:
        print(f"Lighter error: {type(e).__name__}: {e}")
        return {}

async def fetch_from_gateio():
    try:
        configuration = gate_api.Configuration(
            host = "https://api.gateio.ws/api/v4"
        )
        api_client = gate_api.ApiClient(configuration)
        futures_api = gate_api.FuturesApi(api_client)
        # NOTE: gate_api is not async, so this will block. For true async, use an async HTTP client for Gate.io REST API.
        result = {"Gate.io": []}
        tickers = futures_api.list_futures_tickers(settle='usdt')
        for ticker in tickers:
            if hasattr(ticker, 'funding_rate') and hasattr(ticker, 'mark_price'):
                result["Gate.io"].append({
                    'coin': ticker.contract,
                    'price': round(float(ticker.mark_price), 4),
                    'funding_rate': round(float(ticker.funding_rate), 8)
                })
        return result
    except Exception as e:
        # print(f"Gate.io error: {e}")
        return {}

async def fetch_from_derive():
    try:
        BASE_URL = "https://api.lyra.finance"
        url = f"{BASE_URL}/public/get_all_currencies"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
        result = {"Derive": []}
        all_data = data['result']
        funding_rate = get_funding_rate_history()
        for coin in all_data:
            currency = coin.get('currency')
            spot_price = coin.get('spot_price')
            result["Derive"].append({
                'coin': currency,
                'price': round(float(spot_price), 4),
                'funding_rate': round(float(funding_rate), 8)
            })
        return result
    except Exception as e:
        # print(f"Derive error: {e}")
        return {}

def get_funding_rate_history():
    BASE_URL = "https://api.lyra.finance/public/get_funding_rate_history"
    INSTRUMENT = 'ETH-PERP'  # Example: "ETH-PERP", "SOL-PERP", etc.
    now = int(time.time() * 1000)
    one_day_ago = now - (24 * 60 * 60 * 1000)
    payload = {
        "instrument_name": INSTRUMENT,
        "start_timestamp": one_day_ago,
        "end_timestamp": now,
    }
    response = requests.post(BASE_URL, json=payload)
    if response.status_code == 200:
        data = response.json()
        if 'result' in data and 'funding_rate_history' in data['result']:
            result = data['result']['funding_rate_history']
            if result:
                return result[-1]['funding_rate']
            else:
                return 0
        else:
            return 0
    else:
        return 0

async def fetch_funding_data():
    global last_fetch_all_exchanges_time
    current_time = time.time()
    time_since_last_fetch = current_time - last_fetch_all_exchanges_time
    if time_since_last_fetch < ALL_EXCHANGES_RATE_LIMIT_SECONDS:
        sleep_duration = ALL_EXCHANGES_RATE_LIMIT_SECONDS - time_since_last_fetch
        await asyncio.sleep(sleep_duration)
    last_fetch_all_exchanges_time = time.time()
    funding_data = {}
    results = await asyncio.gather(
        fetch_from_hyperliquid(),
        fetch_from_bybit(),
        fetch_from_dydx(),
        # fetch_from_gmx(),
        fetch_from_drift(),
        fetch_from_derive(),
        fetch_from_gateio(),
        fetch_from_lighter()
    )
    for result in results:
        funding_data.update(result)
    exchanges = list(funding_data.keys())
    if len(exchanges) < 7:
        print("Not enough exchanges in data:", exchanges)
        return {}
    if len(funding_data) == 7:
        return funding_data
