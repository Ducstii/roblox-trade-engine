import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime
from models.data_models import RobloxItem, DemandTier

logger = logging.getLogger(__name__)

class UnderpricingFinder:
    """Finds undervalued items with high potential for profit"""
    
    def __init__(self):
        self.undervaluation_threshold = 0.1  # 10% below RAP
        self.min_demand_threshold = DemandTier.MEDIUM
        self.max_risk_threshold = 0.7
        
    def find_undervalued_items(self, items: List[RobloxItem]) -> List[RobloxItem]:
        """Find items that are undervalued relative to their potential"""
        try:
            logger.info("Finding undervalued items...")
            
            undervalued_items = []
            
            for item in items:
                undervaluation_score = self._calculate_undervaluation_score(item)
                
                if undervaluation_score > 0.6:  # High undervaluation threshold
                    item.momentum_score = undervaluation_score
                    undervalued_items.append(item)
            
            # Sort by undervaluation score
            undervalued_items.sort(key=lambda x: x.momentum_score, reverse=True)
            
            logger.info(f"Found {len(undervalued_items)} undervalued items")
            return undervalued_items
            
        except Exception as e:
            logger.error(f"Error finding undervalued items: {e}")
            return []
    
    def _calculate_undervaluation_score(self, item: RobloxItem) -> float:
        """Calculate how undervalued an item is"""
        try:
            score = 0.0
            
            # RAP vs current value comparison
            if item.rap > 0 and item.value > 0:
                rap_ratio = item.value / item.rap
                
                if rap_ratio < 0.9:  # Trading below 90% of RAP
                    undervaluation = (0.9 - rap_ratio) / 0.9
                    score += min(undervaluation * 2, 0.4)  # Cap at 40% of score
                
                # Bonus for significant undervaluation
                if rap_ratio < 0.8:  # Trading below 80% of RAP
                    score += 0.2
            
            # Projected value vs current value
            if item.projected > item.value and item.value > 0:
                projection_ratio = item.projected / item.value
                if projection_ratio > 1.1:  # 10%+ upside potential
                    upside = (projection_ratio - 1.0) * 2
                    score += min(upside, 0.3)  # Cap at 30% of score
            
            # Demand factor - high demand items shouldn't be undervalued
            demand_scores = {
                DemandTier.NONE: 0.0,
                DemandTier.LOW: 0.1,
                DemandTier.MEDIUM: 0.3,
                DemandTier.HIGH: 0.5,
                DemandTier.VERY_HIGH: 0.7
            }
            demand_score = demand_scores.get(item.demand, 0.0)
            score += demand_score * 0.2
            
            # Volume factor - sufficient liquidity
            if item.volume > 50:  # Minimum volume for liquidity
                volume_score = min(item.volume / 500.0, 1.0)
                score += volume_score * 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating undervaluation score for item {item.id}: {e}")
            return 0.0
    
    def find_arbitrage_opportunities(self, items: List[RobloxItem]) -> List[Tuple[RobloxItem, RobloxItem, float]]:
        """Find arbitrage opportunities between items"""
        try:
            logger.info("Finding arbitrage opportunities...")
            
            opportunities = []
            
            # Sort items by value for efficient comparison
            sorted_items = sorted(items, key=lambda x: x.value)
            
            for i, item1 in enumerate(sorted_items):
                for j, item2 in enumerate(sorted_items[i+1:], i+1):
                    if item1.id == item2.id:
                        continue
                    
                    arbitrage_score = self._calculate_arbitrage_score(item1, item2)
                    
                    if arbitrage_score > 0.7:  # High arbitrage threshold
                        opportunities.append((item1, item2, arbitrage_score))
            
            # Sort by arbitrage score
            opportunities.sort(key=lambda x: x[2], reverse=True)
            
            logger.info(f"Found {len(opportunities)} arbitrage opportunities")
            return opportunities[:20]  # Limit to top 20
            
        except Exception as e:
            logger.error(f"Error finding arbitrage opportunities: {e}")
            return []
    
    def _calculate_arbitrage_score(self, item1: RobloxItem, item2: RobloxItem) -> float:
        """Calculate arbitrage potential between two items"""
        try:
            score = 0.0
            
            # Value ratio analysis
            if item1.value > 0 and item2.value > 0:
                value_ratio = item1.value / item2.value
                
                # Look for items with similar value but different demand/volume
                if 0.8 <= value_ratio <= 1.2:  # Similar value range
                    score += 0.3
                    
                    # Demand differential
                    demand_diff = abs(self._demand_to_numeric(item1.demand) - self._demand_to_numeric(item2.demand))
                    if demand_diff >= 2:  # Significant demand difference
                        score += 0.3
                    
                    # Volume differential
                    volume_diff = abs(item1.volume - item2.volume)
                    if volume_diff > 200:  # Significant volume difference
                        score += 0.2
            
            # RAP differential
            if item1.rap > 0 and item2.rap > 0:
                rap_ratio = item1.rap / item2.rap
                if 0.7 <= rap_ratio <= 1.3:  # Similar RAP range
                    score += 0.2
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating arbitrage score: {e}")
            return 0.0
    
    def _demand_to_numeric(self, demand: DemandTier) -> int:
        """Convert demand tier to numeric value"""
        demand_map = {
            DemandTier.NONE: 0,
            DemandTier.LOW: 1,
            DemandTier.MEDIUM: 2,
            DemandTier.HIGH: 3,
            DemandTier.VERY_HIGH: 4
        }
        return demand_map.get(demand, 0)
    
    def find_value_traps(self, items: List[RobloxItem]) -> List[RobloxItem]:
        """Find items that appear undervalued but are actually value traps"""
        try:
            logger.info("Finding value traps...")
            
            value_traps = []
            
            for item in items:
                trap_score = self._calculate_trap_score(item)
                
                if trap_score > 0.7:  # High trap threshold
                    item.momentum_score = trap_score
                    value_traps.append(item)
            
            # Sort by trap score
            value_traps.sort(key=lambda x: x.momentum_score, reverse=True)
            
            logger.info(f"Found {len(value_traps)} potential value traps")
            return value_traps
            
        except Exception as e:
            logger.error(f"Error finding value traps: {e}")
            return []
    
    def _calculate_trap_score(self, item: RobloxItem) -> float:
        """Calculate how likely an item is to be a value trap"""
        try:
            score = 0.0
            
            # Low demand despite low price
            if item.demand in [DemandTier.NONE, DemandTier.LOW] and item.value < item.rap:
                score += 0.4
            
            # Very low volume (illiquid)
            if item.volume < 20:
                score += 0.3
            
            # Declining projected value
            if item.projected < item.value:
                score += 0.3
            
            # Not hyped or rare (no catalyst for recovery)
            if not item.hyped and not item.rare:
                score += 0.2
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating trap score: {e}")
            return 0.0
    
    def find_sleeping_giants(self, items: List[RobloxItem]) -> List[RobloxItem]:
        """Find items with high potential that are currently overlooked"""
        try:
            logger.info("Finding sleeping giants...")
            
            sleeping_giants = []
            
            for item in items:
                giant_score = self._calculate_giant_score(item)
                
                if giant_score > 0.6:  # High potential threshold
                    item.momentum_score = giant_score
                    sleeping_giants.append(item)
            
            # Sort by giant score
            sleeping_giants.sort(key=lambda x: x.momentum_score, reverse=True)
            
            logger.info(f"Found {len(sleeping_giants)} sleeping giants")
            return sleeping_giants
            
        except Exception as e:
            logger.error(f"Error finding sleeping giants: {e}")
            return []
    
    def _calculate_giant_score(self, item: RobloxItem) -> float:
        """Calculate sleeping giant potential"""
        try:
            score = 0.0
            
            # High demand but low volume (undiscovered)
            if item.demand in [DemandTier.HIGH, DemandTier.VERY_HIGH] and item.volume < 100:
                score += 0.4
            
            # Rare or premium items with low volume
            if (item.rare or item.premium) and item.volume < 200:
                score += 0.3
            
            # High projected value relative to current
            if item.projected > item.value * 1.2:  # 20%+ upside
                score += 0.3
            
            # Not currently hyped (room to grow)
            if not item.hyped:
                score += 0.2
            
            # Good value relative to RAP
            if item.value < item.rap * 0.95:  # Trading below RAP
                score += 0.2
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating giant score: {e}")
            return 0.0
    
    def get_undervaluation_summary(self, items: List[RobloxItem]) -> Dict[str, Any]:
        """Get summary of undervaluation analysis"""
        try:
            undervalued = self.find_undervalued_items(items)
            arbitrage_opps = self.find_arbitrage_opportunities(items)
            value_traps = self.find_value_traps(items)
            sleeping_giants = self.find_sleeping_giants(items)
            
            return {
                "undervalued_items": len(undervalued),
                "arbitrage_opportunities": len(arbitrage_opps),
                "value_traps": len(value_traps),
                "sleeping_giants": len(sleeping_giants),
                "top_undervalued": [item.name for item in undervalued[:5]],
                "top_arbitrage": [(item1.name, item2.name) for item1, item2, _ in arbitrage_opps[:5]],
                "top_traps": [item.name for item in value_traps[:5]],
                "top_giants": [item.name for item in sleeping_giants[:5]],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting undervaluation summary: {e}")
            return {} 