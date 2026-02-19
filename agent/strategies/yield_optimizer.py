"""
Yield Optimizer
AI-powered portfolio optimization for yield farming
"""

import logging
from typing import List, Dict
from web3 import Web3

logger = logging.getLogger(__name__)


class YieldOptimizer:
    """
    Optimizes portfolio allocation across yield opportunities
    """
    
    def __init__(self, config):
        self.config = config
    
    async def optimize_portfolio(self, opportunities: List[Dict], positions: List[Dict]) -> List[Dict]:
        """
        Decide which opportunities to pursue based on current portfolio
        
        Args:
            opportunities: List of evaluated opportunities
            positions: List of current positions
            
        Returns:
            List of decisions (actions to take)
        """
        logger.info("🤖 AI Optimizer analyzing portfolio...")
        
        decisions = []
        
        # Calculate available capital
        active_positions = [p for p in positions if p.get('amount', 0) > 0]
        total_allocated = sum(p.get('amount', 0) for p in active_positions)
        
        # Get vault balance from config (assuming we have it)
        # For now, use a fixed amount based on vault balance
        available_capital = 0.003  # 0.003 BNB from your vault
        
        logger.info(f"Available capital: {available_capital} BNB")
        logger.info(f"Current positions: {len(active_positions)}")
        logger.info(f"Opportunities to evaluate: {len(opportunities)}")
        
        # If no positions yet, open initial positions
        if len(active_positions) == 0:
            logger.info("No current positions - selecting initial allocations...")
            
            # Sort opportunities by APY (highest first)
            sorted_opps = sorted(opportunities, key=lambda x: x['apy'], reverse=True)
            
            # Take top 3 opportunities
            top_opportunities = sorted_opps[:3]
            
            # Allocate capital across top opportunities
            allocation_per_opp = available_capital / len(top_opportunities)
            
            for opp in top_opportunities:
                # Only allocate if amount is meaningful (at least 0.0005 BNB)
                if allocation_per_opp >= 0.0005:
                    decisions.append({
                        'action': 'OPEN_POSITION',
                        'protocol': opp['protocol_address'],
                        'token': opp['token'],
                        'amount': allocation_per_opp,
                        'apy': opp['apy'],
                        'risk_score': opp['score']['risk_score'],
                        'reason': f"Initial allocation: {opp['token_symbol']} offers {opp['apy']:.2f}% APY with risk score {opp['score']['risk_score']:.1f}/10"
                    })
                    
                    logger.info(f"Decision: Open {opp['token_symbol']} position with {allocation_per_opp:.4f} BNB")
        
        else:
            logger.info("Portfolio already has positions - checking for better opportunities...")
            
            # Calculate average APY of current positions
            current_avg_apy = sum(p.get('entry_apy', 0) for p in active_positions) / len(active_positions)
            
            # Find opportunities significantly better than current average
            better_opportunities = [
                opp for opp in opportunities
                if opp['apy'] > current_avg_apy * (1 + self.config.rebalance_threshold / 100)
            ]
            
            if better_opportunities:
                logger.info(f"Found {len(better_opportunities)} opportunities better than current {current_avg_apy:.2f}% APY")
                
                # Sort by APY
                sorted_better = sorted(better_opportunities, key=lambda x: x['apy'], reverse=True)
                best = sorted_better[0]
                
                # Check if we have available capital to add position
                if available_capital > 0.001:
                    decisions.append({
                        'action': 'OPEN_POSITION',
                        'protocol': best['protocol_address'],
                        'token': best['token'],
                        'amount': min(available_capital * 0.5, 0.002),  # Use up to half or 0.002 BNB
                        'apy': best['apy'],
                        'risk_score': best['score']['risk_score'],
                        'reason': f"Better opportunity: {best['token_symbol']} offers {best['apy']:.2f}% vs current {current_avg_apy:.2f}%"
                    })
                    
                    logger.info(f"Decision: Add {best['token_symbol']} position (better APY)")
            else:
                logger.info("No significantly better opportunities found - holding current positions")
        
        logger.info(f"✅ Generated {len(decisions)} decisions")
        
        return decisions
    
    async def check_rebalancing(self, positions: List[Dict], opportunities: List[Dict], threshold: float) -> List[Dict]:
        """
        Check if portfolio should be rebalanced
        
        Args:
            positions: Current active positions
            opportunities: Available opportunities
            threshold: Minimum improvement threshold (%)
            
        Returns:
            List of rebalancing decisions
        """
        logger.info("⚖️ Checking for rebalancing opportunities...")
        
        decisions = []
        
        if not positions or not opportunities:
            return decisions
        
        # Find worst performing position
        worst_position = min(positions, key=lambda p: p.get('entry_apy', 0))
        worst_apy = worst_position.get('entry_apy', 0) / 100  # Convert basis points to percentage
        
        # Find best opportunity
        best_opportunity = max(opportunities, key=lambda o: o['apy'])
        best_apy = best_opportunity['apy']
        
        # Calculate improvement
        improvement = ((best_apy - worst_apy) / worst_apy) * 100 if worst_apy > 0 else 0
        
        logger.info(f"Worst position APY: {worst_apy:.2f}%")
        logger.info(f"Best opportunity APY: {best_apy:.2f}%")
        logger.info(f"Potential improvement: {improvement:.2f}%")
        
        # If improvement is significant, rebalance
        if improvement >= threshold:
            decisions.append({
                'action': 'REBALANCE',
                'from_position_id': worst_position['id'],
                'to_protocol': best_opportunity['protocol_address'],
                'to_token': best_opportunity['token'],
                'to_apy': best_opportunity['apy'],
                'risk_score': best_opportunity['score']['risk_score'],
                'reason': f"Rebalancing: Moving from {worst_apy:.2f}% to {best_apy:.2f}% APY ({improvement:.1f}% improvement)"
            })
            
            logger.info(f"✅ Rebalancing recommended: {improvement:.1f}% improvement")
        else:
            logger.info("No rebalancing needed - improvement below threshold")
        
        return decisions