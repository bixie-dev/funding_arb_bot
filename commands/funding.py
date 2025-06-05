from funding_dashboard.dashboard import fetch_realtime_funding_data

def detect_arbitrage_opportunities(funding_threshold=0.004, price_threshold=2.0):
    data = fetch_realtime_funding_data()
    opportunities = []

    exchanges = list(data.keys())

    for asset1 in data[exchanges[0]]:
        ex1 = exchanges[0]
        coin = asset1['coin']
        price1 = asset1['price']
        funding1 = asset1['funding_rate']
        coin_len = len(coin)
        for asset2 in data[exchanges[1]]:
            if(asset1['coin'] == asset2['coin'][:coin_len]):
                ex2 = exchanges[1]
                price2 = asset2['price']
                funding2 = asset2['funding_rate']
        for asset3 in data[exchanges[2]]:
            if(asset1['coin'] == asset3['coin'][:coin_len]):
                ex3 = exchanges[1]
                price3 = asset3['price']
                funding3 = asset3['funding_rate']
        opportunities.append({
            'coin': coin,
            'ex1': ex1,
            'price1': price1,
            'funding1': funding1,
            'ex2': ex2,
            'price2': price2,
            'funding2': funding2,
            'ex3': ex3,
            'price3': price3,
            'funding3': funding3
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