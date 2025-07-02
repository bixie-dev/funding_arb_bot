from exchanges.base_exchange import BaseExchange
from utils.logger import logger
from config.config_loader import get_config
import requests
import hmac
import hashlib
import time
import json
from urllib.parse import urlencode

class Gate(BaseExchange):
    def __init__(self):
        config = get_config()
        self.api_key = config['gate']['api_key']
        self.api_secret = config['gate']['api_secret']
        self.base_url = "https://api.gateio.ws/api/v4"
        self.session = requests.Session()

    def _sign(self, method, url, query_string, body):
        t = str(int(time.time()))
        hashed_payload = hashlib.sha512(body.encode()).hexdigest() if body else ''
        to_sign = f"{method}\n{url}\n{query_string}\n{hashed_payload}\n{t}"
        sign = hmac.new(self.api_secret.encode(), to_sign.encode(), hashlib.sha512).hexdigest()
        return sign, t

    def _request(self, method, endpoint, params=None, data=None):
        url = f"{self.base_url}{endpoint}"
        query_string = ''
        if params:
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            url += '?' + query_string
        body = json.dumps(data) if data else ''
        sign, t = self._sign(method, endpoint, query_string, body)
        headers = {
            "KEY": self.api_key,
            "Timestamp": t,
            "SIGN": sign,
            "Content-Type": "application/json"
        }
        resp = self.session.request(method, url, headers=headers, data=body if data else None)
        if resp.status_code == 200:
            return resp.json()
        else:
            logger.error(f"[gate] API error: {resp.text}")
            return None

    def get_balance(self):
        try:
            resp = self._request("GET", "/futures/usdt/accounts")
            if resp:
                balance = float(resp['total']['available'])
                logger.info(f"[gate] Balance: {balance}")
                return balance
            return None
        except Exception as e:
            logger.error(f"[gate] Error getting balance: {str(e)}")
            return None

    def get_open_positions(self):
        try:
            resp = self._request("GET", "/futures/usdt/positions")
            result = {}
            for pos in resp:
                if float(pos['size']) != 0:
                    result[pos['contract']] = {
                        'size': float(pos['size']),
                        'leverage': float(pos['leverage']),
                        'entry_price': float(pos['entry_price']),
                        'mark_price': float(pos['mark_price']),
                        'unrealized_pnl': float(pos['unrealised_pnl']),
                        'position_value': float(pos['position_value']),
                        'side': 'BUY' if float(pos['size']) > 0 else 'SELL'
                    }
            return result
        except Exception as e:
            logger.error(f"[gate] Error getting open positions: {str(e)}")
            return {}

    def get_funding_rate(self, contract):
        try:
            resp = self._request("GET", "/futures/usdt/funding_rate", params={"contract": contract})
            if resp:
                funding_rate = float(resp['funding_rate'])
                logger.info(f"[gate] Funding rate for {contract}: {funding_rate}")
                return funding_rate
            return None
        except Exception as e:
            logger.error(f"[gate] Error getting funding rate: {str(e)}")
            return None

    def _get_current_price(self, contract):
        try:
            resp = self._request("GET", "/futures/usdt/tickers", params={"contract": contract})
            if resp and isinstance(resp, list) and len(resp) > 0:
                return float(resp[0]['last'])
            return None
        except Exception as e:
            logger.error(f"[gate] Error getting price: {str(e)}")
            return None

    def open_position(self, contract, size, leverage, side, order_type="limit", price=None):
        try:
            # Set leverage
            self._request("POST", f"/futures/usdt/positions/{contract}/leverage", data={"leverage": leverage})
            order = {
                "contract": contract,
                "size": size,
                "price": price if order_type == "limit" else 0,
                "tif": "gtc",
                "iceberg": 0,
                "text": "api",
                "side": side.lower(),  # "buy" or "sell"
                "reduce_only": False
            }
            if order_type == "market":
                order["price"] = 0
            resp = self._request("POST", "/futures/usdt/orders", data=order)
            logger.info(f"[gate] Order placed: {resp}")
            return resp
        except Exception as e:
            logger.error(f"[gate] Error opening position: {str(e)}")
            return None

    def close_position(self, contract):
        try:
            positions = self.get_open_positions()
            if contract not in positions:
                logger.warning(f"[gate] No open position for {contract}")
                return False
            pos = positions[contract]
            side = "sell" if pos['side'] == "BUY" else "buy"
            order = {
                "contract": contract,
                "size": abs(pos['size']),
                "price": 0,
                "tif": "gtc",
                "iceberg": 0,
                "text": "api",
                "side": side,
                "reduce_only": True
            }
            resp = self._request("POST", "/futures/usdt/orders", data=order)
            logger.info(f"[gate] Close order placed: {resp}")
            return resp
        except Exception as e:
            logger.error(f"[gate] Error closing position: {str(e)}")
            return None