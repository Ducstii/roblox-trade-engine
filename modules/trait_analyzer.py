import logging
from typing import List, Dict, Any, Set
from datetime import datetime
from models.data_models import RobloxItem, DemandTier

logger = logging.getLogger(__name__)

class TraitAnalyzer:
    """Analyzes item traits and characteristics for enhanced scoring"""
    
    def __init__(self):
        self.valuable_categories = {
            "hats": 0.8,
            "faces": 0.7,
            "accessories": 0.6,
            "limiteds": 0.9,
            "collectibles": 0.7,
            "rare": 0.8,
            "premium": 0.6
        }
        
        self.trending_keywords = {
            "vintage": 0.3,
            "classic": 0.2,
            "retro": 0.2,
            "exclusive": 0.4,
            "limited": 0.3,
            "rare": 0.4,
            "premium": 0.3,
            "collector": 0.3,
            "special": 0.2,
            "unique": 0.3
        }
        
    def analyze_item_traits(self, items: List[RobloxItem]) -> List[RobloxItem]:
        """Analyze traits for all items and update their trait scores"""
        try:
            logger.info("Analyzing item traits...")
            
            for item in items:
                trait_score = self._calculate_trait_score(item)
                item.trait_score = trait_score
            
            # Sort by trait score
            items.sort(key=lambda x: x.trait_score, reverse=True)
            
            logger.info(f"Analyzed traits for {len(items)} items")
            return items
            
        except Exception as e:
            logger.error(f"Error analyzing item traits: {e}")
            return items
    
    def _calculate_trait_score(self, item: RobloxItem) -> float:
        """Calculate trait-based score for an item"""
        try:
            score = 0.0
            
            # Category-based scoring
            category_score = self._analyze_category(item)
            score += category_score * 0.3
            
            # Name-based keyword analysis
            keyword_score = self._analyze_keywords(item)
            score += keyword_score * 0.2
            
            # Rarity analysis
            rarity_score = self._analyze_rarity(item)
            score += rarity_score * 0.3
            
            # Demand consistency
            demand_score = self._analyze_demand_consistency(item)
            score += demand_score * 0.2
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating trait score for item {item.id}: {e}")
            return 0.0
    
    def _analyze_category(self, item: RobloxItem) -> float:
        """Analyze item category for scoring"""
        try:
            category = item.category.lower()
            
            # Direct category match
            if category in self.valuable_categories:
                return self.valuable_categories[category]
            
            # Partial category matches
            for valuable_cat, score in self.valuable_categories.items():
                if valuable_cat in category or category in valuable_cat:
                    return score * 0.8  # Slightly reduced for partial matches
            
            # Default category score
            return 0.3
            
        except Exception as e:
            logger.error(f"Error analyzing category: {e}")
            return 0.3
    
    def _analyze_keywords(self, item: RobloxItem) -> float:
        """Analyze item name for trending keywords"""
        try:
            name = item.name.lower()
            score = 0.0
            
            for keyword, keyword_score in self.trending_keywords.items():
                if keyword in name:
                    score += keyword_score
            
            # Cap the keyword score
            return min(score, 0.8)
            
        except Exception as e:
            logger.error(f"Error analyzing keywords: {e}")
            return 0.0
    
    def _analyze_rarity(self, item: RobloxItem) -> float:
        """Analyze item rarity characteristics"""
        try:
            score = 0.0
            
            # Rare status
            if item.rare:
                score += 0.4
            
            # Premium status
            if item.premium:
                score += 0.3
            
            # Availability factor (lower availability = higher rarity)
            if item.available > 0:
                availability_ratio = min(item.available / 1000.0, 1.0)
                rarity_bonus = (1.0 - availability_ratio) * 0.3
                score += rarity_bonus
            
            # Value-based rarity (higher value items tend to be rarer)
            if item.value > 10000:
                score += 0.2
            elif item.value > 5000:
                score += 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error analyzing rarity: {e}")
            return 0.0
    
    def _analyze_demand_consistency(self, item: RobloxItem) -> float:
        """Analyze demand consistency and stability"""
        try:
            score = 0.0
            
            # High demand items get higher scores
            demand_scores = {
                DemandTier.NONE: 0.0,
                DemandTier.LOW: 0.2,
                DemandTier.MEDIUM: 0.5,
                DemandTier.HIGH: 0.8,
                DemandTier.VERY_HIGH: 1.0
            }
            score += demand_scores.get(item.demand, 0.0) * 0.6
            
            # Volume consistency (moderate volume is good)
            if 50 <= item.volume <= 500:
                score += 0.2
            elif item.volume > 500:
                score += 0.1  # High volume might indicate oversaturation
            
            # Hype factor (temporary boost)
            if item.hyped:
                score += 0.2
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error analyzing demand consistency: {e}")
            return 0.0
    
    def find_similar_items(self, target_item: RobloxItem, all_items: List[RobloxItem], limit: int = 5) -> List[RobloxItem]:
        """Find items similar to the target item"""
        try:
            logger.info(f"Finding items similar to {target_item.name}...")
            
            similarities = []
            
            for item in all_items:
                if item.id == target_item.id:
                    continue
                
                similarity_score = self._calculate_similarity(target_item, item)
                if similarity_score > 0.5:  # Minimum similarity threshold
                    item.trait_score = similarity_score
                    similarities.append(item)
            
            # Sort by similarity score
            similarities.sort(key=lambda x: x.trait_score, reverse=True)
            
            logger.info(f"Found {len(similarities)} similar items")
            return similarities[:limit]
            
        except Exception as e:
            logger.error(f"Error finding similar items: {e}")
            return []
    
    def _calculate_similarity(self, item1: RobloxItem, item2: RobloxItem) -> float:
        """Calculate similarity between two items"""
        try:
            score = 0.0
            
            # Category similarity
            if item1.category.lower() == item2.category.lower():
                score += 0.3
            
            # Value range similarity
            value_ratio = min(item1.value, item2.value) / max(item1.value, item2.value)
            if value_ratio > 0.8:  # Within 20% value range
                score += 0.2
            
            # Demand similarity
            if item1.demand == item2.demand:
                score += 0.2
            
            # Rarity similarity
            if item1.rare == item2.rare:
                score += 0.1
            if item1.premium == item2.premium:
                score += 0.1
            
            # Name keyword similarity
            name_similarity = self._calculate_name_similarity(item1.name, item2.name)
            score += name_similarity * 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between item names"""
        try:
            words1 = set(name1.lower().split())
            words2 = set(name2.lower().split())
            
            if not words1 or not words2:
                return 0.0
            
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            if not union:
                return 0.0
            
            return len(intersection) / len(union)
            
        except Exception as e:
            logger.error(f"Error calculating name similarity: {e}")
            return 0.0
    
    def analyze_trait_patterns(self, items: List[RobloxItem]) -> Dict[str, Any]:
        """Analyze patterns in item traits"""
        try:
            logger.info("Analyzing trait patterns...")
            
            patterns = {
                "category_distribution": {},
                "rarity_distribution": {},
                "demand_distribution": {},
                "value_ranges": {},
                "trending_keywords": {}
            }
            
            # Category distribution
            for item in items:
                category = item.category.lower()
                patterns["category_distribution"][category] = patterns["category_distribution"].get(category, 0) + 1
            
            # Rarity distribution
            rare_count = sum(1 for item in items if item.rare)
            premium_count = sum(1 for item in items if item.premium)
            patterns["rarity_distribution"] = {
                "rare": rare_count,
                "premium": premium_count,
                "total": len(items)
            }
            
            # Demand distribution
            demand_counts = {}
            for item in items:
                demand = item.demand.value
                demand_counts[demand] = demand_counts.get(demand, 0) + 1
            patterns["demand_distribution"] = demand_counts
            
            # Value ranges
            value_ranges = {
                "low": sum(1 for item in items if item.value < 1000),
                "medium": sum(1 for item in items if 1000 <= item.value < 10000),
                "high": sum(1 for item in items if item.value >= 10000)
            }
            patterns["value_ranges"] = value_ranges
            
            # Trending keywords
            keyword_counts = {}
            for item in items:
                name = item.name.lower()
                for keyword in self.trending_keywords:
                    if keyword in name:
                        keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
            patterns["trending_keywords"] = keyword_counts
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing trait patterns: {e}")
            return {}
    
    def get_trait_recommendations(self, items: List[RobloxItem]) -> Dict[str, Any]:
        """Get trait-based trading recommendations"""
        try:
            logger.info("Generating trait recommendations...")
            
            recommendations = {
                "high_trait_score": [],
                "category_opportunities": {},
                "rarity_opportunities": [],
                "keyword_opportunities": [],
                "similar_item_groups": []
            }
            
            # High trait score items
            high_trait_items = [item for item in items if item.trait_score > 0.7]
            recommendations["high_trait_score"] = [
                {
                    "name": item.name,
                    "trait_score": item.trait_score,
                    "category": item.category,
                    "value": item.value
                }
                for item in high_trait_items[:10]
            ]
            
            # Category opportunities
            category_scores = {}
            for item in items:
                category = item.category.lower()
                if category not in category_scores:
                    category_scores[category] = []
                category_scores[category].append(item.trait_score)
            
            for category, scores in category_scores.items():
                avg_score = sum(scores) / len(scores)
                if avg_score > 0.6:
                    recommendations["category_opportunities"][category] = {
                        "average_score": avg_score,
                        "item_count": len(scores)
                    }
            
            # Rarity opportunities
            rare_items = [item for item in items if item.rare and item.trait_score > 0.5]
            recommendations["rarity_opportunities"] = [
                {
                    "name": item.name,
                    "trait_score": item.trait_score,
                    "value": item.value,
                    "demand": item.demand.value
                }
                for item in rare_items[:5]
            ]
            
            # Keyword opportunities
            keyword_items = []
            for item in items:
                name = item.name.lower()
                keyword_count = sum(1 for keyword in self.trending_keywords if keyword in name)
                if keyword_count >= 2 and item.trait_score > 0.5:  # Multiple keywords
                    keyword_items.append({
                        "name": item.name,
                        "trait_score": item.trait_score,
                        "keyword_count": keyword_count,
                        "value": item.value
                    })
            
            recommendations["keyword_opportunities"] = sorted(
                keyword_items, 
                key=lambda x: x["keyword_count"], 
                reverse=True
            )[:5]
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting trait recommendations: {e}")
            return {} 