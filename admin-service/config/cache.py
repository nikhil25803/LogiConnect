import os
import json
from redis.asyncio import Redis
from dotenv import load_dotenv

load_dotenv()


class RedisCache:
    def __init__(self):
        self.host = os.getenv("REDIS_HOST", "localhost")
        self.port = int(os.getenv("REDIS_PORT", "6379"))
        self.cache = Redis(host=self.host, port=self.port, decode_responses=True)
        self.expiry = 60 * 10

    async def set_cache(self, key, value):
        try:
            await self.cache.set(key, json.dumps(value), ex=self.expiry)
        except Exception as e:
            print(f"Error setting cache: {e}")

    async def get_cache(self, key):
        try:

            value = await self.cache.get(key)
            if value:

                return json.loads(value)
            return None
        except Exception as e:
            print(f"Error getting cache: {e}")
            return None
