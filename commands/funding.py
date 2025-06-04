from funding_dashboard.dashboard import fetch_realtime_funding_data

def detect_arbitrage_opportunities(funding_threshold=0.004, price_threshold=2.0):   
    data = fetch_realtime_funding_data()
    opportunities = []

    exchanges = list(data.keys())
    for i in range(len(exchanges)):
        for j in range(i + 1, len(exchanges)):
            ex1 = exchanges[i]
            ex2 = exchanges[j]
            rate_diff = abs(data[ex1]['funding_rate'] - data[ex2]['funding_rate'])
            price_diff = abs(data[ex1]['price'] - data[ex2]['price'])

            if rate_diff >= funding_threshold or price_diff >= price_threshold:
                opportunities.append({
                    "exchange_1": ex1,
                    "exchange_2": ex2,
                    "funding_rate_1": data[ex1]['funding_rate'],
                    "funding_rate_2": data[ex2]['funding_rate'],
                    "price_1": data[ex1]['price'],
                    "price_2": data[ex2]['price'],
                    "funding_diff": round(rate_diff, 4),
                    "price_diff": round(price_diff, 2)
                })

    # Sort by highest opportunity (combined spread)
    opportunities.sort(key=lambda x: max(x['funding_diff'], x['price_diff']), reverse=True)
    return opportunities

if __name__ == "__main__":
    print("Scanning for arbitrage opportunities...")
    opps = detect_arbitrage_opportunities()
    if opps:
        print(f"Found {len(opps)} opportunity(ies):\n")
        for opp in opps:
            print(f"{opp['exchange_1']} vs {opp['exchange_2']} | "
                  f"Funding Δ: {opp['funding_diff']:.4%} | "
                  f"Price Δ: ${opp['price_diff']:.2f}")
    else:
        print("No profitable opportunities found.")