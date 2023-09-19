from __future__ import annotations

import redis
from config import Config


class RedisConnection:

    def __init__(self):
        self.redis_client = None

    def __enter__(self) -> RedisConnection:

        try:
            self.redis_client = redis.Redis(host=Config.redis_host, port=Config.redis_port, db=Config.redis_db)
        except Exception as err:
            print(f"Failed to connect to Redis: {err}")

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.redis_client:
            self.redis_client.close()

    def insert_to_hash(self, hash: str, field: str, value: str) -> None:
        try:
            self.redis_client.hset(hash, field, value)
        except redis.exceptions.ResponseError as e:
            print(f"Failed to set value: {e}")

    def insert_to_set(self, set: str, value: str) -> str:
        try:
            self.redis_client.sadd(set, value)
        except redis.exceptions.ResponseError as e:
            print(f"Failed to set value: {e}")

    def get_value_from_hash(self, hash: str, field: str) -> str or None:
        return self.redis_client.hget(hash, field)

    def exists_in_set(self, set: str, value: str) -> bool:
        return bool(self.redis_client.sismember(set, value))
    
    def get_set_length(self, set: str) -> int:
        return self.redis_client.scard(set)
    
    def get_set_values(self, set: str) -> set:
        return self.redis_client.smembers(set)
    
    def delete_key(self, key: str) -> None:
        self.redis_client.delete(key)
    