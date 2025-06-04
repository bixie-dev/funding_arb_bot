from exchanges.base_exchange import BaseExchange
from utils.logger import logger
from config.config_loader import get_config

class Drift(BaseExchange):
    def __init__(self):
        config = get_config()
        self.api_key = config['hyperliquid']['api_key']
        self.api_secret = config['hyperliquid']['api_secret']
        self.positions = {{}}
        self.balance = 10000
        self.funding_rate = 0.01

    def get_balance(self):
        logger.info(f"[Drift] Balance: {{self.balance}}")
        return self.balance

    def open_position(self, coin, size, leverage, order_type="limit"):
        logger.info(f"[Drift] Opening position | Coin: {{coin}}, Size: {{size}}, Leverage: {{leverage}}, Order Type: {{order_type}}")
        position_id = f"{{coin}}_long"
        self.positions[position_id] = {{
            "coin": coin,
            "size": size,
            "leverage": leverage,
            "order_type": order_type,
            "entry_price": 100,
            "funding": self.funding_rate * size
        }}
        logger.info(f"[Drift] Position opened: {{self.positions[position_id]}}")
        return position_id

    def close_position(self, position_id):
        if position_id in self.positions:
            logger.info(f"[Drift] Closing position: {{self.positions[position_id]}}")
            del self.positions[position_id]
            return True
        logger.warning(f"[Drift] Position not found.")
        return False

    def get_open_positions(self):
        logger.info(f"[Drift] Open positions: {{self.positions}}")
        return self.positions

    def get_funding_rate(self, coin):
        logger.info(f"[Drift] Funding rate for {{coin}}: {{self.funding_rate}}")
        return self.funding_rate