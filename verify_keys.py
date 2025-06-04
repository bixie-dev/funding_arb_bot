
from exchanges.bybit import BybitExchange
from exchanges.hyperliquid import HyperliquidExchange

def test_bybit():
    print("Testing Bybit API credentials...")
    try:
        client = BybitExchange()
        result = client.get_balance()
        print("✅ Raw response from Bybit get_balance():")
        print(result)
    except Exception as e:
        print("❌ Bybit API key failed:", str(e))

def test_hyperliquid():
    print("Testing Hyperliquid API credentials...")
    try:
        client = HyperliquidExchange()
        result = client.get_balance()
        print("✅ Raw response from Hyperliquid get_balance():")
        print(result)
    except Exception as e:
        print("❌ Hyperliquid API access failed:", str(e))

if __name__ == "__main__":
    test_bybit()
    print()
    test_hyperliquid()
