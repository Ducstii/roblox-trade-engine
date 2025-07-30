import json
import os
from typing import Dict, Any, Optional
from pydantic import BaseModel
from pathlib import Path

class ScoringWeights(BaseModel):
    roi_weight: float = 0.3
    demand_weight: float = 0.2
    volume_weight: float = 0.15
    volatility_weight: float = 0.1
    engagement_weight: float = 0.15
    trait_weight: float = 0.1

class DiscordConfig(BaseModel):
    webhook_url: Optional[str] = None
    role_id: Optional[str] = None
    alert_threshold: int = 3500
    confidence_threshold: float = 0.9

class SystemConfig(BaseModel):
    scan_interval: int = 60  # seconds
    cache_retention_days: int = 30
    max_concurrent_requests: int = 10
    api_rate_limit_delay: float = 1.0

class ConfigManager:
    def __init__(self, config_path: str = "config/settings.json"):
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Default configuration
        self.default_config = {
            "scoring_weights": ScoringWeights().dict(),
            "discord": DiscordConfig().dict(),
            "system": SystemConfig().dict(),
            "strategy_mode": "sniper",
            "enabled_modules": [
                "momentum_detector",
                "underpricing_finder", 
                "calendar_forecaster",
                "trait_analyzer",
                "engagement_miner"
            ]
        }
        
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                return self.default_config
        else:
            self.save_config(self.default_config)
            return self.default_config
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_scoring_weights(self) -> ScoringWeights:
        """Get current scoring weights"""
        return ScoringWeights(**self.config.get("scoring_weights", {}))
    
    def update_scoring_weights(self, weights: ScoringWeights) -> None:
        """Update scoring weights"""
        self.config["scoring_weights"] = weights.dict()
        self.save_config(self.config)
    
    def get_discord_config(self) -> DiscordConfig:
        """Get Discord configuration"""
        return DiscordConfig(**self.config.get("discord", {}))
    
    def update_discord_config(self, discord_config: DiscordConfig) -> None:
        """Update Discord configuration"""
        self.config["discord"] = discord_config.dict()
        self.save_config(self.config)
    
    def get_system_config(self) -> SystemConfig:
        """Get system configuration"""
        return SystemConfig(**self.config.get("system", {}))
    
    def get_strategy_mode(self) -> str:
        """Get current strategy mode"""
        return self.config.get("strategy_mode", "sniper")
    
    def set_strategy_mode(self, mode: str) -> None:
        """Set strategy mode"""
        valid_modes = ["sniper", "aggressive", "conservative", "momentum"]
        if mode in valid_modes:
            self.config["strategy_mode"] = mode
            self.save_config(self.config)
        else:
            raise ValueError(f"Invalid strategy mode. Must be one of: {valid_modes}")
    
    def get_enabled_modules(self) -> list:
        """Get list of enabled modules"""
        return self.config.get("enabled_modules", [])
    
    def toggle_module(self, module_name: str, enabled: bool) -> None:
        """Enable or disable a module"""
        modules = self.get_enabled_modules()
        if enabled and module_name not in modules:
            modules.append(module_name)
        elif not enabled and module_name in modules:
            modules.remove(module_name)
        
        self.config["enabled_modules"] = modules
        self.save_config(self.config)

# Global config instance
config_manager = ConfigManager() 