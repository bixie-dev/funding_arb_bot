from exchanges.base_exchange import BaseExchange
from utils.logger import logger
from config.config_loader import get_config
from web3 import Web3
from eth_account import Account
import json
import time

class Gmx(BaseExchange):
    def __init__(self):
        config = get_config()
        self.private_key = config['gmx']['private_key']
        self.rpc_url = config['gmx']['rpc_url']  # Arbitrum or Avalanche RPC
        self.chain_id = config['gmx']['chain_id']  # 42161 for Arbitrum, 43114 for Avalanche
        
        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        self.account = Account.from_key(self.private_key)
        
        # Load contract ABIs
        self.router_abi = self._load_abi('gmx_router')
        self.vault_abi = self._load_abi('gmx_vault')
        self.position_router_abi = self._load_abi('gmx_position_router')
        
        # Contract addresses
        self.router_address = self._get_contract_address('router')
        self.vault_address = self._get_contract_address('vault')
        self.position_router_address = self._get_contract_address('position_router')
        
        # Initialize contracts
        self.router = self.w3.eth.contract(
            address=self.router_address,
            abi=self.router_abi
        )
        self.vault = self.w3.eth.contract(
            address=self.vault_address,
            abi=self.vault_abi
        )
        self.position_router = self.w3.eth.contract(
            address=self.position_router_address,
            abi=self.position_router_abi
        )
        
        self.positions = {}
        self._update_positions()

    def _load_abi(self, contract_name):
        """Load contract ABI from file"""
        try:
            with open(f'config/abis/{contract_name}.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"[GMX] Error loading ABI for {contract_name}: {str(e)}")
            return None

    def _get_contract_address(self, contract_type):
        """Get contract address based on chain"""
        addresses = {
            'router': {
                '42161': '0xaBBc5F99639c9B6bCb58544ddf04EFA6802F4064',  # Arbitrum
                '43114': '0x5F719c2F1095F7B9fc68a68e35B51194f4b6eF57'   # Avalanche
            },
            'vault': {
                '42161': '0x489ee077994B6658eAfA855C308275EAd8097C4A',
                '43114': '0x9ab2De34A33fB459b538c43f251eB825645e8595'
            },
            'position_router': {
                '42161': '0xb87a436B93fFE9D75c5cFA7bAcFff96430b09868',
                '43114': '0xffF6D276Bc37c61A23f06410Dce4A400f66420f8'
            }
        }
        return addresses[contract_type][str(self.chain_id)]

    def _update_positions(self):
        """Update local positions cache from exchange"""
        try:
            positions = self.vault.functions.getPositions(
                self.account.address
            ).call()
            
            self.positions = {
                pos['indexToken']: {
                    'size': float(pos['size']) / 1e30,  # GMX uses 1e30 for decimals
                    'leverage': float(pos['leverage']) / 1e4,
                    'entry_price': float(pos['averagePrice']) / 1e30,
                    'mark_price': float(pos['markPrice']) / 1e30,
                    'unrealized_pnl': float(pos['unrealisedPnl']) / 1e30,
                    'position_value': float(pos['positionValue']) / 1e30,
                    'side': 'BUY' if float(pos['size']) > 0 else 'SELL'
                }
                for pos in positions
                if float(pos['size']) != 0
            }
        except Exception as e:
            logger.error(f"[GMX] Error updating positions: {str(e)}")

    def get_balance(self):
        """Get actual wallet balance from GMX"""
        try:
            balance = self.vault.functions.getBalance(
                self.account.address
            ).call()
            balance = float(balance) / 1e30  # GMX uses 1e30 for decimals
            logger.info(f"[GMX] Balance: {balance}")
            return balance
        except Exception as e:
            logger.error(f"[GMX] Error getting balance: {str(e)}")
            return None

    def open_position(self, coin, size, leverage, order_type="limit"):
        """Open a real position on GMX"""
        try:
            # Convert size to GMX decimals
            size_wei = int(size * 1e30)
            
            # Get current price
            current_price = self._get_current_price(coin)
            if not current_price:
                return None

            # Prepare transaction
            tx_params = {
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 500000,
                'gasPrice': self.w3.eth.gas_price
            }

            # Create position
            tx = self.position_router.functions.createIncreasePosition(
                [coin],  # path
                coin,    # indexToken
                size_wei,
                0,       # minOut
                int(leverage * 1e4),  # leverage in basis points
                True,    # isLong
                int(current_price * 1e30),  # acceptablePrice
                int(time.time()) + 300  # executionFee
            ).build_transaction(tx_params)

            # Sign and send transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt['status'] == 1:
                logger.info(f"[GMX] Position opened successfully: {tx_hash.hex()}")
                self._update_positions()
                return tx_hash.hex()
            return None
        except Exception as e:
            logger.error(f"[GMX] Error opening position: {str(e)}")
            return None

    def close_position(self, position_id):
        """Close a real position on GMX"""
        try:
            if position_id not in self.positions:
                logger.warning(f"[GMX] Position {position_id} not found")
                return False

            position = self.positions[position_id]
            size_wei = int(abs(float(position['size'])) * 1e30)

            # Prepare transaction
            tx_params = {
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 500000,
                'gasPrice': self.w3.eth.gas_price
            }

            # Create decrease position
            tx = self.position_router.functions.createDecreasePosition(
                [position_id],  # path
                position_id,    # indexToken
                size_wei,
                0,             # minOut
                True,          # isLong
                self.account.address,  # receiver
                int(time.time()) + 300  # executionFee
            ).build_transaction(tx_params)

            # Sign and send transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt['status'] == 1:
                logger.info(f"[GMX] Position closed successfully: {position_id}")
                self._update_positions()
                return True
            return False
        except Exception as e:
            logger.error(f"[GMX] Error closing position: {str(e)}")
            return False

    def get_open_positions(self):
        """Get real open positions from GMX"""
        self._update_positions()
        return self.positions

    def get_funding_rate(self, coin):
        """Get real funding rate from GMX"""
        try:
            funding_rate = self.vault.functions.getFundingRate(coin).call()
            funding_rate = float(funding_rate) / 1e6  # GMX uses 1e6 for funding rates
            logger.info(f"[GMX] Funding rate for {coin}: {funding_rate}")
            return funding_rate
        except Exception as e:
            logger.error(f"[GMX] Error getting funding rate: {str(e)}")
            return None

    def _get_current_price(self, coin):
        """Get current market price for a symbol"""
        try:
            price = self.vault.functions.getMaxPrice(coin).call()
            return float(price) / 1e30  # GMX uses 1e30 for decimals
        except Exception as e:
            logger.error(f"[GMX] Error getting price: {str(e)}")
            return None