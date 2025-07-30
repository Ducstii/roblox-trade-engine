import logging
from typing import List, Dict, Any
from models.data_models import RobloxItem, DemandTier, StrategyMode
from config.config_manager import config_manager

logger = logging.getLogger(__name__)

class ScoreEngine:
    """Engine for scoring Roblox items based on various metrics"""
    
    def __init__(self):
        self.weights = config_manager.get_scoring_weights()
        self.strategy_mode = config_manager.get_strategy_mode()
        
    def calculate_score(self, item: RobloxItem) -> float:
        """Calculate weighted score for an item"""
        try:
            # Calculate individual component scores
            roi_score = self._calculate_roi_score(item)
            demand_score = self._calculate_demand_score(item)
            volume_score = self._calculate_volume_score(item)
            volatility_score = self._calculate_volatility_score(item)
            engagement_score = self._calculate_engagement_score(item)
            trait_score = self._calculate_trait_score(item)
            
            # Apply strategy mode adjustments
            strategy_adjustment = self._apply_strategy_adjustment(item)
            
            # Calculate weighted score
            weighted_score = (
                roi_score * self.weights.roi_weight +
                demand_score * self.weights.demand_weight +
                volume_score * self.weights.volume_weight +
                volatility_score * self.weights.volatility_weight +
                engagement_score * self.weights.engagement_weight +
                trait_score * self.weights.trait_weight
            ) * strategy_adjustment
            
            # Update item with calculated scores
            item.roi = roi_score
            item.volatility = volatility_score
            item.engagement_score = engagement_score
            item.trait_score = trait_score
            
            return weighted_score
            
        except Exception as e:
            logger.error(f"Error calculating score for item {item.id}: {e}")
            return 0.0
    
    def _calculate_roi_score(self, item: RobloxItem) -> float:
        """Calculate ROI score based on projected vs current value"""
        try:
            if item.value <= 0:
                return 0.0
            
            # Calculate ROI percentage
            roi_percentage = ((item.projected - item.value) / item.value) * 100
            
            # Normalize to 0-1 scale (cap at 50% ROI for scoring)
            roi_score = min(roi_percentage / 50.0, 1.0)
            
            return max(roi_score, 0.0)
            
        except Exception as e:
            logger.error(f"Error calculating ROI score: {e}")
            return 0.0
    
    def _calculate_demand_score(self, item: RobloxItem) -> float:
        """Calculate demand score based on demand tier"""
        demand_scores = {
            DemandTier.NONE: 0.0,
            DemandTier.LOW: 0.2,
            DemandTier.MEDIUM: 0.5,
            DemandTier.HIGH: 0.8,
            DemandTier.VERY_HIGH: 1.0
        }
        
        return demand_scores.get(item.demand, 0.0)
    
    def _calculate_volume_score(self, item: RobloxItem) -> float:
        """Calculate volume score based on trade volume"""
        try:
            # Normalize volume (assume 1000+ trades per day is max)
            volume_score = min(item.volume / 1000.0, 1.0)
            
            return volume_score
            
        except Exception as e:
            logger.error(f"Error calculating volume score: {e}")
            return 0.0
    
    def _calculate_volatility_score(self, item: RobloxItem) -> float:
        """Calculate volatility score (higher volatility = higher risk/reward)"""
        try:
            # This would ideally use historical price data
            # For now, use a simple heuristic based on RAP vs value
            if item.rap <= 0:
                return 0.5  # Default moderate volatility
            
            volatility_ratio = abs(item.value - item.rap) / item.rap
            
            # Normalize to 0-1 scale
            volatility_score = min(volatility_ratio, 1.0)
            
            return volatility_score
            
        except Exception as e:
            logger.error(f"Error calculating volatility score: {e}")
            return 0.5
    
    def _calculate_engagement_score(self, item: RobloxItem) -> float:
        """Calculate engagement score based on social metrics"""
        try:
            # This would ideally use social media data
            # For now, use item properties as proxies
            
            score = 0.0
            
            # Premium items get bonus
            if item.premium:
                score += 0.3
            
            # Hyped items get bonus
            if item.hyped:
                score += 0.4
            
            # Rare items get bonus
            if item.rare:
                score += 0.3
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating engagement score: {e}")
            return 0.0
    
    def _calculate_trait_score(self, item: RobloxItem) -> float:
        """Calculate trait-based score"""
        try:
            score = 0.0
            
            # Category-based scoring
            high_value_categories = ["hats", "faces", "accessories", "limiteds"]
            if item.category.lower() in high_value_categories:
                score += 0.4
            
            # Rarity bonus
            if item.rare:
                score += 0.3
            
            # Premium bonus
            if item.premium:
                score += 0.3
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating trait score: {e}")
            return 0.0
    
    def _apply_strategy_adjustment(self, item: RobloxItem) -> float:
        """Apply strategy-specific adjustments to the score"""
        try:
            if self.strategy_mode == StrategyMode.SNIPER:
                # Sniper mode favors undervalued items
                if item.value < item.rap:
                    return 1.2  # Boost undervalued items
                else:
                    return 0.8  # Penalize overvalued items
                    
            elif self.strategy_mode == StrategyMode.AGGRESSIVE:
                # Aggressive mode favors high-volume, trending items
                if item.hyped and item.volume > 100:
                    return 1.3  # Boost trending items
                else:
                    return 0.9
                    
            elif self.strategy_mode == StrategyMode.CONSERVATIVE:
                # Conservative mode favors stable, established items
                if item.demand in [DemandTier.HIGH, DemandTier.VERY_HIGH] and not item.hyped:
                    return 1.1  # Boost stable items
                else:
                    return 0.9
                    
            elif self.strategy_mode == StrategyMode.MOMENTUM:
                # Momentum mode favors items with recent price increases
                if item.projected > item.value:
                    return 1.2  # Boost rising items
                else:
                    return 0.8  # Penalize falling items
            
            return 1.0  # Default no adjustment
            
        except Exception as e:
            logger.error(f"Error applying strategy adjustment: {e}")
            return 1.0
    
    def score_items(self, items: List[RobloxItem]) -> List[RobloxItem]:
        """Score a list of items and return them sorted by score"""
        try:
            logger.info(f"Scoring {len(items)} items...")
            
            # Calculate scores for all items
            for item in items:
                item.momentum_score = self.calculate_score(item)
            
            # Sort by score (highest first)
            scored_items = sorted(items, key=lambda x: x.momentum_score, reverse=True)
            
            logger.info(f"Scoring completed. Top score: {scored_items[0].momentum_score if scored_items else 0}")
            
            return scored_items
            
        except Exception as e:
            logger.error(f"Error scoring items: {e}")
            return items
    
    def get_top_picks(self, items: List[RobloxItem], limit: int = 10) -> List[RobloxItem]:
        """Get top scored items"""
        scored_items = self.score_items(items)
        return scored_items[:limit]
    
    def update_weights(self, new_weights):
        """Update scoring weights"""
        self.weights = new_weights
    
    def update_strategy_mode(self, mode: str):
        """Update strategy mode"""
        self.strategy_mode = mode 