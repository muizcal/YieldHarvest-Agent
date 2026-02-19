"""
Execution Engine - Direct DeFi Trading
Executes trades directly on protocols without vault contract
"""

import logging
from web3 import Web3
from eth_account import Account
import json

logger = logging.getLogger(__name__)


class ExecutionEngine:
    """
    Executes trades directly on DeFi protocols
    """
    
    def __init__(self, config, blockchain):
        self.config = config
        self.blockchain = blockchain
        self.w3 = blockchain.w3
        self.account = Account.from_key(config.private_key)
        
        # Track positions locally (since no contract)
        self.positions = []
        self.position_id_counter = 0
        
        # Save positions to file
        self.positions_file = "agent/data/positions.json"
        self._load_positions()
        
        logger.info(f"ExecutionEngine initialized for {self.account.address}")
    
    def _load_positions(self):
        """Load positions from file"""
        try:
            import os
            os.makedirs("agent/data", exist_ok=True)
            
            if os.path.exists(self.positions_file):
                with open(self.positions_file, 'r') as f:
                    data = json.load(f)
                    self.positions = data.get('positions', [])
                    self.position_id_counter = data.get('next_id', 0)
        except Exception as e:
            logger.warning(f"Could not load positions: {e}")
            self.positions = []
            self.position_id_counter = 0
    
    def _save_positions(self):
        """Save positions to file"""
        try:
            import os
            os.makedirs("agent/data", exist_ok=True)
            
            with open(self.positions_file, 'w') as f:
                json.dump({
                    'positions': self.positions,
                    'next_id': self.position_id_counter
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save positions: {e}")
    
    async def open_position(self, protocol, token, amount, apy, risk_score, reason):
        """
        Open a position by simulating DeFi interaction
        For hackathon demo: logs the decision and tracks it locally
        """
        logger.info(f"🚀 Opening position")
        logger.info(f"   Protocol: {protocol}")
        logger.info(f"   Token: {token}")
        logger.info(f"   Amount: {amount} BNB")
        logger.info(f"   Expected APY: {apy}%")
        logger.info(f"   Risk Score: {risk_score}/10")
        logger.info(f"   Reason: {reason}")
        
        try:
            # Check balance
            balance = self.w3.eth.get_balance(self.account.address)
            balance_bnb = float(Web3.from_wei(balance, 'ether'))
            
            if balance_bnb < amount:
                logger.error(f"❌ Insufficient balance: {balance_bnb} BNB < {amount} BNB")
                return False
            
            # For demo: We're not actually executing the trade to save gas
            # In production, this would interact with the actual protocol
            logger.info("📝 DEMO MODE: Position tracked locally (no on-chain execution)")
            
            # Create position record
            position = {
                'id': self.position_id_counter,
                'protocol': protocol,
                'token': token,
                'amount': amount,
                'entry_apy': apy,
                'risk_score': risk_score,
                'entry_timestamp': int(self.w3.eth.get_block('latest')['timestamp']),
                'reason': reason,
                'status': 'open'
            }
            
            self.positions.append(position)
            self.position_id_counter += 1
            self._save_positions()
            
            logger.info(f"✅ Position #{position['id']} created successfully!")
            logger.info(f"   Total positions: {len([p for p in self.positions if p['status'] == 'open'])}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error opening position: {e}", exc_info=True)
            return False
    
    async def close_position(self, position_id, reason):
        """Close a position"""
        logger.info(f"🔒 Closing position #{position_id}")
        logger.info(f"   Reason: {reason}")
        
        try:
            # Find position
            position = None
            for p in self.positions:
                if p['id'] == position_id and p['status'] == 'open':
                    position = p
                    break
            
            if not position:
                logger.error(f"❌ Position #{position_id} not found or already closed")
                return False
            
            # Calculate profit (simulated)
            current_time = self.w3.eth.get_block('latest')['timestamp']
            time_held = current_time - position['entry_timestamp']
            days_held = time_held / 86400
            
            # Simulate yield earned
            yearly_yield = position['amount'] * (position['entry_apy'] / 100)
            yield_earned = yearly_yield * (days_held / 365)
            
            position['status'] = 'closed'
            position['close_timestamp'] = current_time
            position['yield_earned'] = yield_earned
            position['close_reason'] = reason
            
            self._save_positions()
            
            logger.info(f"✅ Position closed!")
            logger.info(f"   Held for: {days_held:.2f} days")
            logger.info(f"   Yield earned: {yield_earned:.6f} BNB")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error closing position: {e}", exc_info=True)
            return False
    
    async def compound_position(self, position_id):
        """Compound rewards"""
        logger.info(f"🔄 Compounding position #{position_id}")
        
        try:
            position = None
            for p in self.positions:
                if p['id'] == position_id and p['status'] == 'open':
                    position = p
                    break
            
            if not position:
                logger.error(f"❌ Position #{position_id} not found")
                return False
            
            # Simulate compounding
            current_time = self.w3.eth.get_block('latest')['timestamp']
            last_compound = position.get('last_compound', position['entry_timestamp'])
            time_since = current_time - last_compound
            
            if time_since < 3600:  # Less than 1 hour
                logger.info("⏰ Too soon to compound (< 1 hour)")
                return False
            
            # Calculate rewards
            days_since = time_since / 86400
            rewards = position['amount'] * (position['entry_apy'] / 100) * (days_since / 365)
            
            # Add to position
            position['amount'] += rewards
            position['last_compound'] = current_time
            
            self._save_positions()
            
            logger.info(f"✅ Compounded {rewards:.6f} BNB")
            logger.info(f"   New amount: {position['amount']:.6f} BNB")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error compounding: {e}", exc_info=True)
            return False
    
    async def rebalance(self, from_pos, to_protocol, to_token, to_apy, risk_score, reason):
        """Rebalance from one position to another"""
        logger.info(f"⚖️ Rebalancing position #{from_pos}")
        
        try:
            # Close old position
            close_success = await self.close_position(from_pos, f"Rebalancing: {reason}")
            
            if not close_success:
                return False
            
            # Get amount from closed position
            closed_position = None
            for p in self.positions:
                if p['id'] == from_pos:
                    closed_position = p
                    break
            
            if not closed_position:
                return False
            
            amount = closed_position['amount'] + closed_position.get('yield_earned', 0)
            
            # Open new position
            return await self.open_position(
                to_protocol,
                to_token,
                amount,
                to_apy,
                risk_score,
                reason
            )
            
        except Exception as e:
            logger.error(f"❌ Error rebalancing: {e}", exc_info=True)
            return False
    
    def get_open_positions(self):
        """Get all open positions"""
        return [p for p in self.positions if p['status'] == 'open']
    
    def get_total_value(self):
        """Get total value of all open positions"""
        return sum(p['amount'] for p in self.positions if p['status'] == 'open')
    
    def get_performance_summary(self):
        """Get performance summary"""
        open_positions = [p for p in self.positions if p['status'] == 'open']
        closed_positions = [p for p in self.positions if p['status'] == 'closed']
        
        total_deployed = sum(p['amount'] for p in open_positions)
        total_yield = sum(p.get('yield_earned', 0) for p in closed_positions)
        
        return {
            'open_positions': len(open_positions),
            'closed_positions': len(closed_positions),
            'total_deployed': total_deployed,
            'total_yield_earned': total_yield,
            'positions': self.positions
        }
