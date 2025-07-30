import logging
import random
from typing import List, Dict, Any, Tuple
from datetime import datetime
from models.data_models import RobloxItem, TradeCombo, StrategyMode
from config.config_manager import config_manager

logger = logging.getLogger(__name__)

class TradeSimulator:
    """Simulator for generating and evaluating trade combinations"""
    
    def __init__(self):
        self.min_combo_value = 1000  # Minimum total value for a combo
        self.max_combo_items = 4     # Maximum items per side of trade
        self.confidence_threshold = 0.7
        
    def generate_trade_combos(self, items: List[RobloxItem], limit: int = 10) -> List[TradeCombo]:
        """Generate trade combinations from scored items"""
        try:
            logger.info(f"Generating trade combos from {len(items)} items...")
            
            combos = []
            attempts = 0
            max_attempts = limit * 10  # Prevent infinite loops
            
            while len(combos) < limit and attempts < max_attempts:
                attempts += 1
                
                # Generate a random combo
                combo = self._generate_single_combo(items)
                
                if combo and self._validate_combo(combo):
                    combos.append(combo)
            
            # Sort by projected gain
            combos.sort(key=lambda x: x.projected_gain, reverse=True)
            
            logger.info(f"Generated {len(combos)} valid trade combos")
            return combos[:limit]
            
        except Exception as e:
            logger.error(f"Error generating trade combos: {e}")
            return []
    
    def _generate_single_combo(self, items: List[RobloxItem]) -> TradeCombo:
        """Generate a single trade combination"""
        try:
            # Filter items by minimum value
            valuable_items = [item for item in items if item.value >= 100]
            
            if len(valuable_items) < 2:
                return None
            
            # Randomly select items for each side
            offered_count = random.randint(1, min(self.max_combo_items, len(valuable_items) // 2))
            requested_count = random.randint(1, min(self.max_combo_items, len(valuable_items) // 2))
            
            offered_items = random.sample(valuable_items, offered_count)
            remaining_items = [item for item in valuable_items if item not in offered_items]
            requested_items = random.sample(remaining_items, requested_count)
            
            # Calculate combo metrics
            total_offered = sum(item.value for item in offered_items)
            total_requested = sum(item.value for item in requested_items)
            projected_gain = total_requested - total_offered
            
            # Calculate confidence based on various factors
            confidence = self._calculate_combo_confidence(offered_items, requested_items)
            
            # Calculate risk level
            risk_level = self._calculate_risk_level(offered_items, requested_items, projected_gain)
            
            # Generate combo ID
            combo_id = f"combo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(offered_items)}_{len(requested_items)}"
            
            return TradeCombo(
                id=combo_id,
                items_offered=offered_items,
                items_requested=requested_items,
                projected_gain=projected_gain,
                confidence=confidence,
                risk_level=risk_level,
                strategy_used=StrategyMode(config_manager.get_strategy_mode()),
                total_value_offered=total_offered,
                total_value_requested=total_requested,
                roi_percentage=(projected_gain / total_offered * 100) if total_offered > 0 else 0,
                volume_score=self._calculate_volume_score(offered_items + requested_items),
                demand_score=self._calculate_demand_score(offered_items + requested_items)
            )
            
        except Exception as e:
            logger.error(f"Error generating single combo: {e}")
            return None
    
    def _validate_combo(self, combo: TradeCombo) -> bool:
        """Validate if a combo meets minimum criteria"""
        try:
            # Check minimum value
            if combo.total_value_offered < self.min_combo_value:
                return False
            
            # Check for positive gain
            if combo.projected_gain <= 0:
                return False
            
            # Check confidence threshold
            if combo.confidence < self.confidence_threshold:
                return False
            
            # Check for reasonable item counts
            if len(combo.items_offered) == 0 or len(combo.items_requested) == 0:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating combo: {e}")
            return False
    
    def _calculate_combo_confidence(self, offered: List[RobloxItem], requested: List[RobloxItem]) -> float:
        """Calculate confidence score for a trade combo"""
        try:
            confidence = 0.5  # Base confidence
            
            # Volume factor
            avg_volume = sum(item.volume for item in offered + requested) / len(offered + requested)
            if avg_volume > 500:
                confidence += 0.2
            elif avg_volume > 100:
                confidence += 0.1
            
            # Demand factor
            high_demand_items = [item for item in requested if item.demand.value in ['high', 'very_high']]
            demand_ratio = len(high_demand_items) / len(requested) if requested else 0
            confidence += demand_ratio * 0.2
            
            # Value balance factor
            total_offered = sum(item.value for item in offered)
            total_requested = sum(item.value for item in requested)
            if total_offered > 0:
                value_ratio = total_requested / total_offered
                if 1.1 <= value_ratio <= 1.5:  # Sweet spot for value ratio
                    confidence += 0.1
            
            # Rarity factor
            rare_items = [item for item in requested if item.rare]
            if rare_items:
                confidence += 0.1
            
            return min(confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating combo confidence: {e}")
            return 0.5
    
    def _calculate_risk_level(self, offered: List[RobloxItem], requested: List[RobloxItem], gain: int) -> str:
        """Calculate risk level for a trade combo"""
        try:
            total_offered = sum(item.value for item in offered)
            
            if total_offered == 0:
                return "Unknown"
            
            # Calculate risk based on gain percentage and item characteristics
            gain_percentage = (gain / total_offered) * 100
            
            # High volatility items increase risk
            volatile_items = [item for item in offered + requested if item.volatility > 0.7]
            volatility_penalty = len(volatile_items) * 0.1
            
            # Low volume items increase risk
            low_volume_items = [item for item in offered + requested if item.volume < 50]
            volume_penalty = len(low_volume_items) * 0.05
            
            risk_score = 0.5  # Base risk
            
            if gain_percentage > 30:
                risk_score += 0.3
            elif gain_percentage > 20:
                risk_score += 0.2
            elif gain_percentage > 10:
                risk_score += 0.1
            
            risk_score += volatility_penalty + volume_penalty
            
            # Categorize risk
            if risk_score < 0.3:
                return "Low"
            elif risk_score < 0.6:
                return "Medium"
            elif risk_score < 0.8:
                return "High"
            else:
                return "Very High"
                
        except Exception as e:
            logger.error(f"Error calculating risk level: {e}")
            return "Unknown"
    
    def _calculate_volume_score(self, items: List[RobloxItem]) -> float:
        """Calculate volume-based score for items"""
        try:
            if not items:
                return 0.0
            
            total_volume = sum(item.volume for item in items)
            avg_volume = total_volume / len(items)
            
            # Normalize to 0-1 scale
            return min(avg_volume / 1000.0, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating volume score: {e}")
            return 0.0
    
    def _calculate_demand_score(self, items: List[RobloxItem]) -> float:
        """Calculate demand-based score for items"""
        try:
            if not items:
                return 0.0
            
            demand_scores = {
                'none': 0.0,
                'low': 0.2,
                'medium': 0.5,
                'high': 0.8,
                'very_high': 1.0
            }
            
            total_demand_score = sum(demand_scores.get(item.demand.value, 0.0) for item in items)
            avg_demand_score = total_demand_score / len(items)
            
            return avg_demand_score
            
        except Exception as e:
            logger.error(f"Error calculating demand score: {e}")
            return 0.0
    
    def filter_combos_by_threshold(self, combos: List[TradeCombo], min_gain: int, min_confidence: float) -> List[TradeCombo]:
        """Filter combos by gain and confidence thresholds"""
        try:
            filtered = [
                combo for combo in combos
                if combo.projected_gain >= min_gain and combo.confidence >= min_confidence
            ]
            
            logger.info(f"Filtered {len(combos)} combos to {len(filtered)} based on thresholds")
            return filtered
            
        except Exception as e:
            logger.error(f"Error filtering combos: {e}")
            return combos
    
    def get_best_combos(self, items: List[RobloxItem], limit: int = 5, min_gain: int = 1000) -> List[TradeCombo]:
        """Get the best trade combinations"""
        try:
            # Generate combos
            combos = self.generate_trade_combos(items, limit * 2)
            
            # Filter by thresholds
            filtered_combos = self.filter_combos_by_threshold(combos, min_gain, self.confidence_threshold)
            
            # Return top results
            return filtered_combos[:limit]
            
        except Exception as e:
            logger.error(f"Error getting best combos: {e}")
            return [] 