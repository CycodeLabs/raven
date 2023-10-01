from __future__ import annotations

import redis
from src.config.config import Config
import src.logger.log as log


class RedisConnection:
    def __init__(self, redis_db):
        self.redis_client = None
        self.redis_host = Config.redis_host
        self.redis_port = Config.redis_port
        self.redis_db = redis_db

    def __enter__(self) -> RedisConnection:
        try:
            self.redis_client = redis.Redis(
                host=self.redis_host, port=self.redis_port, db=self.redis_db
            )
        except Exception as err:
            log.error(f"Failed to connect to Redis: {err}")

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.redis_client:
            self.redis_client.close()

    ## Hash functions
    def insert_to_hash(self, hash: str, field: str, value: str) -> None:
        try:
            self.redis_client.hset(hash, field, value)
        except redis.exceptions.ResponseError as e:
            log.error(f"Failed to set value: {e}")

    def get_value_from_hash(self, key: str, field: str) -> str:
        return self.redis_client.hget(key, field)

    ## String functions
    def insert_to_string(self, key: str, value: str) -> None:
        try:
            self.redis_client.set(key, value)
        except redis.exceptions.ResponseError as e:
            log.error(f"Failed to set value: {e}")

    def get_string(self, key: str) -> str:
        return self.redis_client.get(key)

    ## Set functions
    def insert_to_set(self, set: str, value: str) -> str:
        try:
            self.redis_client.sadd(set, value)
        except redis.exceptions.ResponseError as e:
            log.error(f"Failed to set value: {e}")

    def exists_in_set(self, set: str, value: str) -> bool:
        return bool(self.redis_client.sismember(set, value))

    def get_set_length(self, set: str) -> int:
        return self.redis_client.scard(set)

    def get_set_values(self, set: str) -> set:
        return self.redis_client.smembers(set)

    ## General DB functions
    def delete_key(self, key: str) -> None:
        self.redis_client.delete(key)

    def flush_db(self) -> None:
        self.redis_client.flushdb()

    def get_all_keys(self) -> list:
        return self.redis_client.keys()
