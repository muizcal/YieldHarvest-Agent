"""
Discovery Engine
Scans BNB Chain for yield farming opportunities
"""

import logging
from typing import List, Dict
import asyncio

logger = logging.getLogger(__name__)


class DiscoveryEngine:
    """
    Discovers yield farming opportunities across BSC protocols
    """
    
    def __init__(self, config, blockchain):
        self.config = config
        self.blockchain = blockchain
        
        # Protocols to scan
        self.protocols = {
            'pancakeswap': self.config.pancake_masterchef,
            'venus': self.config.venus_comptroller,
            'thena': self.config.thena_router,
        }
    
    async def discover_opportunities(self) -> List[Dict]:
        """
        Scan all protocols for yield opportunities
        
        Returns:
            List of opportunities with protocol, token, APY, TVL, etc.
        """
        logger.info("Scanning protocols for opportunities...")
        
        all_opportunities = []
        
        # Scan each protocol in parallel
        tasks = [
            self._scan_pancakeswap(),
            self._scan_venus(),
            self._scan_thena(),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error scanning protocol: {result}")
            else:
                all_opportunities.extend(result)
        
        logger.info(f"Found {len(all_opportunities)} total opportunities")
        
        return all_opportunities
    
    async def _scan_pancakeswap(self) -> List[Dict]:
        """Scan PancakeSwap MasterChef for LP farming opportunities"""
        opportunities = []
        
        try:
            # Get pool count from MasterChef
            pool_count = await self.blockchain.get_pancake_pool_count()
            
            # Scan top pools (limit to avoid rate limits)
            max_pools = min(pool_count, 50)
            
            for pool_id in range(max_pools):
                try:
                    pool_info = await self.blockchain.get_pancake_pool_info(pool_id)
                    
                    # Calculate APY
                    apy = await self._calculate_pancake_apy(pool_id, pool_info)
                    
                    # Get TVL
                    tvl = pool_info.get('total_staked', 0)
                    
                    # Only include if meets minimum criteria
                    if apy >= self.config.min_apy and tvl >= 10000:  # $10k minimum
                        opportunities.append({
                            'protocol': 'pancakeswap',
                            'protocol_address': self.config.pancake_masterchef,
                            'pool_id': pool_id,
                            'token': pool_info['lp_token'],
                            'token_symbol': pool_info.get('symbol', 'LP'),
                            'apy': apy,
                            'tvl': tvl,
                            'contract_age_days': await self._get_contract_age(pool_info['lp_token']),
                        })
                
                except Exception as e:
                    logger.debug(f"Error scanning PancakeSwap pool {pool_id}: {e}")
            
            logger.info(f"Found {len(opportunities)} PancakeSwap opportunities")
            
        except Exception as e:
            logger.error(f"Error scanning PancakeSwap: {e}")
        
        return opportunities
    
    async def _scan_venus(self) -> List[Dict]:
        """Scan Venus Protocol for lending opportunities"""
        opportunities = []
        
        try:
            # Get all vTokens from Venus
            markets = await self.blockchain.get_venus_markets()
            
            for market in markets:
                try:
                    # Get supply APY
                    supply_apy = await self.blockchain.get_venus_supply_apy(market)
                    
                    # Get market info
                    market_info = await self.blockchain.get_venus_market_info(market)
                    
                    tvl = market_info.get('total_supply', 0)
                    
                    if supply_apy >= self.config.min_apy and tvl >= 10000:
                        opportunities.append({
                            'protocol': 'venus',
                            'protocol_address': self.config.venus_comptroller,
                            'token': market,
                            'token_symbol': market_info.get('symbol', 'vToken'),
                            'apy': supply_apy,
                            'tvl': tvl,
                            'contract_age_days': await self._get_contract_age(market),
                        })
                
                except Exception as e:
                    logger.debug(f"Error scanning Venus market {market}: {e}")
            
            logger.info(f"Found {len(opportunities)} Venus opportunities")
            
        except Exception as e:
            logger.error(f"Error scanning Venus: {e}")
        
        return opportunities
    
    async def _scan_thena(self) -> List[Dict]:
        """Scan Thena for gauge/bribe opportunities"""
        opportunities = []
        
        try:
            # Get all gauges from Thena
            gauges = await self.blockchain.get_thena_gauges()
            
            for gauge in gauges:
                try:
                    # Get APY from bribes + emissions
                    apy = await self.blockchain.get_thena_gauge_apy(gauge)
                    
                    gauge_info = await self.blockchain.get_thena_gauge_info(gauge)
                    tvl = gauge_info.get('total_staked', 0)
                    
                    if apy >= self.config.min_apy and tvl >= 10000:
                        opportunities.append({
                            'protocol': 'thena',
                            'protocol_address': self.config.thena_router,
                            'gauge': gauge,
                            'token': gauge_info['lp_token'],
                            'token_symbol': gauge_info.get('symbol', 'LP'),
                            'apy': apy,
                            'tvl': tvl,
                            'contract_age_days': await self._get_contract_age(gauge),
                        })
                
                except Exception as e:
                    logger.debug(f"Error scanning Thena gauge {gauge}: {e}")
            
            logger.info(f"Found {len(opportunities)} Thena opportunities")
            
        except Exception as e:
            logger.error(f"Error scanning Thena: {e}")
        
        return opportunities
    
    async def _calculate_pancake_apy(self, pool_id: int, pool_info: Dict) -> float:
        """Calculate APY for PancakeSwap pool"""
        try:
            # Get CAKE rewards per block
            cake_per_block = pool_info.get('alloc_point', 0) * pool_info.get('cake_per_block', 0)
            
            # Get CAKE price
            cake_price = await self.blockchain.get_token_price('CAKE')
            
            # Calculate yearly rewards
            blocks_per_year = 10512000  # BSC: ~3 seconds per block
            yearly_rewards = cake_per_block * blocks_per_year * cake_price
            
            # Calculate APY
            tvl = pool_info.get('total_staked', 1)  # Avoid division by zero
            apy = (yearly_rewards / tvl) * 100
            
            return round(apy, 2)
            
        except Exception as e:
            logger.debug(f"Error calculating PancakeSwap APY: {e}")
            return 0.0
    
    async def _get_contract_age(self, address: str) -> int:
        """Get contract age in days"""
        try:
            creation_block = await self.blockchain.get_contract_creation_block(address)
            current_block = await self.blockchain.get_block_number()
            
            blocks_diff = current_block - creation_block
            days = blocks_diff * 3 / 86400  # 3 second blocks
            
            return int(days)
            
        except Exception:
            return 0
