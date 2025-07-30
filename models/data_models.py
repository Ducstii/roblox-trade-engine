from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class DemandTier(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

class StrategyMode(str, Enum):
    SNIPER = "sniper"
    AGGRESSIVE = "aggressive"
    CONSERVATIVE = "conservative"
    MOMENTUM = "momentum"

class RobloxItem(BaseModel):
    """Represents a Roblox Limited item"""
    id: int
    name: str
    rap: int = Field(description="Recent Average Price")
    value: int = Field(description="Current market value")
    demand: DemandTier
    volume: int = Field(description="Trade volume in last 24h")
    available: int = Field(description="Number available for trade")
    premium: bool = Field(description="Premium item status")
    projected: int = Field(description="Projected value")
    hyped: bool = Field(description="Currently hyped")
    rare: bool = Field(description="Rare item status")
    category: str = Field(description="Item category")
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    
    # Calculated fields
    roi: float = Field(default=0.0, description="Return on Investment percentage")
    volatility: float = Field(default=0.0, description="Price volatility score")
    engagement_score: float = Field(default=0.0, description="Social engagement score")
    trait_score: float = Field(default=0.0, description="Trait-based score")
    momentum_score: float = Field(default=0.0, description="Momentum indicator")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TradeCombo(BaseModel):
    """Represents a trade combination"""
    id: str
    items_offered: List[RobloxItem]
    items_requested: List[RobloxItem]
    projected_gain: int = Field(description="Projected profit in Robux")
    confidence: float = Field(description="Confidence score (0-1)")
    risk_level: str = Field(description="Risk assessment")
    strategy_used: StrategyMode
    created: datetime = Field(default_factory=datetime.now)
    
    # Additional metrics
    total_value_offered: int = Field(description="Total value of offered items")
    total_value_requested: int = Field(description="Total value of requested items")
    roi_percentage: float = Field(description="ROI as percentage")
    volume_score: float = Field(description="Volume-based score")
    demand_score: float = Field(description="Demand-based score")

class MarketMetrics(BaseModel):
    """Market-wide metrics and indicators"""
    total_items: int
    total_value: int
    average_rap: float
    market_volatility: float
    top_gainers: List[RobloxItem]
    top_losers: List[RobloxItem]
    trending_items: List[RobloxItem]
    risk_index: float = Field(description="Overall market risk (0-1)")
    timestamp: datetime = Field(default_factory=datetime.now)

class ScanResult(BaseModel):
    """Result of a market scan"""
    items_scanned: int
    items_found: int
    scan_duration: float
    timestamp: datetime = Field(default_factory=datetime.now)
    top_picks: List[RobloxItem]
    best_combos: List[TradeCombo]
    market_metrics: MarketMetrics
    errors: List[str] = Field(default_factory=list)

class DiscordAlert(BaseModel):
    """Discord alert payload"""
    combo: str = Field(description="Trade combination description")
    gain: int = Field(description="Projected gain in Robux")
    confidence: float = Field(description="Confidence score")
    forecast: str = Field(description="Market forecast")
    link: str = Field(description="Rolimons item link")
    risk_level: str = Field(description="Risk assessment")
    strategy: StrategyMode = Field(description="Strategy used")
    timestamp: datetime = Field(default_factory=datetime.now)

class TimelineData(BaseModel):
    """Historical timeline data for an item"""
    item_id: int
    dates: List[datetime]
    rap_values: List[int]
    demand_values: List[str]
    volume_values: List[int]
    value_values: List[int]
    
class ForecastWindow(BaseModel):
    """Predicted trade window"""
    start_date: datetime
    end_date: datetime
    confidence: float
    expected_gain: int
    reasoning: str
    affected_items: List[int]

class SystemStatus(BaseModel):
    """System status and health metrics"""
    uptime: float
    last_scan: Optional[datetime]
    current_mode: StrategyMode
    active_modules: List[str]
    cache_size: int
    api_requests_today: int
    alerts_sent_today: int
    errors_count: int
    is_healthy: bool

class ConfigUpdate(BaseModel):
    """Configuration update payload"""
    scoring_weights: Optional[Dict[str, float]] = None
    strategy_mode: Optional[StrategyMode] = None
    discord_webhook: Optional[str] = None
    alert_threshold: Optional[int] = None
    scan_interval: Optional[int] = None

class WebhookConfig(BaseModel):
    """Discord webhook configuration"""
    webhook_url: str
    role_id: Optional[str] = None
    alert_threshold: int = 3500
    confidence_threshold: float = 0.9 