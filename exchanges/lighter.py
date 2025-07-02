from exchanges.base_exchange import BaseExchange
from utils.logger import logger
from config.config_loader import get_config
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from anchorpy import Program, Provider, Wallet
import base58
import time
import json

class Lighter(BaseExchange):
    def __init__(self):
        config = get_config()
        self.private_key = config['lighter']['private_key']
        self.rpc_url = "https://api.mainnet-beta.solana.com"
        
        # Initialize Solana client
        self.client = AsyncClient(self.rpc_url)
        
        # Initialize wallet from private key
        self.keypair = Keypair.from_secret_key(base58.b58decode(self.private_key))
        self.wallet = Wallet(self.keypair)
        
        # Initialize Lighter program
        self.provider = Provider(self.client, self.wallet)
        self.program = Program(
            "lighter",
            self.provider,
            "https://raw.githubusercontent.com/lighter-protocol/protocol/master/target/idl/lighter.json"
        )
        
        self.positions = {}
        self._update_positions()

    async def _update_positions(self):
        """Update local positions cache from exchange"""
        try:
            # Get user account
            user_account = await self.program.account["User"].fetch(
                self.wallet.public_key
            )
            
            positions = user_account.positions
            self.positions = {
                str(pos.market_index): {
                    'size': float(pos.base_asset_amount),
                    'leverage': float(pos.leverage),
                    'entry_price': float(pos.entry_price),
                    'mark_price': float(pos.mark_price),
                    'unrealized_pnl': float(pos.unrealized_pnl),
                    'position_value': float(pos.position_value),
                    'side': 'BUY' if float(pos.base_asset_amount) > 0 else 'SELL'
                }
                for pos in positions
                if float(pos.base_asset_amount) != 0
            }
        except Exception as e:
            logger.error(f"[Lighter] Error updating positions: {str(e)}")

    async def get_balance(self):
        """Get actual wallet balance from Lighter"""
        try:
            user_account = await self.program.account["User"].fetch(
                self.wallet.public_key
            )
            balance = float(user_account.collateral)
            logger.info(f"[Lighter] Balance: {balance}")
            return balance
        except Exception as e:
            logger.error(f"[Lighter] Error getting balance: {str(e)}")
            return None

    async def open_position(self, coin, size, leverage, order_type="limit"):
        """Open a real position on Lighter"""
        try:
            # Get market index for the coin
            market_index = await self._get_market_index(coin)
            if not market_index:
                return None

            # Set leverage
            await self.program.rpc["update_leverage"](
                market_index,
                leverage,
                ctx=self.program.context
            )

            # Get current price for limit orders
            current_price = await self._get_current_price(coin)
            if not current_price:
                return None

            # Place the order
            order_params = {
                "market_index": market_index,
                "direction": "long",
                "size": size,
                "price": current_price if order_type == "limit" else None,
                "order_type": order_type,
                "reduce_only": False
            }

            tx = await self.program.rpc["place_order"](
                **order_params,
                ctx=self.program.context
            )
            
            if tx:
                logger.info(f"[Lighter] Order placed successfully: {tx}")
                await self._update_positions()
                return tx
            return None
        except Exception as e:
            logger.error(f"[Lighter] Error opening position: {str(e)}")
            return None

    async def close_position(self, position_id):
        """Close a real position on Lighter"""
        try:
            if position_id not in self.positions:
                logger.warning(f"[Lighter] Position {position_id} not found")
                return False

            position = self.positions[position_id]
            order_params = {
                "market_index": int(position_id),
                "direction": "short" if position['side'] == "BUY" else "long",
                "size": abs(float(position['size'])),
                "price": None,  # Market order
                "order_type": "market",
                "reduce_only": True
            }

            tx = await self.program.rpc["place_order"](
                **order_params,
                ctx=self.program.context
            )
            
            if tx:
                logger.info(f"[Lighter] Position closed successfully: {position_id}")
                await self._update_positions()
                return True
            return False
        except Exception as e:
            logger.error(f"[Lighter] Error closing position: {str(e)}")
            return False

    async def get_open_positions(self):
        """Get real open positions from Lighter"""
        await self._update_positions()
        return self.positions

    async def get_funding_rate(self, coin):
        """Get real funding rate from Lighter"""
        try:
            market_index = await self._get_market_index(coin)
            if not market_index:
                return None

            market = await self.program.account["Market"].fetch(market_index)
            funding_rate = float(market.funding_rate)
            logger.info(f"[Lighter] Funding rate for {coin}: {funding_rate}")
            return funding_rate
        except Exception as e:
            logger.error(f"[Lighter] Error getting funding rate: {str(e)}")
            return None

    async def _get_current_price(self, coin):
        """Get current market price for a symbol"""
        try:
            market_index = await self._get_market_index(coin)
            if not market_index:
                return None

            market = await self.program.account["Market"].fetch(market_index)
            return float(market.oracle_price)
        except Exception as e:
            logger.error(f"[Lighter] Error getting price: {str(e)}")
            return None

    async def _get_market_index(self, coin):
        """Get market index for a coin symbol"""
        try:
            markets = await self.program.account["Market"].all()
            for market in markets:
                if market.account.symbol == coin:
                    return market.public_key
            return None
        except Exception as e:
            logger.error(f"[Lighter] Error getting market index: {str(e)}")
            return None