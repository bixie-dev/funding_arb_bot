
import threading
import time
import random

class FundingDataFeeder:
    def __init__(self, callback):
        self.callback = callback
        self.running = False

    def start(self):
        self.running = True
        thread = threading.Thread(target=self._simulate_funding_data)
        thread.daemon = True
        thread.start()

    def _simulate_funding_data(self):
        exchanges = ['bybit', 'dydx', 'gmx', 'hyperliquid']
        coins = ['BTC', 'ETH', 'SOL', 'AVAX']

        while self.running:
            for ex in exchanges:
                data = {
                    'exchange': ex,
                    'coin': random.choice(coins),
                    'funding_rate': round(random.uniform(-0.02, 0.03), 6),
                    'spread': round(random.uniform(0.01, 0.05), 4),
                    'timestamp': time.time()
                }
                self.callback(data)
            time.sleep(3)
