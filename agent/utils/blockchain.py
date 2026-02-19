"""
Blockchain Client - Simplified Version
No smart contract dependencies - just Web3 basics
"""

from web3 import Web3
from web3.middleware import geth_poa_middleware
import logging

logger = logging.getLogger(__name__)


class BlockchainClient:
    def __init__(self, config):
        self.config = config
        self.w3 = Web3(Web3.HTTPProvider(config.bsc_rpc_url))
        
        # BSC is POA chain - inject POA middleware
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        logger.info(f"Connected to BSC: {self.w3.is_connected()}")
    
    async def get_balance(self, address):
        """Get BNB balance"""
        return self.w3.eth.get_balance(Web3.to_checksum_address(address))
    
    async def is_valid_session_key(self, address):
        """
        Check if address is valid (simplified - just check if it's the owner)
        For the simplified version, we don't use session keys
        """
        # Always return True for owner address
        return True
    
    async def get_whitelisted_protocols(self):
        """
        Get whitelisted protocols (hardcoded for demo)
        """
        return [
            Web3.to_checksum_address("0xa5f8C5Dbd5F286960b9d90548680aE5ebFf07652"),  # PancakeSwap
            Web3.to_checksum_address("0xfD36E2c2a6789Db23113685031d7F16329158384"),  # Venus
            Web3.to_checksum_address("0xd4ae6eCA985340Dd434D38F470aCCce4DC78D109"),  # Thena
        ]
    
    async def get_all_positions(self):
        """
        Get positions from local storage (no contract)
        This will be handled by ExecutionEngine
        """
        return []
    
    async def get_block_number(self):
        """Get current block number"""
        return self.w3.eth.block_number
    
    async def get_performance_metrics(self):
        """
        Get performance metrics (simplified)
        """
        return {
            'tvl': 0,
            'deposited': 0,
            'withdrawn': 0,
            'yield_earned': 0,
            'gas_spent': 0,
            'net_profit': 0,
            'average_apy': 0
        }
    
    async def log_performance_snapshot(self, tvl, yield_earned, avg_apy, active_count):
        """Log performance (to file instead of blockchain)"""
        logger.info(f"Performance: TVL={tvl}, Yield={yield_earned}, APY={avg_apy}, Active={active_count}")
