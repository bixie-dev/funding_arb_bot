
import requests
from config.config_loader import get_config

class HyperliquidExchange:
    def __init__(self):
        config = get_config()
        self.wallet = config['hyperliquid']['wallet']
        self.api_key = config['hyperliquid']['api_key']
        self.base_url = "https://api.hyperliquid.xyz"

    def place_limit_order(self, coin, leverage, size, side):
        return {
            "status": "mock",
            "exchange": "hyperliquid",
            "coin": coin,
            "leverage": leverage,
            "size": size,
            "side": side
        }

    def get_open_positions(self):
        return [{
            "id": "hl123",
            "coin": "ETH",
            "pnl": 40.0,
            "funding": -2.0,
            "spread": 0.03
        }]

    def close_position(self, position_id):
        return {"status": "mock", "position_id": position_id}

    def nuke_positions(self):
        return {"status": "mock", "message": "All closed"}

    def get_balance(self):
        return {"ETH": 1.2}
