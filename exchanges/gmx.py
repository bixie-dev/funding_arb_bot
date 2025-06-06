from exchanges.base_exchange import BaseExchange
from utils.logger import logger
from config.config_loader import get_config

class Gmx(BaseExchange):
    def __init__(self, api_key=None, api_secret=None):
        config = get_config()
        self.api_key = config['gmx']['private_key']
        self.api_secret = config['gmx']['wallet_address']
        self.positions = {}
        self.balance = 10000
        self.funding_rate = 0.01

    def get_balance(self):
        logger.info(f"[Gmx] Balance: {{self.balance}}")
        return self.balance

    def open_position(self, coin, size, leverage, order_type="limit"):
        logger.info(f"[Gmx] Opening position | Coin: {{coin}}, Size: {{size}}, Leverage: {{leverage}}, Order Type: {{order_type}}")
        position_id = f"{{coin}}_long"
        self.positions[position_id] = {
            "coin": coin,
            "size": size,
            "leverage": leverage,
            "order_type": order_type,
            "entry_price": 100,
            "funding": self.funding_rate * size
        }
        logger.info(f"[Gmx] Position opened: {{self.positions[position_id]}}")
        return position_id

    def close_position(self, position_id):
        if position_id in self.positions:
            logger.info(f"[Gmx] Closing position: {{self.positions[position_id]}}")
            del self.positions[position_id]
            return True
        logger.warning(f"[Gmx] Position not found.")
        return False

    def get_open_positions(self):
        logger.info(f"[Gmx] Open positions: {{self.positions}}")
        return self.positions

    def get_funding_rate(self, coin):
        logger.info(f"[Gmx] Funding rate for {{coin}}: {{self.funding_rate}}")
        return self.funding_rate