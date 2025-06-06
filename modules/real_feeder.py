import requests
from config.config_loader import get_config

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
        config = get_config()
        API_KEY = str(config['gmx']['private_key'])
        url = f"https://gateway.thegraph.com/api/{API_KEY}/subgraphs/id/2SJf7yp8pNwcc9K6U8YLDNMbwH4TukKbUt8pFqHdL8ug"

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

def fetch_funding_data():
    funding_data = {}
    funding_data.update(fetch_from_hyperliquid())
    funding_data.update(fetch_from_bybit())  # will overwrite Hyperliquid coins if symbol matches
    funding_data.update(fetch_from_dydx())
    return funding_data