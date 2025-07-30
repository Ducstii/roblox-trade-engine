import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from models.data_models import RobloxItem, DemandTier

logger = logging.getLogger(__name__)
,

class MomentumDetector:
    """Detects momentum and trending patterns in Roblox items"""
    
    def __init__(self):
        self.momentum_threshold = 0.15  # 15% price increase threshold
        self.volume_threshold = 200     # Minimum volume for momentum
        self.trending_days = 7          # Days to look back for trends
        
    def detect_momentum_items(self, items: List[RobloxItem], historical_data: Dict[int, List] = None) -> List[RobloxItem]:
        """Detect items with positive momentum"""
        try:
            logger.info("Detecting momentum items...")
            
            momentum_items = []
            
            for item in items:
                momentum_score = self._calculate_momentum_score(item, historical_data)
                
                if momentum_score > 0.6:  # High momentum threshold
                    item.momentum_score = momentum_score
                    momentum_items.append(item)
            
            # Sort by momentum score
            momentum_items.sort(key=lambda x: x.momentum_score, reverse=True)
            
            logger.info(f"Found {len(momentum_items)} items with momentum")
            return momentum_items
            
        except Exception as e:
            logger.error(f"Error detecting momentum items: {e}")
            return []
    
    def _calculate_momentum_score(self, item: RobloxItem, historical_data: Dict[int, List] = None) -> float:
        """Calculate momentum score for an item"""
        try:
            score = 0.0
            
            # Price momentum (projected vs current)
            if item.value > 0 and item.projected > item.value:
                price_momentum = (item.projected - item.value) / item.value
                score += min(price_momentum * 2, 0.4)  # Cap at 40% of score
            
            # Volume momentum
            if item.volume > self.volume_threshold:
                volume_score = min(item.volume / 1000.0, 1.0)
                score += volume_score * 0.2
            
            # Demand momentum
            demand_scores = {
                DemandTier.NONE: 0.0,
                DemandTier.LOW: 0.1,
                DemandTier.MEDIUM: 0.3,
                DemandTier.HIGH: 0.5,
                DemandTier.VERY_HIGH: 0.7
            }
            score += demand_scores.get(item.demand, 0.0) * 0.2
            
            # Hype momentum
            if item.hyped:
                score += 0.2
            
            # Historical momentum (if data available)
            if historical_data and item.id in historical_data:
                hist_score = self._calculate_historical_momentum(item.id, historical_data[item.id])
                score += hist_score * 0.2
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating momentum score for item {item.id}: {e}")
            return 0.0
    
    def _calculate_historical_momentum(self, item_id: int, history: List[Dict]) -> float:
        """Calculate momentum based on historical price data"""
        try:
            if len(history) < 2:
                return 0.0
            
            # Sort by date (assuming history has 'date' and 'value' fields)
            sorted_history = sorted(history, key=lambda x: x.get('date', 0))
            
            if len(sorted_history) < 2:
                return 0.0
            
            # Calculate price change over the last few days
            recent_prices = sorted_history[-min(7, len(sorted_history)):]
            
            if len(recent_prices) < 2:
                return 0.0
            
            # Calculate average price change
            price_changes = []
            for i in range(1, len(recent_prices)):
                prev_price = recent_prices[i-1].get('value', 0)
                curr_price = recent_prices[i].get('value', 0)
                
                if prev_price > 0:
                    change = (curr_price - prev_price) / prev_price
                    price_changes.append(change)
            
            if not price_changes:
                return 0.0
            
            # Calculate momentum as average positive changes
            positive_changes = [c for c in price_changes if c > 0]
            if positive_changes:
                avg_momentum = sum(positive_changes) / len(positive_changes)
                return min(avg_momentum, 1.0)
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating historical momentum: {e}")
            return 0.0
    
    def detect_trending_items(self, items: List[RobloxItem]) -> List[RobloxItem]:
        """Detect items that are currently trending"""
        try:
            logger.info("Detecting trending items...")
            
            trending_items = []
            
            for item in items:
                trending_score = self._calculate_trending_score(item)
                
                if trending_score > 0.7:  # High trending threshold
                    item.momentum_score = trending_score
                    trending_items.append(item)
            
            # Sort by trending score
            trending_items.sort(key=lambda x: x.momentum_score, reverse=True)
            
            logger.info(f"Found {len(trending_items)} trending items")
            return trending_items
            
        except Exception as e:
            logger.error(f"Error detecting trending items: {e}")
            return []
    
    def _calculate_trending_score(self, item: RobloxItem) -> float:
        """Calculate trending score for an item"""
        try:
            score = 0.0
            
            # High volume indicates trending
            if item.volume > 500:
                score += 0.3
            elif item.volume > 200:
                score += 0.2
            
            # High demand indicates trending
            if item.demand in [DemandTier.HIGH, DemandTier.VERY_HIGH]:
                score += 0.3
            
            # Hype status indicates trending
            if item.hyped:
                score += 0.4
            
            # Premium items trend more
            if item.premium:
                score += 0.1
            
            # Rare items trend more
            if item.rare:
                score += 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating trending score: {e}")
            return 0.0
    
    def detect_reversal_signals(self, items: List[RobloxItem], historical_data: Dict[int, List] = None) -> List[RobloxItem]:
        """Detect items showing reversal signals (potential bounce-backs)"""
        try:
            logger.info("Detecting reversal signals...")
            
            reversal_items = []
            
            for item in items:
                reversal_score = self._calculate_reversal_score(item, historical_data)
                
                if reversal_score > 0.6:  # High reversal threshold
                    item.momentum_score = reversal_score
                    reversal_items.append(item)
            
            # Sort by reversal score
            reversal_items.sort(key=lambda x: x.momentum_score, reverse=True)
            
            logger.info(f"Found {len(reversal_items)} items with reversal signals")
            return reversal_items
            
        except Exception as e:
            logger.error(f"Error detecting reversal signals: {e}")
            return []
    
    def _calculate_reversal_score(self, item: RobloxItem, historical_data: Dict[int, List] = None) -> float:
        """Calculate reversal score for an item"""
        try:
            score = 0.0
            
            # Items trading below RAP might be undervalued
            if item.value < item.rap and item.rap > 0:
                undervaluation = (item.rap - item.value) / item.rap
                score += min(undervaluation, 0.3)
            
            # High demand despite low price suggests reversal potential
            if item.demand in [DemandTier.HIGH, DemandTier.VERY_HIGH] and item.value < item.rap:
                score += 0.3
            
            # Increasing volume suggests reversal
            if item.volume > 300:
                score += 0.2
            
            # Historical reversal patterns (if data available)
            if historical_data and item.id in historical_data:
                hist_reversal = self._detect_historical_reversal(item.id, historical_data[item.id])
                score += hist_reversal * 0.2
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating reversal score: {e}")
            return 0.0
    
    def _detect_historical_reversal(self, item_id: int, history: List[Dict]) -> float:
        """Detect historical reversal patterns"""
        try:
            if len(history) < 5:
                return 0.0
            
            # Sort by date
            sorted_history = sorted(history, key=lambda x: x.get('date', 0))
            
            # Look for V-shaped patterns (decline followed by recovery)
            prices = [h.get('value', 0) for h in sorted_history]
            
            if len(prices) < 5:
                return 0.0
            
            # Check if recent prices are higher than recent lows
            recent_prices = prices[-5:]
            min_price = min(recent_prices)
            current_price = recent_prices[-1]
            
            if current_price > min_price and min_price > 0:
                recovery_ratio = (current_price - min_price) / min_price
                return min(recovery_ratio, 1.0)
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error detecting historical reversal: {e}")
            return 0.0
    
    def get_momentum_summary(self, items: List[RobloxItem]) -> Dict[str, Any]:
        """Get summary of momentum analysis"""
        try:
            momentum_items = self.detect_momentum_items(items)
            trending_items = self.detect_trending_items(items)
            reversal_items = self.detect_reversal_signals(items)
            
            return {
                "momentum_items": len(momentum_items),
                "trending_items": len(trending_items),
                "reversal_items": len(reversal_items),
                "top_momentum": [item.name for item in momentum_items[:5]],
                "top_trending": [item.name for item in trending_items[:5]],
                "top_reversals": [item.name for item in reversal_items[:5]],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting momentum summary: {e}")
            return {} 