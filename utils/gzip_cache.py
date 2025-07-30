import gzip
import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import pickle

logger = logging.getLogger(__name__)

class GzipCache:
    """GZIP-compressed caching system for efficient data storage"""
    
    def __init__(self, cache_dir: str = "cache", max_age_hours: int = 24):
        self.cache_dir = cache_dir
        self.max_age_hours = max_age_hours
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        
        logger.info(f"GzipCache initialized with cache_dir={cache_dir}, max_age={max_age_hours}h")
    
    def save_data(self, key: str, data: Any, compress: bool = True) -> bool:
        """Save data to cache with optional compression"""
        try:
            cache_file = os.path.join(self.cache_dir, f"{key}.cache")
            metadata_file = os.path.join(self.cache_dir, f"{key}.meta")
            
            # Prepare metadata
            metadata = {
                "timestamp": datetime.now().isoformat(),
                "compressed": compress,
                "data_type": type(data).__name__,
                "size": len(str(data)) if hasattr(data, '__len__') else 0
            }
            
            # Save data
            if compress:
                with gzip.open(cache_file, 'wt', encoding='utf-8') as f:
                    if isinstance(data, (dict, list)):
                        json.dump(data, f, indent=2)
                    else:
                        f.write(str(data))
            else:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    if isinstance(data, (dict, list)):
                        json.dump(data, f, indent=2)
                    else:
                        f.write(str(data))
            
            # Save metadata
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            logger.debug(f"Saved data to cache: {key} ({metadata['size']} bytes)")
            return True
            
        except Exception as e:
            logger.error(f"Error saving data to cache {key}: {e}")
            return False
    
    def load_data(self, key: str) -> Optional[Any]:
        """Load data from cache"""
        try:
            cache_file = os.path.join(self.cache_dir, f"{key}.cache")
            metadata_file = os.path.join(self.cache_dir, f"{key}.meta")
            
            # Check if files exist
            if not os.path.exists(cache_file) or not os.path.exists(metadata_file):
                return None
            
            # Load metadata
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Check if cache is expired
            cache_time = datetime.fromisoformat(metadata["timestamp"])
            if datetime.now() - cache_time > timedelta(hours=self.max_age_hours):
                logger.debug(f"Cache expired for {key}")
                self.delete_data(key)
                return None
            
            # Load data
            if metadata.get("compressed", False):
                with gzip.open(cache_file, 'rt', encoding='utf-8') as f:
                    data = f.read()
            else:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = f.read()
            
            # Parse data based on type
            if metadata.get("data_type") in ["dict", "list"]:
                data = json.loads(data)
            
            logger.debug(f"Loaded data from cache: {key}")
            return data
            
        except Exception as e:
            logger.error(f"Error loading data from cache {key}: {e}")
            return None
    
    def delete_data(self, key: str) -> bool:
        """Delete data from cache"""
        try:
            cache_file = os.path.join(self.cache_dir, f"{key}.cache")
            metadata_file = os.path.join(self.cache_dir, f"{key}.meta")
            
            if os.path.exists(cache_file):
                os.remove(cache_file)
            if os.path.exists(metadata_file):
                os.remove(metadata_file)
            
            logger.debug(f"Deleted cache: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting cache {key}: {e}")
            return False
    
    def clear_cache(self) -> bool:
        """Clear all cached data"""
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith(('.cache', '.meta')):
                    os.remove(os.path.join(self.cache_dir, filename))
            
            logger.info("Cache cleared")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about cached data"""
        try:
            cache_info = {
                "total_files": 0,
                "total_size": 0,
                "oldest_file": None,
                "newest_file": None,
                "expired_files": 0
            }
            
            oldest_time = None
            newest_time = None
            
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.meta'):
                    metadata_file = os.path.join(self.cache_dir, filename)
                    
                    try:
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        
                        cache_time = datetime.fromisoformat(metadata["timestamp"])
                        file_size = metadata.get("size", 0)
                        
                        cache_info["total_files"] += 1
                        cache_info["total_size"] += file_size
                        
                        # Track oldest/newest
                        if oldest_time is None or cache_time < oldest_time:
                            oldest_time = cache_time
                            cache_info["oldest_file"] = filename.replace('.meta', '')
                        
                        if newest_time is None or cache_time > newest_time:
                            newest_time = cache_time
                            cache_info["newest_file"] = filename.replace('.meta', '')
                        
                        # Check if expired
                        if datetime.now() - cache_time > timedelta(hours=self.max_age_hours):
                            cache_info["expired_files"] += 1
                    
                    except Exception as e:
                        logger.warning(f"Error reading metadata for {filename}: {e}")
            
            return cache_info
            
        except Exception as e:
            logger.error(f"Error getting cache info: {e}")
            return {}
    
    def cleanup_expired(self) -> int:
        """Remove expired cache files"""
        try:
            expired_count = 0
            
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.meta'):
                    metadata_file = os.path.join(self.cache_dir, filename)
                    
                    try:
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        
                        cache_time = datetime.fromisoformat(metadata["timestamp"])
                        
                        if datetime.now() - cache_time > timedelta(hours=self.max_age_hours):
                            key = filename.replace('.meta', '')
                            if self.delete_data(key):
                                expired_count += 1
                    
                    except Exception as e:
                        logger.warning(f"Error checking expiration for {filename}: {e}")
            
            logger.info(f"Cleaned up {expired_count} expired cache files")
            return expired_count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired cache: {e}")
            return 0 