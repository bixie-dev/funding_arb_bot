from exchanges.base_exchange import BaseExchange
from utils.logger import logger
from config.config_loader import get_config
from pybit.unified_trading import HTTP
from decimal import Decimal
import time

class Bybit(BaseExchange):
    def __init__(self):
        config = get_config()
        self.api_key = config['bybit']['api_key']
        self.api_secret = config['bybit']['api_secret']
        self.client = HTTP(
            testnet=False,  # Set to True for testnet
            api_key=self.api_key,
            api_secret=self.api_secret,
            recv_window=50000
        )
        self.positions = {}
        self._update_positions()

    def _update_positions(self):
        """Update local positions cache from exchange using V5 API"""
        try:
            # Try without settleCoin first
            response = self.client.get_positions(
                category="linear"
            )
            if response['retCode'] == 0:
                positions = response['result']['list']
                self.positions = {
                    pos['symbol']: {
                        'size': float(pos['size']),
                        'leverage': float(pos['leverage']),
                        'entry_price': float(pos['entryPrice']),
                        'mark_price': float(pos['markPrice']),
                        'unrealized_pnl': float(pos['unrealisedPnl']),
                        'position_value': float(pos['positionValue']),
                        'side': pos['side']
                    }
                    for pos in positions
                    if float(pos['size']) != 0
                }
            else:
                logger.error(f"[Bybit] Failed to get positions: {response['retMsg']}")
        except Exception as e:
            logger.error(f"[Bybit] Error updating positions: {str(e)}")

    def get_balance(self):
        """Get actual wallet balance from Bybit using V5 API"""
        try:
            response = self.client.get_wallet_balance(
                accountType="UNIFIED"
            )
            if response['retCode'] == 0:
                balance = float(response['result']['list'][0]['totalWalletBalance'])
                logger.info(f"[Bybit] Balance: {balance}")
                return balance
            else:
                logger.error(f"[Bybit] Failed to get balance: {response['retMsg']}")
                return None
        except Exception as e:
            logger.error(f"[Bybit] Error getting balance: {str(e)}")
            return None

    def open_position(self, coin, size, leverage, side, order_type="limit", price=None):
        """Open a real position on Bybit V5 API"""
        try:
            # Set leverage first
            coin = coin + "USDT"
            self.client.set_leverage(
                category="linear",
                symbol=coin,
                buyLeverage=str(leverage),
                sellLeverage=str(leverage)
            )
            # Side: "Buy" for long, "Sell" for short
            side = "Buy" if side.lower() == "long" else "Sell"
            order_params = {
                "category": "linear",
                "symbol": coin,
                "side": side,
                "orderType": order_type.capitalize(),
                "qty": str(size),
                "timeInForce": "GTC"
            }
            if order_type == "limit":
                if price is None:
                    price = self._get_current_price(coin)
                order_params["price"] = str(price)
            response = self.client.place_order(**order_params)
            if response['retCode'] == 0:
                order_id = response['result']['orderId']
                logger.info(f"[Bybit] Order placed successfully: {order_id}")
                time.sleep(1)
                self._update_positions()
                return order_id
            else:
                logger.error(f"[Bybit] Failed to place order: {response['retMsg']}")
                return None
        except Exception as e:
            logger.error(f"[Bybit] Error opening position: {str(e)}")
            return None

    def close_position(self, position_id):
        """Close a real position on Bybit V5 API"""
        try:
            if position_id not in self.positions:
                logger.warning(f"[Bybit] Position {position_id} not found")
                return False
            position = self.positions[position_id]
            side = "Sell" if position['side'] == "Buy" else "Buy"
            response = self.client.place_order(
                category="linear",
                symbol=position_id,
                side=side,
                orderType="Market",
                qty=str(position['size']),
                reduceOnly=True
            )
            if response['retCode'] == 0:
                logger.info(f"[Bybit] Position closed successfully: {position_id}")
                self._update_positions()
                return True
            else:
                logger.error(f"[Bybit] Failed to close position: {response['retMsg']}")
                return False
        except Exception as e:
            logger.error(f"[Bybit] Error closing position: {str(e)}")
            return False

    def get_open_positions(self):
        """Get real open positions from Bybit using V5 API"""
        self._update_positions()
        return self.positions

    def get_funding_rate(self, coin):
        """Get real funding rate from Bybit using V5 API"""
        try:
            response = self.client.get_funding_rate_history(
                category="linear",
                symbol=coin,
                limit=1
            )
            if response['retCode'] == 0 and response['result']['list']:
                funding_rate = float(response['result']['list'][0]['fundingRate'])
                logger.info(f"[Bybit] Funding rate for {coin}: {funding_rate}")
                return funding_rate
            else:
                logger.error(f"[Bybit] Failed to get funding rate: {response['retMsg']}")
                return None
        except Exception as e:
            logger.error(f"[Bybit] Error getting funding rate: {str(e)}")
            return None

    def _get_current_price(self, coin):
        """Get current market price for a symbol using V5 API"""
        try:
            response = self.client.get_tickers(
                category="linear",
                symbol=coin
            )
            if response['retCode'] == 0 and response['result']['list']:
                return float(response['result']['list'][0]['lastPrice'])
            else:
                logger.error(f"[Bybit] Failed to get price: {response['retMsg']}")
                return None
        except Exception as e:
            logger.error(f"[Bybit] Error getting price: {str(e)}")
            return None