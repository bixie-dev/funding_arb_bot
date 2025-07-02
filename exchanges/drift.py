import os
import asyncio
from solana.rpc.async_api import AsyncClient
from anchorpy import Wallet
from driftpy.keypair import load_keypair
from driftpy.drift_client import DriftClient
from driftpy.types import PositionDirection, OrderType
from utils.logger import logger

class Drift:
    def __init__(self, keypair_path=None, rpc_url="https://api.mainnet-beta.solana.com"):
        # Use default keypair path if not provided
        if keypair_path is None:
            keypair_path = os.path.expanduser("~/.config/solana/my-keypair.json")
        self.keypair_path = keypair_path
        self.rpc_url = rpc_url
        self.connection = None
        self.wallet = None
        self.drift_client = None
        self.initialized = False

    async def initialize(self):
        self.connection = AsyncClient(self.rpc_url)
        self.wallet = Wallet(load_keypair(self.keypair_path))
        self.drift_client = DriftClient(self.connection, self.wallet, "mainnet")
        await self.drift_client.subscribe()
        self.initialized = True

    async def close(self):
        if self.drift_client:
            await self.drift_client.unsubscribe()
        if self.connection:
            await self.connection.close()
        self.initialized = False

    async def get_balance(self):
        if not self.initialized:
            await self.initialize()
        user = await self.drift_client.get_user()
        return user.collateral

    async def get_open_positions(self):
        if not self.initialized:
            await self.initialize()
        user = await self.drift_client.get_user()
        positions = {}
        for pos in user.perp_positions:
            if pos.base_asset_amount != 0:
                market_index = pos.market_index
                market_name = str(market_index)
                positions[market_name] = {
                    'size': pos.base_asset_amount,
                    'leverage': user.leverage,
                    'entry_price': pos.quote_entry_amount,
                    'mark_price': pos.last_cumulative_funding_rate,
                    'unrealized_pnl': pos.unrealized_pnl,
                    'position_value': pos.quote_asset_amount,
                    'side': 'BUY' if pos.base_asset_amount > 0 else 'SELL'
                }
        return positions

    async def get_funding_rate(self, market_index):
        if not self.initialized:
            await self.initialize()
        market = await self.drift_client.get_perp_market_account(market_index)
        return market.amm.last_funding_rate

    async def get_current_price(self, market_index):
        if not self.initialized:
            await self.initialize()
        market = await self.drift_client.get_perp_market_account(market_index)
        return market.amm.last_mark_price_twap

    async def open_position(self, market_index, size, leverage, side, order_type="limit", price=None):
        if not self.initialized:
            await self.initialize()
        direction = PositionDirection.LONG if side.upper() == "BUY" else PositionDirection.SHORT
        order_type_enum = OrderType.LIMIT if order_type.lower() == "limit" else OrderType.MARKET
        try:
            tx = await self.drift_client.open_position(
                market_index=market_index,
                direction=direction,
                base_asset_amount=size,
                order_type=order_type_enum,
                price=price,
                leverage=leverage
            )
            logger.info(f"[Drift] Opened position: {tx}")
            return tx
        except Exception as e:
            logger.error(f"[Drift] Error opening position: {str(e)}")
            return None

    async def close_position(self, market_index):
        if not self.initialized:
            await self.initialize()
        try:
            tx = await self.drift_client.close_position(market_index)
            logger.info(f"[Drift] Closed position: {tx}")
            return tx
        except Exception as e:
            logger.error(f"[Drift] Error closing position: {str(e)}")
            return None

# Example usage:
# drift = Drift()
# asyncio.run(drift.get_balance())