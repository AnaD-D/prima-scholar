"""
Prima Scholar Prediction Service
Handles caching and real-time prediction updates
"""

import redis
import json
import logging
from typing import Dict, Optional

class PredictionService:
    def __init__(self, excellence_engine, db_manager, redis_url: Optional[str] = None):
        self.excellence_engine = excellence_engine
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
        
        # Initialize Redis for caching
        if redis_url:
            try:
                self.redis_client = redis.from_url(redis_url)
                self.cache_enabled = True
                self.logger.info("Redis cache enabled")
            except Exception as e:
                self.logger.warning(f"Redis connection failed: {e}")
                self.cache_enabled = False
        else:
            self.cache_enabled = False
    
    def get_cached_prediction(self, student_id: str, distinction: str) -> Optional[Dict]:
        """Get cached prediction if available"""
        if not self.cache_enabled:
            return None
            
        try:
            cache_key = f"prediction:{student_id}:{distinction}"
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            return None
            
        except Exception as e:
            self.logger.error(f"Cache retrieval failed: {e}")
            return None
    
    def cache_prediction(self, student_id: str, distinction: str, prediction: Dict, ttl: int = 600):
        """Cache prediction result"""
        if not self.cache_enabled:
            return
            
        try:
            cache_key = f"prediction:{student_id}:{distinction}"
            self.redis_client.setex(
                cache_key, 
                ttl, 
                json.dumps(prediction)
            )
        except Exception as e:
            self.logger.error(f"Cache storage failed: {e}")
    
    def test_cache(self) -> bool:
        """Test cache connection"""
        if not self.cache_enabled:
            return False
            
        try:
            self.redis_client.ping()
            return True
        except:
            return False