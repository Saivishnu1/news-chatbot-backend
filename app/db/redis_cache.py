import os
import json
import redis
from typing import Optional, Any
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv('REDIS_HOST', 'redis-17265.c212.ap-south-1-1.ec2.redns.redis-cloud.com')
REDIS_PORT = int(os.getenv('REDIS_PORT', '17265'))
REDIS_DB = os.getenv('REDIS_DB', 'default')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

# Initialize Redis client
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True
)

def get_cache(key: str) -> Optional[Any]:
    """Get value from Redis cache"""
    try:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        print(f"Error getting from cache: {str(e)}")
        return None

def set_cache(key: str, value: Any, expiry_seconds: int = 3600) -> bool:
    """Set value in Redis cache with expiry"""
    try:
        redis_client.setex(
            key,
            expiry_seconds,
            json.dumps(value)
        )
        return True
    except Exception as e:
        print(f"Error setting cache: {str(e)}")
        return False

def delete_cache(key: str) -> bool:
    """Delete value from Redis cache"""
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        print(f"Error deleting from cache: {str(e)}")
        return False