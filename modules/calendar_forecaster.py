import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from models.data_models import RobloxItem, ForecastWindow

logger = logging.getLogger(__name__)

class CalendarForecaster:
    """Forecasts optimal trade windows and market timing"""
    
    def __init__(self):
        self.forecast_days = 30  # Days to forecast ahead
        self.confidence_threshold = 0.6
        self.min_window_days = 3
        self.max_window_days = 14
        
    def forecast_trade_windows(self, items: List[RobloxItem], historical_data: Dict[int, List] = None) -> List[ForecastWindow]:
        """Forecast optimal trade windows for items"""
        try:
            logger.info("Forecasting trade windows...")
            
            windows = []
            
            for item in items:
                item_windows = self._forecast_item_windows(item, historical_data)
                windows.extend(item_windows)
            
            # Sort by expected gain
            windows.sort(key=lambda x: x.expected_gain, reverse=True)
            
            logger.info(f"Forecasted {len(windows)} trade windows")
            return windows
            
        except Exception as e:
            logger.error(f"Error forecasting trade windows: {e}")
            return []
    
    def _forecast_item_windows(self, item: RobloxItem, historical_data: Dict[int, List] = None) -> List[ForecastWindow]:
        """Forecast trade windows for a specific item"""
        try:
            windows = []
            
            # Analyze current market conditions
            current_conditions = self._analyze_current_conditions(item)
            
            # Predict short-term windows (1-7 days)
            short_windows = self._predict_short_term_windows(item, current_conditions)
            windows.extend(short_windows)
            
            # Predict medium-term windows (1-4 weeks)
            medium_windows = self._predict_medium_term_windows(item, current_conditions, historical_data)
            windows.extend(medium_windows)
            
            # Predict long-term windows (1-3 months)
            long_windows = self._predict_long_term_windows(item, current_conditions, historical_data)
            windows.extend(long_windows)
            
            return windows
            
        except Exception as e:
            logger.error(f"Error forecasting windows for item {item.id}: {e}")
            return []
    
    def _analyze_current_conditions(self, item: RobloxItem) -> Dict[str, Any]:
        """Analyze current market conditions for an item"""
        try:
            conditions = {
                "value_trend": "stable",
                "volume_trend": "stable",
                "demand_strength": "medium",
                "volatility": "medium",
                "market_sentiment": "neutral"
            }
            
            # Value trend analysis
            if item.projected > item.value * 1.1:
                conditions["value_trend"] = "rising"
            elif item.projected < item.value * 0.9:
                conditions["value_trend"] = "falling"
            
            # Volume trend analysis
            if item.volume > 500:
                conditions["volume_trend"] = "high"
            elif item.volume < 50:
                conditions["volume_trend"] = "low"
            
            # Demand strength
            demand_map = {
                "none": "weak",
                "low": "weak",
                "medium": "medium",
                "high": "strong",
                "very_high": "very_strong"
            }
            conditions["demand_strength"] = demand_map.get(item.demand.value, "medium")
            
            # Volatility assessment
            if item.volatility > 0.7:
                conditions["volatility"] = "high"
            elif item.volatility < 0.3:
                conditions["volatility"] = "low"
            
            # Market sentiment
            if item.hyped:
                conditions["market_sentiment"] = "bullish"
            elif item.value < item.rap * 0.8:
                conditions["market_sentiment"] = "bearish"
            
            return conditions
            
        except Exception as e:
            logger.error(f"Error analyzing current conditions: {e}")
            return {}
    
    def _predict_short_term_windows(self, item: RobloxItem, conditions: Dict[str, Any]) -> List[ForecastWindow]:
        """Predict short-term trade windows (1-7 days)"""
        try:
            windows = []
            
            # Immediate opportunities (next 1-3 days)
            if conditions.get("value_trend") == "rising" and conditions.get("demand_strength") in ["strong", "very_strong"]:
                window = ForecastWindow(
                    start_date=datetime.now(),
                    end_date=datetime.now() + timedelta(days=3),
                    confidence=0.8,
                    expected_gain=int(item.projected - item.value),
                    reasoning="Strong demand with rising value trend",
                    affected_items=[item.id]
                )
                windows.append(window)
            
            # Volume-based opportunities
            if conditions.get("volume_trend") == "high" and item.volume > 300:
                window = ForecastWindow(
                    start_date=datetime.now(),
                    end_date=datetime.now() + timedelta(days=5),
                    confidence=0.7,
                    expected_gain=int((item.projected - item.value) * 0.8),
                    reasoning="High volume indicates active trading",
                    affected_items=[item.id]
                )
                windows.append(window)
            
            return windows
            
        except Exception as e:
            logger.error(f"Error predicting short-term windows: {e}")
            return []
    
    def _predict_medium_term_windows(self, item: RobloxItem, conditions: Dict[str, Any], historical_data: Dict[int, List] = None) -> List[ForecastWindow]:
        """Predict medium-term trade windows (1-4 weeks)"""
        try:
            windows = []
            
            # Weekly patterns
            if historical_data and item.id in historical_data:
                weekly_patterns = self._analyze_weekly_patterns(item.id, historical_data[item.id])
                
                for pattern in weekly_patterns:
                    window = ForecastWindow(
                        start_date=pattern["start_date"],
                        end_date=pattern["end_date"],
                        confidence=pattern["confidence"],
                        expected_gain=pattern["expected_gain"],
                        reasoning=f"Weekly pattern: {pattern['reasoning']}",
                        affected_items=[item.id]
                    )
                    windows.append(window)
            
            # Demand cycle predictions
            if conditions.get("demand_strength") == "very_strong":
                window = ForecastWindow(
                    start_date=datetime.now() + timedelta(days=7),
                    end_date=datetime.now() + timedelta(days=21),
                    confidence=0.6,
                    expected_gain=int((item.projected - item.value) * 1.2),
                    reasoning="Strong demand cycle expected to continue",
                    affected_items=[item.id]
                )
                windows.append(window)
            
            return windows
            
        except Exception as e:
            logger.error(f"Error predicting medium-term windows: {e}")
            return []
    
    def _predict_long_term_windows(self, item: RobloxItem, conditions: Dict[str, Any], historical_data: Dict[int, List] = None) -> List[ForecastWindow]:
        """Predict long-term trade windows (1-3 months)"""
        try:
            windows = []
            
            # Seasonal patterns
            seasonal_window = self._analyze_seasonal_patterns(item, historical_data)
            if seasonal_window:
                windows.append(seasonal_window)
            
            # Market cycle predictions
            if conditions.get("market_sentiment") == "bullish" and item.rare:
                window = ForecastWindow(
                    start_date=datetime.now() + timedelta(days=30),
                    end_date=datetime.now() + timedelta(days=90),
                    confidence=0.5,
                    expected_gain=int((item.projected - item.value) * 1.5),
                    reasoning="Rare item in bullish market cycle",
                    affected_items=[item.id]
                )
                windows.append(window)
            
            return windows
            
        except Exception as e:
            logger.error(f"Error predicting long-term windows: {e}")
            return []
    
    def _analyze_weekly_patterns(self, item_id: int, history: List[Dict]) -> List[Dict[str, Any]]:
        """Analyze weekly trading patterns"""
        try:
            patterns = []
            
            if len(history) < 14:  # Need at least 2 weeks of data
                return patterns
            
            # Group data by week
            weekly_data = {}
            for entry in history:
                date = entry.get("date")
                if isinstance(date, str):
                    date = datetime.fromisoformat(date.replace('Z', '+00:00'))
                
                week_start = date - timedelta(days=date.weekday())
                week_key = week_start.strftime("%Y-%W")
                
                if week_key not in weekly_data:
                    weekly_data[week_key] = []
                weekly_data[week_key].append(entry)
            
            # Analyze patterns
            for week_key, week_data in weekly_data.items():
                if len(week_data) < 3:  # Need at least 3 data points per week
                    continue
                
                # Calculate weekly metrics
                values = [entry.get("value", 0) for entry in week_data]
                volumes = [entry.get("volume", 0) for entry in week_data]
                
                avg_value = sum(values) / len(values)
                avg_volume = sum(volumes) / len(volumes)
                value_change = (values[-1] - values[0]) / values[0] if values[0] > 0 else 0
                
                # Identify profitable patterns
                if value_change > 0.05 and avg_volume > 100:  # 5%+ gain with good volume
                    pattern = {
                        "start_date": datetime.now() + timedelta(days=7),  # Next week
                        "end_date": datetime.now() + timedelta(days=14),
                        "confidence": min(abs(value_change) * 2, 0.8),
                        "expected_gain": int(avg_value * value_change),
                        "reasoning": f"Weekly pattern: {value_change:.1%} average gain"
                    }
                    patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing weekly patterns: {e}")
            return []
    
    def _analyze_seasonal_patterns(self, item: RobloxItem, historical_data: Dict[int, List] = None) -> Optional[ForecastWindow]:
        """Analyze seasonal trading patterns"""
        try:
            # This is a simplified seasonal analysis
            # In a real implementation, you'd analyze years of data
            
            current_month = datetime.now().month
            
            # Holiday season patterns (November-December)
            if current_month in [11, 12]:
                return ForecastWindow(
                    start_date=datetime.now() + timedelta(days=30),
                    end_date=datetime.now() + timedelta(days=60),
                    confidence=0.6,
                    expected_gain=int((item.projected - item.value) * 1.3),
                    reasoning="Holiday season typically increases demand",
                    affected_items=[item.id]
                )
            
            # Summer patterns (June-August)
            elif current_month in [6, 7, 8]:
                return ForecastWindow(
                    start_date=datetime.now() + timedelta(days=45),
                    end_date=datetime.now() + timedelta(days=90),
                    confidence=0.5,
                    expected_gain=int((item.projected - item.value) * 1.1),
                    reasoning="Summer break increases trading activity",
                    affected_items=[item.id]
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing seasonal patterns: {e}")
            return None
    
    def get_forecast_summary(self, items: List[RobloxItem]) -> Dict[str, Any]:
        """Get summary of forecast analysis"""
        try:
            windows = self.forecast_trade_windows(items)
            
            # Categorize windows by timeframe
            short_term = [w for w in windows if (w.end_date - w.start_date).days <= 7]
            medium_term = [w for w in windows if 7 < (w.end_date - w.start_date).days <= 30]
            long_term = [w for w in windows if (w.end_date - w.start_date).days > 30]
            
            return {
                "total_windows": len(windows),
                "short_term_windows": len(short_term),
                "medium_term_windows": len(medium_term),
                "long_term_windows": len(long_term),
                "highest_expected_gain": max([w.expected_gain for w in windows]) if windows else 0,
                "average_confidence": sum([w.confidence for w in windows]) / len(windows) if windows else 0,
                "top_windows": [
                    {
                        "start_date": w.start_date.isoformat(),
                        "end_date": w.end_date.isoformat(),
                        "expected_gain": w.expected_gain,
                        "confidence": w.confidence,
                        "reasoning": w.reasoning
                    }
                    for w in windows[:5]
                ],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting forecast summary: {e}")
            return {} 