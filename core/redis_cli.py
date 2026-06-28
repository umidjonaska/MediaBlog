import redis
import orjson
from typing import Any, Optional

class RedisCLI:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        decode_responses=True
    ):
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=decode_responses
        )

    def get(self, key: str) -> Optional[dict]:
        data = self.client.get(key)
        if not data:
            return None
        return orjson.loads(data)

    def set(self, key: str, value: Any, ex: int = None):
        """
        Redis ga ma'lumot saqlash
        """
        # value bytes bo'lsa, str ga o'tkazamiz
        if isinstance(value, bytes):
            value = value.decode('utf-8')
        # dict yoki list bo'lmasa str qilamiz
        elif not isinstance(value, (str, dict, list)):
            value = str(value)

        # JSON ga aylantiramiz
        data = orjson.dumps(value)

        # Redisga saqlaymiz
        if ex:
            self.client.set(key, data, ex=ex)  # self.r emas, self.client
        else:
            self.client.set(key, data)

    def delete(self, key: str) -> bool:
        return bool(self.client.delete(key))
