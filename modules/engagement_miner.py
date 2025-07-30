import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from models.data_models import RobloxItem, DemandTier

logger = logging.getLogger(__name__)

class EngagementMiner:
    """Mines social engagement and sentiment data for items"""
    
    def __init__(self):
        self.sentiment_keywords = {
            "positive": ["amazing", "awesome", "best", "love", "great", "perfect", "wow", "incredible", "beautiful", "stunning"],
            "negative": ["bad", "terrible", "awful", "hate", "worst", "ugly", "disappointing", "boring", "overrated", "trash"],
            "trending": ["viral", "trending", "popular", "hot", "fire", "lit", "buzz", "hype", "craze", "fad"]
        }
        
        self.platform_weights = {
            "discord": 0.4,
            "twitter": 0.3,
            "reddit": 0.2,
            "youtube": 0.1
        }
        
    def analyze_social_engagement(self, items: List[RobloxItem]) -> List[RobloxItem]:
        """Analyze social engagement for all items"""
        try:
            logger.info("Analyzing social engagement...")
            
            for item in items:
                engagement_score = self._calculate_engagement_score(item)
                item.engagement_score = engagement_score
            
            # Sort by engagement score
            items.sort(key=lambda x: x.engagement_score, reverse=True)
            
            logger.info(f"Analyzed engagement for {len(items)} items")
            return items
            
        except Exception as e:
            logger.error(f"Error analyzing social engagement: {e}")
            return items
    
    def _calculate_engagement_score(self, item: RobloxItem) -> float:
        """Calculate social engagement score for an item"""
        try:
            score = 0.0
            
            # Hype factor (from item data)
            if item.hyped:
                score += 0.3
            
            # Demand-based engagement
            demand_scores = {
                DemandTier.NONE: 0.0,
                DemandTier.LOW: 0.1,
                DemandTier.MEDIUM: 0.3,
                DemandTier.HIGH: 0.5,
                DemandTier.VERY_HIGH: 0.7
            }
            score += demand_scores.get(item.demand, 0.0) * 0.2
            
            # Volume-based engagement (proxy for social activity)
            if item.volume > 500:
                score += 0.2
            elif item.volume > 200:
                score += 0.1
            
            # Rarity factor (rare items get more social attention)
            if item.rare:
                score += 0.2
            
            # Premium factor
            if item.premium:
                score += 0.1
            
            # Name-based sentiment analysis
            sentiment_score = self._analyze_name_sentiment(item.name)
            score += sentiment_score * 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating engagement score for item {item.id}: {e}")
            return 0.0
    
    def _analyze_name_sentiment(self, item_name: str) -> float:
        """Analyze sentiment based on item name"""
        try:
            name_lower = item_name.lower()
            score = 0.0
            
            # Count positive keywords
            positive_count = sum(1 for keyword in self.sentiment_keywords["positive"] if keyword in name_lower)
            score += positive_count * 0.1
            
            # Count negative keywords
            negative_count = sum(1 for keyword in self.sentiment_keywords["negative"] if keyword in name_lower)
            score -= negative_count * 0.1
            
            # Count trending keywords
            trending_count = sum(1 for keyword in self.sentiment_keywords["trending"] if keyword in name_lower)
            score += trending_count * 0.15
            
            return max(min(score, 1.0), -1.0)  # Clamp between -1 and 1
            
        except Exception as e:
            logger.error(f"Error analyzing name sentiment: {e}")
            return 0.0
    
    def find_trending_items(self, items: List[RobloxItem]) -> List[RobloxItem]:
        """Find items that are currently trending on social media"""
        try:
            logger.info("Finding trending items...")
            
            trending_items = []
            
            for item in items:
                trending_score = self._calculate_trending_score(item)
                
                if trending_score > 0.6:  # High trending threshold
                    item.engagement_score = trending_score
                    trending_items.append(item)
            
            # Sort by trending score
            trending_items.sort(key=lambda x: x.engagement_score, reverse=True)
            
            logger.info(f"Found {len(trending_items)} trending items")
            return trending_items
            
        except Exception as e:
            logger.error(f"Error finding trending items: {e}")
            return []
    
    def _calculate_trending_score(self, item: RobloxItem) -> float:
        """Calculate trending score based on social indicators"""
        try:
            score = 0.0
            
            # High volume indicates trending
            if item.volume > 800:
                score += 0.4
            elif item.volume > 400:
                score += 0.3
            elif item.volume > 200:
                score += 0.2
            
            # Hype status
            if item.hyped:
                score += 0.3
            
            # High demand
            if item.demand in [DemandTier.HIGH, DemandTier.VERY_HIGH]:
                score += 0.2
            
            # Name contains trending keywords
            name_trending = self._analyze_name_sentiment(item.name)
            if name_trending > 0:
                score += name_trending * 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating trending score: {e}")
            return 0.0
    
    def analyze_sentiment_trends(self, items: List[RobloxItem]) -> Dict[str, Any]:
        """Analyze sentiment trends across items"""
        try:
            logger.info("Analyzing sentiment trends...")
            
            sentiment_data = {
                "positive_items": [],
                "negative_items": [],
                "neutral_items": [],
                "trending_keywords": {},
                "sentiment_distribution": {
                    "positive": 0,
                    "negative": 0,
                    "neutral": 0
                }
            }
            
            for item in items:
                sentiment = self._analyze_name_sentiment(item.name)
                
                if sentiment > 0.2:
                    sentiment_data["positive_items"].append({
                        "name": item.name,
                        "sentiment": sentiment,
                        "engagement_score": item.engagement_score
                    })
                    sentiment_data["sentiment_distribution"]["positive"] += 1
                elif sentiment < -0.2:
                    sentiment_data["negative_items"].append({
                        "name": item.name,
                        "sentiment": sentiment,
                        "engagement_score": item.engagement_score
                    })
                    sentiment_data["sentiment_distribution"]["negative"] += 1
                else:
                    sentiment_data["neutral_items"].append({
                        "name": item.name,
                        "sentiment": sentiment,
                        "engagement_score": item.engagement_score
                    })
                    sentiment_data["sentiment_distribution"]["neutral"] += 1
            
            # Count trending keywords
            keyword_counts = {}
            for item in items:
                name_lower = item.name.lower()
                for keyword in self.sentiment_keywords["trending"]:
                    if keyword in name_lower:
                        keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
            
            sentiment_data["trending_keywords"] = keyword_counts
            
            return sentiment_data
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment trends: {e}")
            return {}
    
    def predict_viral_potential(self, items: List[RobloxItem]) -> List[Dict[str, Any]]:
        """Predict viral potential for items"""
        try:
            logger.info("Predicting viral potential...")
            
            viral_predictions = []
            
            for item in items:
                viral_score = self._calculate_viral_score(item)
                
                if viral_score > 0.5:  # Medium viral potential threshold
                    prediction = {
                        "item_name": item.name,
                        "viral_score": viral_score,
                        "confidence": self._calculate_viral_confidence(item),
                        "reasoning": self._generate_viral_reasoning(item),
                        "estimated_reach": self._estimate_viral_reach(item, viral_score)
                    }
                    viral_predictions.append(prediction)
            
            # Sort by viral score
            viral_predictions.sort(key=lambda x: x["viral_score"], reverse=True)
            
            logger.info(f"Predicted viral potential for {len(viral_predictions)} items")
            return viral_predictions
            
        except Exception as e:
            logger.error(f"Error predicting viral potential: {e}")
            return []
    
    def _calculate_viral_score(self, item: RobloxItem) -> float:
        """Calculate viral potential score"""
        try:
            score = 0.0
            
            # High engagement base
            if item.engagement_score > 0.7:
                score += 0.3
            elif item.engagement_score > 0.5:
                score += 0.2
            
            # High volume (viral items have high activity)
            if item.volume > 600:
                score += 0.3
            elif item.volume > 300:
                score += 0.2
            
            # Hype factor
            if item.hyped:
                score += 0.2
            
            # Rarity factor (rare items go viral more easily)
            if item.rare:
                score += 0.2
            
            # Name appeal
            name_sentiment = self._analyze_name_sentiment(item.name)
            if name_sentiment > 0:
                score += name_sentiment * 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating viral score: {e}")
            return 0.0
    
    def _calculate_viral_confidence(self, item: RobloxItem) -> float:
        """Calculate confidence in viral prediction"""
        try:
            confidence = 0.5  # Base confidence
            
            # Higher volume = higher confidence
            if item.volume > 500:
                confidence += 0.2
            elif item.volume > 200:
                confidence += 0.1
            
            # Consistent demand = higher confidence
            if item.demand in [DemandTier.HIGH, DemandTier.VERY_HIGH]:
                confidence += 0.2
            
            # Hype status = higher confidence
            if item.hyped:
                confidence += 0.1
            
            return min(confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating viral confidence: {e}")
            return 0.5
    
    def _generate_viral_reasoning(self, item: RobloxItem) -> str:
        """Generate reasoning for viral potential"""
        try:
            reasons = []
            
            if item.hyped:
                reasons.append("Currently hyped")
            
            if item.volume > 500:
                reasons.append("High trading volume")
            
            if item.rare:
                reasons.append("Rare item status")
            
            if item.demand in [DemandTier.HIGH, DemandTier.VERY_HIGH]:
                reasons.append("Strong demand")
            
            name_sentiment = self._analyze_name_sentiment(item.name)
            if name_sentiment > 0.2:
                reasons.append("Positive name sentiment")
            
            if reasons:
                return "; ".join(reasons)
            else:
                return "Moderate viral potential"
                
        except Exception as e:
            logger.error(f"Error generating viral reasoning: {e}")
            return "Unknown viral potential"
    
    def _estimate_viral_reach(self, item: RobloxItem, viral_score: float) -> Dict[str, int]:
        """Estimate potential viral reach across platforms"""
        try:
            base_reach = int(viral_score * 10000)  # Base reach multiplier
            
            reach_estimates = {
                "discord": int(base_reach * self.platform_weights["discord"]),
                "twitter": int(base_reach * self.platform_weights["twitter"]),
                "reddit": int(base_reach * self.platform_weights["reddit"]),
                "youtube": int(base_reach * self.platform_weights["youtube"])
            }
            
            # Adjust based on item characteristics
            if item.rare:
                for platform in reach_estimates:
                    reach_estimates[platform] = int(reach_estimates[platform] * 1.5)
            
            if item.hyped:
                for platform in reach_estimates:
                    reach_estimates[platform] = int(reach_estimates[platform] * 1.3)
            
            return reach_estimates
            
        except Exception as e:
            logger.error(f"Error estimating viral reach: {e}")
            return {"discord": 0, "twitter": 0, "reddit": 0, "youtube": 0}
    
    def get_engagement_summary(self, items: List[RobloxItem]) -> Dict[str, Any]:
        """Get summary of engagement analysis"""
        try:
            trending_items = self.find_trending_items(items)
            sentiment_trends = self.analyze_sentiment_trends(items)
            viral_predictions = self.predict_viral_potential(items)
            
            return {
                "total_items_analyzed": len(items),
                "trending_items": len(trending_items),
                "viral_predictions": len(viral_predictions),
                "sentiment_distribution": sentiment_trends.get("sentiment_distribution", {}),
                "top_trending": [
                    {
                        "name": item.name,
                        "engagement_score": item.engagement_score,
                        "volume": item.volume
                    }
                    for item in trending_items[:5]
                ],
                "top_viral": [
                    {
                        "name": pred["item_name"],
                        "viral_score": pred["viral_score"],
                        "confidence": pred["confidence"]
                    }
                    for pred in viral_predictions[:5]
                ],
                "trending_keywords": sentiment_trends.get("trending_keywords", {}),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting engagement summary: {e}")
            return {} 