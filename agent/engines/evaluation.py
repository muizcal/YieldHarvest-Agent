"""
Evaluation Engine
Evaluates yield opportunities for risk and quality
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class EvaluationEngine:
    """
    Evaluates opportunities for risk and suitability
    """
    
    def __init__(self, config, blockchain):
        self.config = config
        self.blockchain = blockchain
    
    async def evaluate_opportunity(self, opportunity: Dict) -> Dict:
        """
        Evaluate an opportunity and return risk/quality metrics
        
        Args:
            opportunity: Dict with protocol, token, apy, tvl, etc.
            
        Returns:
            Dict with risk_score, confidence, and other metrics
        """
        logger.debug(f"Evaluating: {opportunity.get('token_symbol', 'Unknown')} ({opportunity.get('apy', 0):.2f}% APY)")
        
        risk_score = self._calculate_risk_score(opportunity)
        confidence = self._calculate_confidence(opportunity)
        quality_score = self._calculate_quality_score(opportunity)
        
        evaluation = {
            'risk_score': risk_score,
            'confidence': confidence,
            'quality_score': quality_score,
            'recommendation': self._get_recommendation(risk_score, confidence, quality_score)
        }
        
        logger.debug(f"   Risk: {risk_score:.1f}/10, Confidence: {confidence:.2f}, Quality: {quality_score:.1f}/10")
        
        return evaluation
    
    def _calculate_risk_score(self, opp: Dict) -> float:
        """
        Calculate risk score (0-10, lower is better)
        
        Factors:
        - Contract age
        - TVL
        - APY sustainability
        - Protocol reputation
        """
        risk = 5.0  # Start neutral
        
        # Contract age
        age_days = opp.get('contract_age_days', 0)
        if age_days > 365:
            risk -= 2.0  # Very mature
        elif age_days > 180:
            risk -= 1.0  # Mature
        elif age_days < 30:
            risk += 2.5  # Very new
        elif age_days < 90:
            risk += 1.0  # New
        
        # TVL (Total Value Locked)
        tvl = opp.get('tvl', 0)
        if tvl > 100_000_000:  # $100M+
            risk -= 1.5
        elif tvl > 50_000_000:  # $50M+
            risk -= 1.0
        elif tvl > 10_000_000:  # $10M+
            risk -= 0.5
        elif tvl < 1_000_000:  # $1M
            risk += 1.5
        elif tvl < 100_000:  # $100k
            risk += 2.5
        
        # APY sustainability check
        apy = opp.get('apy', 0)
        if apy > 200:
            risk += 4.0  # Extremely suspicious
        elif apy > 100:
            risk += 2.5  # Very high - likely unsustainable
        elif apy > 50:
            risk += 1.0  # High but possible
        elif apy < 3:
            risk += 0.5  # Too low to be worthwhile
        
        # Protocol reputation
        protocol = opp.get('protocol', '').lower()
        known_protocols = ['pancakeswap', 'venus', 'thena', 'uniswap', 'aave', 'compound']
        
        if any(name in protocol for name in known_protocols):
            risk -= 1.5  # Well-known protocols
        
        # Clamp to 0-10
        risk = max(0.0, min(10.0, risk))
        
        return round(risk, 1)
    
    def _calculate_confidence(self, opp: Dict) -> float:
        """
        Calculate confidence in the opportunity data (0-1)
        
        Higher confidence = more reliable data
        """
        confidence = 0.5  # Start at 50%
        
        # Data completeness
        required_fields = ['apy', 'tvl', 'protocol', 'token']
        present_fields = sum(1 for field in required_fields if field in opp and opp[field])
        confidence += (present_fields / len(required_fields)) * 0.3
        
        # TVL indicates real usage
        tvl = opp.get('tvl', 0)
        if tvl > 10_000_000:
            confidence += 0.15
        elif tvl > 1_000_000:
            confidence += 0.05
        
        # Contract age indicates stability
        age = opp.get('contract_age_days', 0)
        if age > 365:
            confidence += 0.1
        elif age > 180:
            confidence += 0.05
        
        # Known protocol increases confidence
        protocol = opp.get('protocol', '').lower()
        if any(name in protocol for name in ['pancakeswap', 'venus', 'thena']):
            confidence += 0.1
        
        return min(1.0, round(confidence, 2))
    
    def _calculate_quality_score(self, opp: Dict) -> float:
        """
        Calculate overall quality score (0-10, higher is better)
        
        Combines APY, safety, and reliability
        """
        quality = 5.0
        
        # APY contribution (but not too high)
        apy = opp.get('apy', 0)
        if 10 <= apy <= 30:
            quality += 2.0  # Sweet spot
        elif 5 <= apy < 10:
            quality += 1.0  # Decent
        elif 30 < apy <= 50:
            quality += 1.0  # Good but risky
        elif apy > 100:
            quality -= 2.0  # Too good to be true
        
        # TVL contribution
        tvl = opp.get('tvl', 0)
        if tvl > 50_000_000:
            quality += 1.5
        elif tvl > 10_000_000:
            quality += 1.0
        elif tvl < 100_000:
            quality -= 1.0
        
        # Stability (age)
        age = opp.get('contract_age_days', 0)
        if age > 365:
            quality += 1.0
        elif age < 30:
            quality -= 1.0
        
        return max(0.0, min(10.0, round(quality, 1)))
    
    def _get_recommendation(self, risk: float, confidence: float, quality: float) -> str:
        """Get a recommendation string"""
        
        if risk <= 3 and confidence >= 0.7 and quality >= 7:
            return "STRONG_BUY"
        elif risk <= 5 and confidence >= 0.6 and quality >= 6:
            return "BUY"
        elif risk <= 7:
            return "HOLD"
        else:
            return "AVOID"