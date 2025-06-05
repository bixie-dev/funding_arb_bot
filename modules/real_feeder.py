import requests
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

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
        # Correct v2 subgraph URL
        url = "https://api.thegraph.com/subgraphs/name/gmx-io/gmx-arbitrum"

        # Updated query (tailored to GMX v2 schema)
        query = """
        {
        tokens(first: 10) {
            id
            symbol
            price
        }

        fundingRates(first: 10, orderBy: timestamp, orderDirection: desc) {
            id
            token {
            id
            symbol
            }
            fundingRate
            timestamp
        }
        }
        """

        response = requests.post(url, json={'query': query})
        data = response.json()

        # Parse tokens and map by ID
        tokens = {t['id']: {'symbol': t['symbol'], 'price': float(t['price'])} for t in data['data']['tokens']}

        # Attach funding rates
        for f in data['data']['fundingRates']:
            token_id = f['token']['id']
            if token_id in tokens:
                tokens[token_id]['fundingRate'] = float(f['fundingRate'])

        # Print results
        for t in tokens.values():
            print(f"{t['symbol']}: Price = ${t['price']:.4f}, Funding Rate = {t.get('fundingRate', 'N/A')}")


    except Exception as e:
        print(f"GMX error: {e}")
        return []

def fetch_funding_data():
    funding_data = {}
    funding_data.update(fetch_from_hyperliquid())
    funding_data.update(fetch_from_bybit())  # will overwrite Hyperliquid coins if symbol matches
    funding_data.update(fetch_from_dydx())
    funding_data.update(fetch_from_gmx())
    return funding_data