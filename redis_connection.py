from __future__ import annotations

import redis
from config import Config
from exceptions import catch_redis_exception


class RedisConnection:

    def __init__(self, redis_db):
        self.redis_client = None
        self.redis_host = Config.redis_host
        self.redis_port = Config.redis_port
        self.redis_db = redis_db

    def __enter__(self) -> RedisConnection:
        try:
            self.redis_client = redis.Redis(host=self.redis_host, port=self.redis_port, db=self.redis_db)
        except Exception as err:
            print(f"Failed to connect to Redis: {err}")

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.redis_client:
            self.redis_client.close()

    @catch_redis_exception
    def insert_to_hash(self, hash: str, field: str, value: str) -> None:
        try:
            self.redis_client.hset(hash, field, value)
        except redis.exceptions.ResponseError as e:
            print(f"Failed to set value: {e}")

    @catch_redis_exception
    def insert_to_string(self, key: str, value: str) -> None:
        try:
            self.redis_client.set(key, value)
        except redis.exceptions.ResponseError as e:
            print(f"Failed to set value: {e}")
    
    @catch_redis_exception
    def get_string(self, key: str) -> str:
        return self.redis_client.get(key)

    @catch_redis_exception
    def insert_to_set(self, set: str, value: str) -> str:
        try:
            self.redis_client.sadd(set, value)
        except redis.exceptions.ResponseError as e:
            print(f"Failed to set value: {e}")

    @catch_redis_exception
    def get_value_from_hash(self, hash: str, field: str) -> str or None:
        return self.redis_client.hget(hash, field)

    @catch_redis_exception
    def exists_in_set(self, set: str, value: str) -> bool:
        return bool(self.redis_client.sismember(set, value))
    
    @catch_redis_exception
    def get_set_length(self, set: str) -> int:
        return self.redis_client.scard(set)
    
    @catch_redis_exception
    def get_set_values(self, set: str) -> set:
        return self.redis_client.smembers(set)
    
    @catch_redis_exception
    def delete_key(self, key: str) -> None:
        self.redis_client.delete(key)
    
    @catch_redis_exception
    def flush_db(self) -> None:
        self.redis_client.flushdb()
    
    @catch_redis_exception
    def get_all_keys(self) -> list:
        return self.redis_client.keys()