from funding_dashboard.dashboard import fetch_realtime_funding_data
from exchanges.hyperliquid import Hyperliquid
from exchanges.bybit import Bybit
from exchanges.gmx import Gmx
from exchanges.dydx import Dydx
from exchanges.drift import Drift
from exchanges.derive import Derive
from exchanges.lighter import Lighter
from exchanges.gate import Gate

async def detect_arbitrage_opportunities(funding_threshold=0.004, price_threshold=2.0):
    data = await fetch_realtime_funding_data()
    if not isinstance(data, dict) or not data:
        print("No valid data returned!")
        return []
    exchanges = list(data.keys())
    opportunities = {
        'data': [],
        'balances': []
    }

    ex1 = exchanges[0]
    ex2 = exchanges[1]
    ex3 = exchanges[2]
    ex4 = exchanges[3]
    ex5 = exchanges[4]
    ex6 = exchanges[5]
    ex8 = exchanges[6]
    price1 = 0
    price2 = 0
    price3 = 0
    price4 = 0
    price5 = 0
    price6 = 0
    price8 = 0
    for asset1 in data[ex1]:
        coin = asset1['coin']
        price1 = asset1['price']
        funding1 = asset1['funding_rate']
        coin_len = len(coin)
        sign = 0
        for asset2 in data[ex2]:
            if(coin == asset2['coin'][:coin_len]):
                sign = 1
                if(abs(price1 - price2) >= abs(price1 - asset2['price'])):
                    price2 = asset2['price']
                    funding2 = asset2['funding_rate']
        if(sign == 0):
            price2 = 0
            funding2 = 0
        sign = 0
        for asset3 in data[ex3]:
            if(coin == asset3['coin'][:coin_len]):
                sign = 1
                if(abs(price1 - price3) >= abs(price1 - asset3['price'])):
                    price3 = asset3['price']
                    funding3 = asset3['funding_rate']
        if(sign == 0):
            price3 = 0
            funding3 = 0                
        sign = 0
        for asset4 in data[ex4]:
            if(coin == asset4['coin'][:coin_len]):
                sign = 1
                if(abs(price1 - price4) >= abs(price1 - asset4['price'])):
                    price4 = asset4['price']
                    funding4 = asset4['funding_rate']
        if(sign == 0):
            price4 = 0
            funding4 = 0                
        sign = 0
        for asset5 in data[ex5]:
            if(coin == asset5['coin'][:coin_len]):
                sign = 1
                if(abs(price1 - price5) >= abs(price1 - asset5['price'])):
                    price5 = asset5['price']
                    funding5 = asset5['funding_rate']
        if(sign == 0):
            price5 = 0
            funding5 = 0                
        sign = 0
        for asset8 in data[ex8]:
            if(coin == asset8['coin'][:coin_len]):
                sign = 1
                if(abs(price1 - price8) >= abs(price1 - asset8['price'])):
                    price8 = asset8['price']
                    funding8 = asset8['funding_rate']
        if(sign == 0):
            price8 = 0
            funding8 = 0
        opportunities['data'].append({
            'coin': coin,
            'ex1': ex1,
            'price1': price1,
            'funding1': funding1,
            'ex2': ex2,
            'price2': price2,
            'funding2': funding2,
            'ex3': ex3,
            'price3': price3,
            'funding3': funding3,
            'ex4': ex4,
            'price4': price4,
            'funding4': funding4,
            'ex5': ex5,
            'price5': price5,
            'funding5': funding5,
            'ex8': ex8,
            'price8': price8,
            'funding8': funding8
        })
    for ex in exchanges:
        if ex == "Hyperliquid":
            client = Hyperliquid()
        elif ex == "Bybit":
            client = Bybit()
        elif ex == "GMX":
            client = Gmx()
        elif ex == "Dydx":
            client = Dydx()
        elif ex == "Drift":
            client = Drift()
        elif ex == "Derive":
            client = Derive()
        elif ex == "Lighter":
            client = Lighter()
        elif ex == "Gate.io":
            client = Gate()
        balance = client.get_balance()
        opportunities['balance'].append({
            'ex': ex,
            'balance': balance
        })
    return opportunities

if __name__ == "__main__":
    print("Scanning for arbitrage opportunities...")
    # opps = asyncio.run(detect_arbitrage_opportunities())
    opps = detect_arbitrage_opportunities()
    if opps:
        print(f"Found {len(opps)} opportunity(ies):\n")
        for opp in opps:
            print(f"{opp['exchange_1']} vs {opp['exchange_2']} | "
                  f"Funding Δ: {opp['funding_diff']:.4%} | "
                  f"Price Δ: ${opp['price_diff']:.2f}")
    else:
        print("No profitable opportunities found.")