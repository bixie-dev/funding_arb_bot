from exchanges.base_exchange import BaseExchange
from utils.logger import logger
from config.config_loader import get_config
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants

class Hyperliquid(BaseExchange):
    def __init__(self):
        config = get_config()
        self.api_url = constants.MAINNET_API_URL
        self.private_key = config['hyperliquid']['api_key']
        self.account_address = config['hyperliquid']['wallet']
        self.info = Info(self.api_url, skip_ws=True)
        self.exchange = Exchange(self.private_key)

    def get_balance(self):
        try:
            user_state = self.info.user_state(self.account_address)
            return float(user_state['marginSummary']['accountValue'])
        except Exception as e:
            logger.error(f"[Hyperliquid] Error getting balance: {str(e)}")
            return None

    def get_open_positions(self):
        try:
            user_state = self.info.user_state(self.account_address)
            positions = user_state.get('perpPositions', [])
            result = {}
            for pos in positions:
                result[pos['coin']] = {
                    'size': float(pos['sz']),
                    'entry_price': float(pos['entryPx']),
                    'mark_price': float(pos['markPx']),
                    'unrealized_pnl': float(pos['unrealizedPnl']),
                    'position_value': float(pos['positionValue']),
                    'side': 'BUY' if float(pos['sz']) > 0 else 'SELL'
                }
            return result
        except Exception as e:
            logger.error(f"[Hyperliquid] Error getting open positions: {str(e)}")
            return {}

    def get_funding_rate(self, coin):
        try:
            perp_meta = self.info.perp_meta()
            for perp in perp_meta:
                if perp['name'] == coin:
                    return float(perp['fundingRate'])
            return None
        except Exception as e:
            logger.error(f"[Hyperliquid] Error getting funding rate: {str(e)}")
            return None

    def open_position(self, coin, size, leverage, side, order_type="limit", price=None):
        try:
            is_buy = side.lower() == "long" or side.upper() == "BUY"
            # Set leverage
            self.exchange.update_leverage(coin, leverage)
            order_params = {
                "coin": coin,
                "is_buy": is_buy,
                "sz": size,
                "reduce_only": False,
            }
            if order_type == "limit":
                if price is None:
                    price = self._get_current_price(coin)
                order_params["limit_px"] = price
                order_params["order_type"] = {"limit": {"tif": "Gtc"}}
            else:
                order_params["order_type"] = {"market": {}}
            result = self.exchange.place_order(order_params)
            logger.info(f"[Hyperliquid] Order placed: {result}")
            return result
        except Exception as e:
            logger.error(f"[Hyperliquid] Error opening position: {str(e)}")
            return None

    def close_position(self, coin):
        try:
            positions = self.get_open_positions()
            if coin not in positions:
                logger.warning(f"[Hyperliquid] No open position for {coin}")
                return False
            pos = positions[coin]
            is_buy = pos['side'] == 'SELL'  # To close a BUY, you SELL, and vice versa
            order_params = {
                "coin": coin,
                "is_buy": is_buy,
                "sz": abs(pos['size']),
                "order_type": {"market": {}},
                "reduce_only": True
            }
            result = self.exchange.place_order(order_params)
            logger.info(f"[Hyperliquid] Close order placed: {result}")
            return result
        except Exception as e:
            logger.error(f"[Hyperliquid] Error closing position: {str(e)}")
            return None

    def _get_current_price(self, coin):
        try:
            mids = self.info.all_mids()
            for mid in mids:
                if mid['name'] == coin:
                    return float(mid['mid'])
            return None
        except Exception as e:
            logger.error(f"[Hyperliquid] Error getting price: {str(e)}")
            return None