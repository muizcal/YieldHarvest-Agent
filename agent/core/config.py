"""
Agent Configuration
Loads and manages all configuration from environment variables
"""

import os
from typing import Optional
from dotenv import load_dotenv
from web3 import Web3

# Load environment variables
load_dotenv()


class Config:
    """Agent configuration loaded from environment"""
    
    def __init__(self):
        # Blockchain
        self.bsc_rpc_url = os.getenv('BSC_RPC_URL', 'https://bsc-dataseed1.binance.org')
        self.chain_id = int(os.getenv('CHAIN_ID', '56'))
        self.private_key = os.getenv('PRIVATE_KEY')
        
        if not self.private_key:
            raise ValueError("PRIVATE_KEY environment variable is required")
        
        # Contract addresses
        self.vault_manager_address = self._get_checksum_address('VAULT_MANAGER_ADDRESS')
        self.session_key_manager_address = self._get_checksum_address('SESSION_KEY_MANAGER_ADDRESS')
        self.decision_logger_address = self._get_checksum_address('DECISION_LOGGER_ADDRESS')
        
        # Session key (derived from private key or separate)
        self.session_key_address = Web3().eth.account.from_key(self.private_key).address
        
        # Agent parameters
        self.min_apy = float(os.getenv('AGENT_MIN_APY', '5.0'))
        self.max_risk_score = float(os.getenv('AGENT_MAX_RISK_SCORE', '7.0'))
        self.compound_interval = int(os.getenv('AGENT_COMPOUND_INTERVAL', '14400'))  # 4 hours
        self.rebalance_threshold = float(os.getenv('AGENT_REBALANCE_THRESHOLD', '2.0'))
        self.max_allocation_per_protocol = float(os.getenv('AGENT_MAX_ALLOCATION_PER_PROTOCOL', '20.0'))
        self.initial_capital = float(os.getenv('AGENT_INITIAL_CAPITAL', '1.0'))
        
        # Protocol addresses (BSC Mainnet)
        self.pancake_router = self._get_checksum_address(
            'PANCAKE_ROUTER',
            '0x10ED43C718714eb63d5aA57B78B54704E256024E'
        )
        self.pancake_masterchef = self._get_checksum_address(
            'PANCAKE_MASTERCHEF',
            '0xa5f8C5Dbd5F286960b9d90548680aE5ebFf07652'
        )
        self.venus_comptroller = self._get_checksum_address(
            'VENUS_COMPTROLLER',
            '0xfD36E2c2a6789Db23113685031d7F16329158384'
        )
        self.thena_router = self._get_checksum_address(
            'THENA_ROUTER',
            '0xd4ae6eCA985340Dd434D38F470aCCce4DC78D109'
        )
        
        # Token addresses
        self.wbnb = self._get_checksum_address(
            'WBNB',
            '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c'
        )
        self.usdt = self._get_checksum_address(
            'USDT',
            '0x55d398326f99059fF775485246999027B3197955'
        )
        self.busd = self._get_checksum_address(
            'BUSD',
            '0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56'
        )
        
        # API keys
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.bscscan_api_key = os.getenv('BSCSCAN_API_KEY')
        self.coingecko_api_key = os.getenv('COINGECKO_API_KEY')
        
        # Safety settings
        self.max_slippage = float(os.getenv('MAX_SLIPPAGE', '1.0'))
        self.max_gas_price = int(os.getenv('MAX_GAS_PRICE', '10'))  # gwei
        self.emergency_pause = os.getenv('EMERGENCY_PAUSE', 'false').lower() == 'true'
        
        # Logging
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_file = os.getenv('LOG_FILE', 'logs/agent.log')
        
        # Development
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'
    
    def _get_checksum_address(self, env_var: str, default: Optional[str] = None) -> str:
        """Get checksummed address from environment or default"""
        address = os.getenv(env_var, default)
        if not address:
            if default is None:
                raise ValueError(f"{env_var} environment variable is required")
            return Web3.to_checksum_address(default)
        return Web3.to_checksum_address(address)
    
    def validate(self):
        """Validate all required configuration is present"""
        required = [
            ('VAULT_MANAGER_ADDRESS', self.vault_manager_address),
            ('SESSION_KEY_MANAGER_ADDRESS', self.session_key_manager_address),
            ('DECISION_LOGGER_ADDRESS', self.decision_logger_address),
        ]
        
        missing = [name for name, value in required if not value]
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
    
    def __str__(self):
        """String representation (hiding sensitive data)"""
        return f"""
YieldHarvest Agent Configuration:
================================
Chain ID: {self.chain_id}
Vault Manager: {self.vault_manager_address}
Session Key: {self.session_key_address}

Agent Parameters:
- Min APY: {self.min_apy}%
- Max Risk Score: {self.max_risk_score}/10
- Compound Interval: {self.compound_interval}s ({self.compound_interval // 3600}h)
- Rebalance Threshold: {self.rebalance_threshold}%
- Max Allocation: {self.max_allocation_per_protocol}%

Safety:
- Max Slippage: {self.max_slippage}%
- Max Gas Price: {self.max_gas_price} gwei
- Emergency Pause: {self.emergency_pause}
"""
