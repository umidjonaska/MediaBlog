import redis
import orjson
from typing import Any, Optional, cast


class RedisCLI:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
    ):
        self.client: redis.Redis = redis.Redis(host=host, port=port, db=db)

    def get(self, key: str) -> Optional[Any]:
        raw = self.client.get(key)
        data = cast(Optional[bytes], raw)
        if data is None:
            return None
        return orjson.loads(data)

    def set(self, key: str, value: Any, ex: int | None = None) -> None:
        data = orjson.dumps(value)
        self.client.set(key, data, ex=ex)

    def delete(self, key: str) -> bool:
        return bool(self.client.delete(key))