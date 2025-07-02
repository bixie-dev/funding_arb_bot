import requests
from exchanges.base_exchange import BaseExchange
from utils.logger import logger
from config.config_loader import get_config

class Derive(BaseExchange):
    def __init__(self):
        config = get_config()
        self.base_url = "https://api.lyra.finance"
        self.api_key = config['derive'].get('address')
        self.api_secret = config['derive'].get('Session_Key')
        self.account_id = config['derive'].get('account_id')
        self.session = requests.Session()
        # Add authentication headers if required by the API

    def _post(self, endpoint, data):
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            # Add authentication headers if needed
        }
        # Add authentication/signature if required by Derive API
        response = self.session.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_balance(self):
        try:
            data = {"accountId": self.account_id}
            resp = self._post("/private/getAccount", data)
            balance = float(resp['result']['collateral'])
            logger.info(f"[Derive] Balance: {balance}")
            return balance
        except Exception as e:
            logger.error(f"[Derive] Error getting balance: {str(e)}")
            return None

    def get_open_positions(self):
        try:
            data = {"accountId": self.account_id}
            resp = self._post("/private/getPositions", data)
            positions = resp['result']['positions']
            result = {}
            for pos in positions:
                result[pos['instrument']] = {
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
            logger.error(f"[Derive] Error getting open positions: {str(e)}")
            return {}

    def get_funding_rate(self, instrument):
        try:
            data = {"instrument": instrument}
            resp = self._post("/public/getFundingRateHistory", data)
            funding_rate = float(resp['result']['fundingRates'][-1]['rate'])
            logger.info(f"[Derive] Funding rate for {instrument}: {funding_rate}")
            return funding_rate
        except Exception as e:
            logger.error(f"[Derive] Error getting funding rate: {str(e)}")
            return None

    def _get_current_price(self, instrument):
        try:
            data = {"instrument": instrument}
            resp = self._post("/public/getTicker", data)
            price = float(resp['result']['markPrice'])
            return price
        except Exception as e:
            logger.error(f"[Derive] Error getting price: {str(e)}")
            return None

    def open_position(self, instrument, size, leverage, side, order_type="limit", price=None):
        try:
            order_data = {
                "accountId": self.account_id,
                "instrument": instrument,
                "side": side.upper(),  # "BUY" or "SELL"
                "size": size,
                "leverage": leverage,
                "orderType": order_type.upper(),  # "LIMIT" or "MARKET"
            }
            if order_type == "limit":
                if price is None:
                    price = self._get_current_price(instrument)
                order_data["price"] = price
            resp = self._post("/private/order", order_data)
            logger.info(f"[Derive] Order placed: {resp}")
            return resp
        except Exception as e:
            logger.error(f"[Derive] Error opening position: {str(e)}")
            return None

    def close_position(self, instrument):
        try:
            # Get open position size and side
            positions = self.get_open_positions()
            if instrument not in positions:
                logger.warning(f"[Derive] No open position for {instrument}")
                return False
            pos = positions[instrument]
            side = "SELL" if pos['side'] == "BUY" else "BUY"
            order_data = {
                "accountId": self.account_id,
                "instrument": instrument,
                "side": side,
                "size": abs(pos['size']),
                "orderType": "MARKET",
                "reduceOnly": True
            }
            resp = self._post("/private/order", order_data)
            logger.info(f"[Derive] Close order placed: {resp}")
            return resp
        except Exception as e:
            logger.error(f"[Derive] Error closing position: {str(e)}")
            return None