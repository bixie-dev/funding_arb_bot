
import threading
import time
import random

def fetch_funding_data():
    exchanges = ["Bybit", "Hyperliquid", "Dydx", "Drift", "GMX", "Derive", "Lighter", "Gate"]
    coins = ['BTC', 'ETH', 'SOL', 'AVAX']
    data = {}
    for ex in exchanges:
        data[ex] = {
            'coin': random.choice(coins),
            'price': round(1000 + random.uniform(-20, 20), 2),
            'funding_rate': round(random.uniform(-0.02, 0.03), 6),
            'spread': round(random.uniform(0.01, 0.05), 4),
            'timestamp': time.time()
        }
    return data