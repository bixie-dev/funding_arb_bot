import requests
from exchanges.base_exchange import BaseExchange
from utils.logger import logger
from config.config_loader import get_config
import time

class Dydx(BaseExchange):
    def __init__(self):
        config = get_config()
        self.base_url = "https://indexer.dydx.trade/v4"
        self.wallet_address = config['dydx']['wallet']
        self.session = requests.Session()
        # Add authentication headers if required

    def _get(self, endpoint, params=None):
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
        }
        response = self.session.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    def _post(self, endpoint, data):
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
        }
        response = self.session.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_balance(self):
        try:
            resp = self._get(f"/accounts/{self.wallet_address}")
            balance = float(resp['account']['equity'])
            logger.info(f"[dYdX] Balance: {balance}")
            return balance
        except Exception as e:
            logger.error(f"[dYdX] Error getting balance: {str(e)}")
            return None

    def get_open_positions(self):
        try:
            resp = self._get(f"/positions/{self.wallet_address}")
            positions = resp['positions']
            result = {}
            for pos in positions:
                result[pos['market']] = {
                    'size': float(pos['size']),
                    'leverage': float(pos['leverage']),
                    'entry_price': float(pos['entryPrice']),
                    'mark_price': float(pos['markPrice']),
                    'unrealized_pnl': float(pos['unrealizedPnl']),
                    'position_value': float(pos['positionValue']),
                    'side': 'BUY' if float(pos['size']) > 0 else 'SELL'
                }
            return result
        except Exception as e:
            logger.error(f"[dYdX] Error getting open positions: {str(e)}")
            return {}

    def get_funding_rate(self, market):
        try:
            resp = self._get(f"/markets/{market}/funding")
            funding_rate = float(resp['funding']['rate'])
            logger.info(f"[dYdX] Funding rate for {market}: {funding_rate}")
            return funding_rate
        except Exception as e:
            logger.error(f"[dYdX] Error getting funding rate: {str(e)}")
            return None

    def _get_current_price(self, market):
        try:
            resp = self._get(f"/markets/{market}")
            price = float(resp['market']['oraclePrice'])
            return price
        except Exception as e:
            logger.error(f"[dYdX] Error getting price: {str(e)}")
            return None

    def open_position(self, market, size, leverage, side, order_type="limit", price=None):
        try:
            order_data = {
                "market": market,
                "side": side.upper(),  # "BUY" or "SELL"
                "size": size,
                "leverage": leverage,
                "orderType": order_type.upper(),  # "LIMIT" or "MARKET"
                "walletAddress": self.wallet_address,
            }
            if order_type == "limit":
                if price is None:
                    price = self._get_current_price(market)
                order_data["price"] = price
            resp = self._post("/orders", order_data)
            logger.info(f"[dYdX] Order placed: {resp}")
            return resp
        except Exception as e:
            logger.error(f"[dYdX] Error opening position: {str(e)}")
            return None

    def close_position(self, market):
        try:
            positions = self.get_open_positions()
            if market not in positions:
                logger.warning(f"[dYdX] No open position for {market}")
                return False
            pos = positions[market]
            side = "SELL" if pos['side'] == "BUY" else "BUY"
            order_data = {
                "market": market,
                "side": side,
                "size": abs(pos['size']),
                "orderType": "MARKET",
                "walletAddress": self.wallet_address,
                "reduceOnly": True
            }
            resp = self._post("/orders", order_data)
            logger.info(f"[dYdX] Close order placed: {resp}")
            return resp
        except Exception as e:
            logger.error(f"[dYdX] Error closing position: {str(e)}")
            return None