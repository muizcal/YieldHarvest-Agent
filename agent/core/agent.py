"""
YieldHarvest Agent - Main Orchestrator
Autonomous AI agent for DeFi yield farming on BNB Chain
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from web3 import Web3
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import Config
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engines.discovery import DiscoveryEngine
from engines.evaluation import EvaluationEngine
from engines.execution import ExecutionEngine
from strategies.yield_optimizer import YieldOptimizer
from strategies.risk_manager import RiskManager
from utils.logger import setup_logger
from utils.blockchain import BlockchainClient
logger = setup_logger(__name__)


class YieldHarvestAgent:
    """
    Main agent orchestrator that coordinates discovery, evaluation, and execution
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.blockchain = BlockchainClient(config)
        
        # Initialize engines
        self.discovery = DiscoveryEngine(config, self.blockchain)
        self.evaluation = EvaluationEngine(config, self.blockchain)
        self.execution = ExecutionEngine(config, self.blockchain)
        
        # Initialize strategies
        self.yield_optimizer = YieldOptimizer(config)
        self.risk_manager = RiskManager(config)
        
        # Scheduler for periodic tasks
        self.scheduler = AsyncIOScheduler()
        
        # State tracking
        self.is_running = False
        self.last_scan_time = None
        self.last_compound_time = None
        self.last_rebalance_time = None
        
        logger.info("YieldHarvest Agent initialized")
    
    async def start(self):
        """Start the autonomous agent"""
        logger.info("🚀 Starting YieldHarvest Agent...")
        
        # Verify contracts are deployed
        await self._verify_setup()
        
        # Schedule periodic tasks
        self._schedule_tasks()
        
        # Start scheduler
        self.scheduler.start()
        self.is_running = True
        
        logger.info("✅ Agent is now running autonomously")
        
        # Trigger first scan immediately
        logger.info("🎬 Triggering immediate first scan...")
        asyncio.create_task(self._scan_opportunities())
        
        # Run main loop
        await self._main_loop()
    
    async def _verify_setup(self):
        """Verify all contracts and configurations are correct"""
        logger.info("Verifying setup...")
        
        # Check vault manager
        vault_balance = await self.blockchain.get_balance(
            self.config.vault_manager_address
        )
        logger.info(f"Vault balance: {Web3.from_wei(vault_balance, 'ether')} BNB")
        
        # Check session key
        is_valid = await self.blockchain.is_valid_session_key(
            self.config.session_key_address
        )
        if not is_valid:
            logger.warning("⚠️ Session key is not valid or expired - agent will run in read-only mode")
        else:
            logger.info(f"✅ Session key is valid")
        
        # Check whitelisted protocols
        protocols = await self.blockchain.get_whitelisted_protocols()
        logger.info(f"Whitelisted protocols: {len(protocols)}")
    
    def _schedule_tasks(self):
        """Schedule periodic agent tasks"""
        # Scan for opportunities every 1 minute
        self.scheduler.add_job(
            lambda: asyncio.create_task(self._scan_opportunities()),
            'interval',
            minutes=1,
            id='scan_opportunities'
        )
        
        # Compound positions every 4 hours (or configured interval)
        compound_hours = self.config.compound_interval // 3600
        self.scheduler.add_job(
            lambda: asyncio.create_task(self._compound_all_positions()),
            'interval',
            hours=compound_hours,
            id='compound_positions'
        )
        
        # Check for rebalancing opportunities every hour
        self.scheduler.add_job(
            lambda: asyncio.create_task(self._check_rebalancing()),
            'interval',
            hours=1,
            id='check_rebalancing'
        )
        
        # Log performance metrics every 6 hours
        self.scheduler.add_job(
            lambda: asyncio.create_task(self._log_performance()),
            'interval',
            hours=6,
            id='log_performance'
        )
    
    async def _main_loop(self):
        """Main agent loop - runs continuously"""
        try:
            while self.is_running:
                # Health check
                await self._health_check()
                
                # Sleep for 60 seconds before next iteration
                await asyncio.sleep(60)
                
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
            await self.shutdown()
        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
            await self.shutdown()
    
    async def _scan_opportunities(self):
        """Scan for new yield opportunities"""
        logger.info("🔍 Scanning for yield opportunities...")
        
        try:
            # Discover opportunities
            opportunities = await self.discovery.discover_opportunities()
            logger.info(f"Found {len(opportunities)} potential opportunities")
            
            if not opportunities:
                logger.warning("No opportunities found - will try again next cycle")
                return
            
            # Evaluate each opportunity
            evaluated = []
            for opp in opportunities:
                score = await self.evaluation.evaluate_opportunity(opp)
                opp['score'] = score
                evaluated.append(opp)
            
            # Filter by minimum thresholds
            qualified = [
                opp for opp in evaluated
                if opp['apy'] >= self.config.min_apy
                and opp['score']['risk_score'] <= self.config.max_risk_score
            ]
            
            logger.info(f"Qualified opportunities: {len(qualified)}")
            
            if not qualified:
                logger.info("No qualified opportunities after filtering")
                return
            
            # Get current positions
            current_positions = await self.blockchain.get_all_positions()
            logger.info(f"Current positions: {len(current_positions)}")
            
            # Use AI to decide which opportunities to pursue
            decisions = await self.yield_optimizer.optimize_portfolio(
                qualified,
                current_positions
            )
            
            logger.info(f"Generated {len(decisions)} decisions")
            
            # Execute decisions
            for decision in decisions:
                await self._execute_decision(decision)
            
            self.last_scan_time = datetime.now()
            
        except Exception as e:
            logger.error(f"Error scanning opportunities: {e}", exc_info=True)
    
    async def _compound_all_positions(self):
        """Compound rewards for all active positions"""
        logger.info("🔄 Compounding all positions...")
        
        try:
            positions = await self.blockchain.get_all_positions()
            active_positions = [p for p in positions if p['amount'] > 0]
            
            logger.info(f"Active positions: {len(active_positions)}")
            
            for position in active_positions:
                # Check if compound interval has passed
                time_since_compound = datetime.now() - datetime.fromtimestamp(position['last_compound_time'])
                
                if time_since_compound.total_seconds() >= self.config.compound_interval:
                    try:
                        await self.execution.compound_position(position['id'])
                        logger.info(f"✅ Compounded position {position['id']}")
                    except Exception as e:
                        logger.error(f"Failed to compound position {position['id']}: {e}")
            
            self.last_compound_time = datetime.now()
            
        except Exception as e:
            logger.error(f"Error compounding positions: {e}", exc_info=True)
    
    async def _check_rebalancing(self):
        """Check if any positions should be rebalanced"""
        logger.info("⚖️ Checking for rebalancing opportunities...")
        
        try:
            # Get current positions
            current_positions = await self.blockchain.get_all_positions()
            active_positions = [p for p in current_positions if p['amount'] > 0]
            
            if not active_positions:
                logger.info("No active positions to rebalance")
                return
            
            # Discover current opportunities
            opportunities = await self.discovery.discover_opportunities()
            
            # Evaluate opportunities
            evaluated = []
            for opp in opportunities:
                score = await self.evaluation.evaluate_opportunity(opp)
                opp['score'] = score
                evaluated.append(opp)
            
            # Check if any opportunity is significantly better
            rebalance_decisions = await self.yield_optimizer.check_rebalancing(
                active_positions,
                evaluated,
                self.config.rebalance_threshold
            )
            
            if rebalance_decisions:
                logger.info(f"Found {len(rebalance_decisions)} rebalancing opportunities")
                
                for decision in rebalance_decisions:
                    await self._execute_decision(decision)
            else:
                logger.info("No rebalancing needed")
            
            self.last_rebalance_time = datetime.now()
            
        except Exception as e:
            logger.error(f"Error checking rebalancing: {e}", exc_info=True)
    
    async def _execute_decision(self, decision: Dict):
        """Execute an agent decision"""
        logger.info(f"Executing decision: {decision['action']}")
        
        try:
            # Risk check
            if not self.risk_manager.approve_decision(decision):
                logger.warning(f"Decision rejected by risk manager: {decision}")
                return
            
            # Execute based on action type
            if decision['action'] == 'OPEN_POSITION':
                await self.execution.open_position(
                    decision['protocol'],
                    decision['token'],
                    decision['amount'],
                    decision['apy'],
                    decision['risk_score'],
                    decision['reason']
                )
            
            elif decision['action'] == 'CLOSE_POSITION':
                await self.execution.close_position(
                    decision['position_id'],
                    decision['reason']
                )
            
            elif decision['action'] == 'REBALANCE':
                await self.execution.rebalance(
                    decision['from_position_id'],
                    decision['to_protocol'],
                    decision['to_token'],
                    decision['to_apy'],
                    decision['risk_score'],
                    decision['reason']
                )
            
            logger.info(f"✅ Decision executed successfully")
            
        except Exception as e:
            logger.error(f"Error executing decision: {e}", exc_info=True)
    
    async def _log_performance(self):
        """Log performance metrics onchain"""
        logger.info("📊 Logging performance metrics...")
        
        try:
            metrics = await self.blockchain.get_performance_metrics()
            
            logger.info(f"Performance Metrics:")
            logger.info(f"  Total Deposited: {Web3.from_wei(metrics['deposited'], 'ether')} BNB")
            logger.info(f"  Total Withdrawn: {Web3.from_wei(metrics['withdrawn'], 'ether')} BNB")
            logger.info(f"  Yield Earned: {Web3.from_wei(metrics['yield_earned'], 'ether')} BNB")
            logger.info(f"  Gas Spent: {Web3.from_wei(metrics['gas_spent'], 'ether')} BNB")
            logger.info(f"  Net Profit: {Web3.from_wei(metrics['net_profit'], 'ether')} BNB")
            
            # Log to contract
            positions = await self.blockchain.get_all_positions()
            active_count = len([p for p in positions if p['amount'] > 0])
            
            await self.blockchain.log_performance_snapshot(
                metrics['tvl'],
                metrics['yield_earned'],
                metrics['average_apy'],
                active_count
            )
            
        except Exception as e:
            logger.error(f"Error logging performance: {e}", exc_info=True)
    
    async def _health_check(self):
        """Perform health check of the agent"""
        try:
            # Check blockchain connection
            block_number = await self.blockchain.get_block_number()
            
            # Check session key validity
            is_valid = await self.blockchain.is_valid_session_key(
                self.config.session_key_address
            )
            
            if not is_valid:
                logger.error("⚠️ Session key is no longer valid!")
                await self.shutdown()
            
        except Exception as e:
            logger.error(f"Health check failed: {e}", exc_info=True)
    
    async def shutdown(self):
        """Gracefully shutdown the agent"""
        logger.info("Shutting down agent...")
        
        self.is_running = False
        
        if self.scheduler.running:
            self.scheduler.shutdown()
        
        logger.info("✅ Agent shutdown complete")


async def main():
    """Main entry point"""
    # Load configuration
    config = Config()
    
    # Create and start agent
    agent = YieldHarvestAgent(config)
    
    try:
        await agent.start()
    except KeyboardInterrupt:
        await agent.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
