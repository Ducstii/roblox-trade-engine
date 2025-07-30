import aiohttp
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import time

from models.data_models import RobloxItem, DemandTier

logger = logging.getLogger(__name__)

class RolimonsScraper:
    """Scraper for Rolimons Limited items data"""
    
    def __init__(self):
        self.base_url = "https://www.rolimons.com/api"
        self.session = None
        self.rate_limit_delay = 1.0  # seconds between requests
        self.last_request_time = 0
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a rate-limited request to Rolimons API"""
        await self._rate_limit()
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"API request failed: {response.status}")
                    return {}
        except Exception as e:
            logger.error(f"Error making request to {url}: {e}")
            return {}
    
    async def get_limited_items(self, limit: int = 1000) -> List[RobloxItem]:
        """Fetch Limited items from Rolimons"""
        try:
            logger.info(f"Fetching {limit} Limited items from Rolimons...")
            
            # Note: This is a placeholder implementation
            # Real Rolimons API endpoints would need to be researched
            endpoint = "items"
            params = {
                "category": "limiteds",
                "limit": limit
            }
            
            data = await self._make_request(endpoint, params)
            
            items = []
            if data and "items" in data:
                for item_data in data["items"]:
                    try:
                        item = self._parse_item_data(item_data)
                        if item:
                            items.append(item)
                    except Exception as e:
                        logger.error(f"Error parsing item data: {e}")
                        continue
            
            logger.info(f"Successfully fetched {len(items)} items")
            return items
            
        except Exception as e:
            logger.error(f"Error fetching Limited items: {e}")
            return []
    
    def _parse_item_data(self, item_data: Dict[str, Any]) -> Optional[RobloxItem]:
        """Parse raw item data into RobloxItem model"""
        try:
            # Map demand string to enum
            demand_str = item_data.get("demand", "none").lower()
            demand_map = {
                "none": DemandTier.NONE,
                "low": DemandTier.LOW,
                "medium": DemandTier.MEDIUM,
                "high": DemandTier.HIGH,
                "very_high": DemandTier.VERY_HIGH
            }
            demand = demand_map.get(demand_str, DemandTier.NONE)
            
            return RobloxItem(
                id=item_data.get("id", 0),
                name=item_data.get("name", "Unknown Item"),
                rap=item_data.get("rap", 0),
                value=item_data.get("value", 0),
                demand=demand,
                volume=item_data.get("volume", 0),
                available=item_data.get("available", 0),
                premium=item_data.get("premium", False),
                projected=item_data.get("projected", 0),
                hyped=item_data.get("hyped", False),
                rare=item_data.get("rare", False),
                category=item_data.get("category", "Unknown"),
                created=datetime.now(),
                updated=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error parsing item data: {e}")
            return None
    
    async def get_item_details(self, item_id: int) -> Optional[RobloxItem]:
        """Get detailed information for a specific item"""
        try:
            endpoint = f"items/{item_id}"
            data = await self._make_request(endpoint)
            
            if data:
                return self._parse_item_data(data)
            return None
            
        except Exception as e:
            logger.error(f"Error fetching item details for {item_id}: {e}")
            return None
    
    async def get_market_trends(self) -> Dict[str, Any]:
        """Get market-wide trends and statistics"""
        try:
            endpoint = "market/trends"
            data = await self._make_request(endpoint)
            
            return data or {}
            
        except Exception as e:
            logger.error(f"Error fetching market trends: {e}")
            return {}
    
    async def search_items(self, query: str, limit: int = 50) -> List[RobloxItem]:
        """Search for items by name"""
        try:
            endpoint = "items/search"
            params = {
                "q": query,
                "limit": limit
            }
            
            data = await self._make_request(endpoint, params)
            
            items = []
            if data and "items" in data:
                for item_data in data["items"]:
                    item = self._parse_item_data(item_data)
                    if item:
                        items.append(item)
            
            return items
            
        except Exception as e:
            logger.error(f"Error searching items: {e}")
            return []
    
    async def get_item_history(self, item_id: int, days: int = 30) -> Dict[str, Any]:
        """Get historical data for an item"""
        try:
            endpoint = f"items/{item_id}/history"
            params = {
                "days": days
            }
            
            data = await self._make_request(endpoint, params)
            
            return data or {}
            
        except Exception as e:
            logger.error(f"Error fetching item history for {item_id}: {e}")
            return {}
    
    def close(self):
        """Close the HTTP session"""
        if self.session:
            asyncio.create_task(self.session.close()) 