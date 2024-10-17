import os
from redis.asyncio import Redis
from dotenv import load_dotenv

load_dotenv()


class RedisCache:
    def __init__(self):
        self.host = "localhost"
        self.port = 6379
        self.cache = Redis(host=self.host, port=self.port, decode_responses=True)
        self.expiry = 60 * 10

    async def set_cache(self, key, value):
        try:
            if isinstance(value, dict):
                value = str(value)
            await self.cache.set(key, value)
        except Exception as e:
            print(f"Error setting cache: {e}")

    async def get_cache(self, key):
        try:

            value = await self.cache.get(key)
            if value:

                return eval(value)
            return None
        except Exception as e:
            print(f"Error getting cache: {e}")
            return None
