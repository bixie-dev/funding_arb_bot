
import requests
import time
import hmac
import hashlib
import json
from config.config_loader import get_config

class BybitExchange:
    def __init__(self):
        config = get_config()
        self.api_key = config['bybit']['api_key']
        self.api_secret = config['bybit']['api_secret']
        self.base_url = "https://api-testnet.bybit.com"

    def _sign(self, params):
        sorted_params = sorted(params.items())
        query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
        return hmac.new(self.api_secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()

    def _send_request(self, method, endpoint, params=None):
        if params is None:
            params = {}
        params["api_key"] = self.api_key
        params["timestamp"] = int(time.time() * 1000)
        params["sign"] = self._sign(params)
        url = f"{self.base_url}{endpoint}"
        if method == "GET":
            response = requests.get(url, params=params)
        else:
            response = requests.post(url, data=params)
        return response.json()

    def place_limit_order(self, coin, leverage, size, side):
        params = {
            "symbol": f"{coin}USDT",
            "side": side.upper(),
            "order_type": "Limit",
            "qty": size,
            "price": 20000,
            "time_in_force": "GoodTillCancel",
            "reduce_only": False,
            "close_on_trigger": False
        }
        return self._send_request("POST", "/v2/private/order/create", params)

    def get_open_positions(self):
        return self._send_request("GET", "/v2/private/position/list")

    def close_position(self, position_id):
        return {"status": "manual", "position_id": position_id}

    def nuke_positions(self):
        return {"status": "manual", "note": "Loop through positions and close all"}

    def get_balance(self):
        return self._send_request("GET", "/v2/private/wallet/balance")
