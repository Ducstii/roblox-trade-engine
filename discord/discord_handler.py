import aiohttp
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from models.data_models import DiscordAlert, TradeCombo, RobloxItem, StrategyMode
from config.config_manager import config_manager

logger = logging.getLogger(__name__)

class DiscordHandler:
    """Handles Discord webhook alerts and notifications"""
    
    def __init__(self):
        self.webhook_url = None
        self.role_id = None
        self.alert_threshold = 3500
        self.confidence_threshold = 0.9
        self.session = None
        
        # Load configuration
        self._load_config()
    
    def _load_config(self):
        """Load Discord configuration from config manager"""
        try:
            discord_config = config_manager.get_discord_config()
            self.webhook_url = discord_config.webhook_url
            self.role_id = discord_config.role_id
            self.alert_threshold = discord_config.alert_threshold
            self.confidence_threshold = discord_config.confidence_threshold
            
            logger.info(f"Discord config loaded: threshold={self.alert_threshold}, confidence={self.confidence_threshold}")
            
        except Exception as e:
            logger.error(f"Error loading Discord config: {e}")
    
    async def send_trade_alert(self, combo: TradeCombo) -> bool:
        """Send a trade alert for a high-quality combo"""
        try:
            # Check if combo meets alert criteria
            if not self._should_alert(combo):
                logger.info(f"Combo {combo.id} doesn't meet alert criteria")
                return False
            
            # Create Discord alert
            alert = self._create_discord_alert(combo)
            
            # Send the alert
            success = await self._send_webhook(alert)
            
            if success:
                logger.info(f"Sent Discord alert for combo {combo.id}")
            else:
                logger.error(f"Failed to send Discord alert for combo {combo.id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending trade alert: {e}")
            return False
    
    def _should_alert(self, combo: TradeCombo) -> bool:
        """Check if a combo should trigger an alert"""
        try:
            # Check gain threshold
            if combo.projected_gain < self.alert_threshold:
                return False
            
            # Check confidence threshold
            if combo.confidence < self.confidence_threshold:
                return False
            
            # Additional checks
            if combo.risk_level == "Very High":
                return False  # Skip very high risk trades
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking alert criteria: {e}")
            return False
    
    def _create_discord_alert(self, combo: TradeCombo) -> DiscordAlert:
        """Create a Discord alert from a trade combo"""
        try:
            # Create combo description
            offered_names = [item.name for item in combo.items_offered]
            requested_names = [item.name for item in combo.items_requested]
            
            combo_description = f"{' + '.join(offered_names)} → {' + '.join(requested_names)}"
            
            # Determine forecast
            forecast = self._determine_forecast(combo)
            
            # Create Rolimons link (using first requested item)
            if combo.items_requested:
                item_id = combo.items_requested[0].id
                link = f"https://www.rolimons.com/item/{item_id}"
            else:
                link = "https://www.rolimons.com"
            
            return DiscordAlert(
                combo=combo_description,
                gain=combo.projected_gain,
                confidence=combo.confidence,
                forecast=forecast,
                link=link,
                risk_level=combo.risk_level,
                strategy=combo.strategy_used,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error creating Discord alert: {e}")
            raise
    
    def _determine_forecast(self, combo: TradeCombo) -> str:
        """Determine market forecast based on combo characteristics"""
        try:
            if combo.confidence > 0.95:
                return "very_strong"
            elif combo.confidence > 0.9:
                return "strong"
            elif combo.confidence > 0.8:
                return "moderate"
            else:
                return "weak"
                
        except Exception as e:
            logger.error(f"Error determining forecast: {e}")
            return "moderate"
    
    async def _send_webhook(self, alert: DiscordAlert) -> bool:
        """Send webhook to Discord"""
        try:
            if not self.webhook_url:
                logger.warning("No Discord webhook URL configured")
                return False
            
            # Create embed
            embed = self._create_embed(alert)
            
            # Prepare payload
            payload = {
                "embeds": [embed]
            }
            
            # Add role mention if configured
            if self.role_id:
                payload["content"] = f"<@&{self.role_id}> New trade opportunity!"
            
            # Send webhook
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.post(self.webhook_url, json=payload) as response:
                if response.status == 204:
                    return True
                else:
                    logger.error(f"Discord webhook failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error sending Discord webhook: {e}")
            return False
    
    def _create_embed(self, alert: DiscordAlert) -> Dict[str, Any]:
        """Create a rich embed for Discord"""
        try:
            # Color based on confidence
            color = self._get_confidence_color(alert.confidence)
            
            # Risk level emoji
            risk_emoji = self._get_risk_emoji(alert.risk_level)
            
            # Strategy emoji
            strategy_emoji = self._get_strategy_emoji(alert.strategy)
            
            embed = {
                "title": f"🎯 Trade Opportunity Detected!",
                "description": f"**{alert.combo}**\n\n{strategy_emoji} **Strategy**: {alert.strategy.value.title()}\n{risk_emoji} **Risk**: {alert.risk_level}\n📈 **Forecast**: {alert.forecast.title()}",
                "color": color,
                "fields": [
                    {
                        "name": "💰 Projected Gain",
                        "value": f"**{alert.gain:,}** Robux",
                        "inline": True
                    },
                    {
                        "name": "🎯 Confidence",
                        "value": f"**{alert.confidence:.1%}**",
                        "inline": True
                    },
                    {
                        "name": "⏰ Detected",
                        "value": f"<t:{int(alert.timestamp.timestamp())}:R>",
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "Roblox Trade Command Engine"
                },
                "timestamp": alert.timestamp.isoformat(),
                "url": alert.link
            }
            
            return embed
            
        except Exception as e:
            logger.error(f"Error creating embed: {e}")
            return {}
    
    def _get_confidence_color(self, confidence: float) -> int:
        """Get color based on confidence level"""
        if confidence > 0.95:
            return 0x00FF00  # Green
        elif confidence > 0.9:
            return 0xFFFF00  # Yellow
        elif confidence > 0.8:
            return 0xFFA500  # Orange
        else:
            return 0xFF0000  # Red
    
    def _get_risk_emoji(self, risk_level: str) -> str:
        """Get emoji for risk level"""
        risk_emojis = {
            "Low": "🟢",
            "Medium": "🟡", 
            "High": "🟠",
            "Very High": "🔴"
        }
        return risk_emojis.get(risk_level, "⚪")
    
    def _get_strategy_emoji(self, strategy: StrategyMode) -> str:
        """Get emoji for strategy mode"""
        strategy_emojis = {
            StrategyMode.SNIPER: "🎯",
            StrategyMode.AGGRESSIVE: "⚡",
            StrategyMode.CONSERVATIVE: "🛡️",
            StrategyMode.MOMENTUM: "📈"
        }
        return strategy_emojis.get(strategy, "🎲")
    
    async def send_system_alert(self, message: str, alert_type: str = "info") -> bool:
        """Send a system alert to Discord"""
        try:
            if not self.webhook_url:
                return False
            
            # Create embed
            embed = {
                "title": f"🔧 System Alert",
                "description": message,
                "color": self._get_alert_color(alert_type),
                "timestamp": datetime.now().isoformat(),
                "footer": {
                    "text": "Roblox Trade Command Engine"
                }
            }
            
            payload = {"embeds": [embed]}
            
            # Send webhook
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.post(self.webhook_url, json=payload) as response:
                return response.status == 204
                
        except Exception as e:
            logger.error(f"Error sending system alert: {e}")
            return False
    
    def _get_alert_color(self, alert_type: str) -> int:
        """Get color for system alert type"""
        colors = {
            "info": 0x0099FF,    # Blue
            "success": 0x00FF00,  # Green
            "warning": 0xFFFF00,  # Yellow
            "error": 0xFF0000     # Red
        }
        return colors.get(alert_type, 0x0099FF)
    
    async def send_market_summary(self, summary: Dict[str, Any]) -> bool:
        """Send market summary to Discord"""
        try:
            if not self.webhook_url:
                return False
            
            embed = {
                "title": "📊 Market Summary",
                "description": "Latest market analysis and opportunities",
                "color": 0x0099FF,
                "fields": [
                    {
                        "name": "🔍 Items Scanned",
                        "value": str(summary.get("items_scanned", 0)),
                        "inline": True
                    },
                    {
                        "name": "🎯 Top Picks",
                        "value": str(summary.get("top_picks_count", 0)),
                        "inline": True
                    },
                    {
                        "name": "💼 Trade Combos",
                        "value": str(summary.get("combos_count", 0)),
                        "inline": True
                    }
                ],
                "timestamp": datetime.now().isoformat(),
                "footer": {
                    "text": "Roblox Trade Command Engine"
                }
            }
            
            payload = {"embeds": [embed]}
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.post(self.webhook_url, json=payload) as response:
                return response.status == 204
                
        except Exception as e:
            logger.error(f"Error sending market summary: {e}")
            return False
    
    def update_config(self, webhook_url: str = None, role_id: str = None, 
                     alert_threshold: int = None, confidence_threshold: float = None):
        """Update Discord configuration"""
        try:
            if webhook_url is not None:
                self.webhook_url = webhook_url
            if role_id is not None:
                self.role_id = role_id
            if alert_threshold is not None:
                self.alert_threshold = alert_threshold
            if confidence_threshold is not None:
                self.confidence_threshold = confidence_threshold
            
            # Save to config
            from config.config_manager import DiscordConfig
            discord_config = DiscordConfig(
                webhook_url=self.webhook_url,
                role_id=self.role_id,
                alert_threshold=self.alert_threshold,
                confidence_threshold=self.confidence_threshold
            )
            config_manager.update_discord_config(discord_config)
            
            logger.info("Discord configuration updated")
            
        except Exception as e:
            logger.error(f"Error updating Discord config: {e}")
    
    async def test_webhook(self) -> bool:
        """Test the Discord webhook connection"""
        try:
            if not self.webhook_url:
                logger.warning("No webhook URL configured")
                return False
            
            test_embed = {
                "title": "🧪 Webhook Test",
                "description": "Discord integration is working correctly!",
                "color": 0x00FF00,
                "timestamp": datetime.now().isoformat()
            }
            
            payload = {"embeds": [test_embed]}
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.post(self.webhook_url, json=payload) as response:
                success = response.status == 204
                if success:
                    logger.info("Discord webhook test successful")
                else:
                    logger.error(f"Discord webhook test failed: {response.status}")
                return success
                
        except Exception as e:
            logger.error(f"Error testing Discord webhook: {e}")
            return False
    
    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None 