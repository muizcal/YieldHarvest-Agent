"""
Risk Manager
Validates and approves/rejects agent decisions based on risk parameters
"""

import logging
from typing import Dict
from web3 import Web3

logger = logging.getLogger(__name__)


class RiskManager:
    """
    Manages risk assessment and decision approval
    """
    
    def __init__(self, config):
        self.config = config
        
        # Risk limits
        self.max_position_size = 0.01  # Max 0.01 BNB per position
        self.max_risk_score = config.max_risk_score
        self.min_apy = config.min_apy
        self.max_allocation_per_protocol = config.max_allocation_per_protocol / 100  # Convert to decimal
    
    def approve_decision(self, decision: Dict) -> bool:
        """
        Approve or reject a decision based on risk parameters
        
        Args:
            decision: Decision dict with action, amount, risk_score, etc.
            
        Returns:
            True if approved, False if rejected
        """
        action = decision.get('action')
        
        logger.info(f"🛡️ Risk Manager evaluating {action} decision...")
        
        try:
            # Check based on action type
            if action == 'OPEN_POSITION':
                return self._approve_open_position(decision)
            
            elif action == 'CLOSE_POSITION':
                return self._approve_close_position(decision)
            
            elif action == 'REBALANCE':
                return self._approve_rebalance(decision)
            
            else:
                logger.warning(f"Unknown action type: {action}")
                return False
                
        except Exception as e:
            logger.error(f"Error in risk approval: {e}")
            return False
    
    def _approve_open_position(self, decision: Dict) -> bool:
        """Approve opening a new position"""
        
        amount = decision.get('amount', 0)
        apy = decision.get('apy', 0)
        risk_score = decision.get('risk_score', 10)
        
        # Check amount
        if amount <= 0:
            logger.warning("❌ Rejected: Amount must be positive")
            return False
        
        if amount > self.max_position_size:
            logger.warning(f"❌ Rejected: Amount {amount} BNB exceeds max position size {self.max_position_size} BNB")
            return False
        
        # Check APY
        if apy < self.min_apy:
            logger.warning(f"❌ Rejected: APY {apy}% below minimum {self.min_apy}%")
            return False
        
        # Check risk score
        if risk_score > self.max_risk_score:
            logger.warning(f"❌ Rejected: Risk score {risk_score} exceeds maximum {self.max_risk_score}")
            return False
        
        # Check protocol address
        protocol = decision.get('protocol')
        if not protocol or protocol == '0x0000000000000000000000000000000000000000':
            logger.warning("❌ Rejected: Invalid protocol address")
            return False
        
        logger.info(f"✅ Approved: Open {amount:.4f} BNB position at {apy:.2f}% APY (risk: {risk_score:.1f}/10)")
        return True
    
    def _approve_close_position(self, decision: Dict) -> bool:
        """Approve closing a position"""
        
        position_id = decision.get('position_id')
        reason = decision.get('reason', 'No reason provided')
        
        if position_id is None:
            logger.warning("❌ Rejected: No position ID provided")
            return False
        
        logger.info(f"✅ Approved: Close position {position_id} - {reason}")
        return True
    
    def _approve_rebalance(self, decision: Dict) -> bool:
        """Approve rebalancing"""
        
        from_position = decision.get('from_position_id')
        to_protocol = decision.get('to_protocol')
        to_apy = decision.get('to_apy', 0)
        risk_score = decision.get('risk_score', 10)
        
        if from_position is None:
            logger.warning("❌ Rejected: No source position specified")
            return False
        
        if not to_protocol:
            logger.warning("❌ Rejected: No target protocol specified")
            return False
        
        # Check target APY
        if to_apy < self.min_apy:
            logger.warning(f"❌ Rejected: Target APY {to_apy}% below minimum {self.min_apy}%")
            return False
        
        # Check target risk
        if risk_score > self.max_risk_score:
            logger.warning(f"❌ Rejected: Target risk score {risk_score} exceeds maximum {self.max_risk_score}")
            return False
        
        logger.info(f"✅ Approved: Rebalance from position {from_position} to {to_apy:.2f}% APY")
        return True
    
    def calculate_risk_score(self, opportunity: Dict) -> float:
        """
        Calculate risk score for an opportunity (0-10, lower is better)
        
        Factors:
        - Contract age (older = lower risk)
        - TVL (higher = lower risk)
        - APY (extremely high = higher risk)
        - Protocol reputation
        """
        risk_score = 5.0  # Start neutral
        
        # Contract age factor
        age_days = opportunity.get('contract_age_days', 0)
        if age_days > 365:
            risk_score -= 2.0  # Very mature
        elif age_days > 180:
            risk_score -= 1.0  # Mature
        elif age_days < 30:
            risk_score += 2.0  # Very new
        elif age_days < 90:
            risk_score += 1.0  # New
        
        # TVL factor
        tvl = opportunity.get('tvl', 0)
        if tvl > 100_000_000:  # $100M+
            risk_score -= 1.5  # Very high TVL
        elif tvl > 10_000_000:  # $10M+
            risk_score -= 0.5  # High TVL
        elif tvl < 100_000:  # $100k
            risk_score += 1.5  # Low TVL
        
        # APY factor (too good to be true?)
        apy = opportunity.get('apy', 0)
        if apy > 100:
            risk_score += 3.0  # Extremely high - likely unsustainable
        elif apy > 50:
            risk_score += 1.5  # Very high
        elif apy > 30:
            risk_score += 0.5  # High but reasonable
        
        # Protocol reputation
        protocol = opportunity.get('protocol', '').lower()
        if any(name in protocol for name in ['pancakeswap', 'venus', 'thena']):
            risk_score -= 1.0  # Known protocols
        
        # Clamp to 0-10 range
        risk_score = max(0.0, min(10.0, risk_score))
        
        return round(risk_score, 1)