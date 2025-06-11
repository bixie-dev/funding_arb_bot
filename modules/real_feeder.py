import requests
import asyncio
from config.config_loader import get_config
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from driftpy.drift_client import DriftClient
from driftpy.constants.config import configs
from lighter.lighter_client import Client
from lighter.modules.blockchain import Api as BlockchainApi
import nest_asyncio
import gate_api
from gate_api.exceptions import ApiException, GateApiException
import time

nest_asyncio.apply()

# Rate limiting for all exchanges
last_fetch_all_exchanges_time = 0
ALL_EXCHANGES_RATE_LIMIT_SECONDS = 30 # increased seconds between overall fetches to be more conservative

def fetch_from_hyperliquid():
    try:
        url = "https://api.hyperliquid.xyz/info"
        payload = {"type": "metaAndAssetCtxs"}
        response = requests.post(url, json=payload)
        data = response.json()
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
                'price': price,
                'funding_rate': funding
            })
        return result
    except Exception as e:
        print(f"Hyperliquid error: {e}")
        return {}

def fetch_from_bybit():
    try:
        url = f"https://api.bybit.com/v5/market/tickers?category=linear"
        response = requests.get(url)
        assets = response.json()
        result = {}
        result['Bybit'] = []
        for coin in assets['result']['list']:
            name = coin['symbol']
            price = coin['lastPrice']
            if(coin['fundingRate'] == ""):
                funding = 0
            else: 
                funding = coin['fundingRate']
            result['Bybit'].append({
                'coin': name,
                'price': price,
                'funding_rate': funding
            })
        
        return result
    except Exception as e:
        print(f"Bybit error: {e}")
        return {}

def fetch_from_dydx():
    try:
        url = "https://api.dydx.exchange/v3/markets"
        response = requests.get(url)
        assets = response.json()
        result = {}
        result['Dydx'] = []
        for symbol, data in assets['markets'].items():
            coin = symbol
            price = data['indexPrice']
            funding_rate = data['nextFundingRate']
            result['Dydx'].append({
                'coin': coin,
                'price': price,
                'funding_rate': funding_rate
            })
        return result
    except Exception as e:
        print(f"Dydx error: {e}")
        return {}
    
def fetch_from_gmx():
    try:
        # config = get_config()
        # API_KEY = str(config['gmx']['private_key'])
        url = "https://gmx-integration-cg.vercel.app/api/arbitrum/pairs"

        query = """
        {
            tokens(first: 10) {
                id
                symbol
                price
            }

            fundingRates(first: 10, orderDirection: desc) {
                token {
                id
                symbol
                }
                fundingRate
            }
        }
        """
        
        headers = {
           "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, json={'query': query})
        data = response.json()
        print(data, '----------------------')
        return {}

    except Exception as e:
        print(f"GMX error: {e}")
        return []

def fetch_from_drift():
    try:
        url = "https://api.drift.trade/markets"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        result = {}
        result['Drift'] = []
        
        for market in data['markets']:
            if market['marketType'] == 'PERP':  # Only process perpetual markets
                result['Drift'].append({
                    'coin': market['name'],
                    'price': float(market['oraclePrice']),
                    'funding_rate': float(market['fundingRate'])
                })
        print(result, '----------------')
        return result
    except Exception as e:
        print(f"Drift error: {e}")
        return {}
    
def fetch_from_lighter():
    try:
        config = get_config()
        api_auth = config['lighter']['api_auth']
        web3_provider_url = config['lighter']['web3_provider_url']
        
        # Initialize Lighter client
        client = Client(api_auth=api_auth, web3_provider_url=web3_provider_url)
        
        # Get all perpetual markets
        markets = client.get_markets()
        print(markets, '----------------')
        result = {}
        result['Lighter'] = []
        
        for market in markets:
            if market.type == 'perpetual':  # Only process perpetual markets
                result['Lighter'].append({
                    'coin': market.symbol,
                    'price': float(market.mark_price),
                    'funding_rate': float(market.funding_rate)
                })
        
        return result
    except Exception as e:
        print(f"Lighter error: {type(e).__name__}: {e}")
        return {}

def fetch_from_gateio():
    try:
        configuration = gate_api.Configuration(
            host = "https://api.gateio.ws/api/v4"
        )
        api_client = gate_api.ApiClient(configuration)
        futures_api = gate_api.FuturesApi(api_client)

        # Fetch all futures tickers, which include funding rates and mark prices
        result = {"Gate.io": []}
        tickers = futures_api.list_futures_tickers(settle='usdt')

        for ticker in tickers:
            if hasattr(ticker, 'funding_rate') and hasattr(ticker, 'mark_price'):
                result["Gate.io"].append({
                    'coin': ticker.contract,
                    'price': float(ticker.mark_price),
                    'funding_rate': float(ticker.funding_rate)
                })
        return result
    except GateApiException as ex:
        print(f"Gate.io API Exception: {ex.label}: {ex.message}. Status: {ex.status}, Headers: {ex.headers}")
        return {}
    except ApiException as e:
        print(f"Gate.io General API Exception: {e}")
        return {}
    except Exception as e:
        print(f"Gate.io error: {e}")
        return {}

def fetch_funding_data():
    global last_fetch_all_exchanges_time
    current_time = time.time()
    time_since_last_fetch = current_time - last_fetch_all_exchanges_time

    if time_since_last_fetch < ALL_EXCHANGES_RATE_LIMIT_SECONDS:
        sleep_duration = ALL_EXCHANGES_RATE_LIMIT_SECONDS - time_since_last_fetch
        time.sleep(sleep_duration)

    last_fetch_all_exchanges_time = time.time()

    funding_data = {}
    funding_data.update(fetch_from_hyperliquid())
    funding_data.update(fetch_from_bybit())  # will overwrite Hyperliquid coins if symbol matches
    funding_data.update(fetch_from_dydx())
    funding_data.update(fetch_from_drift())
    # funding_data.update(fetch_from_lighter())
    funding_data.update(fetch_from_gateio())
    # drift_data = asyncio.run(fetch_from_drift())
    # funding_data.update(drift_data)
    return funding_data