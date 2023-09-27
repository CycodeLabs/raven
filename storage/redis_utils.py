from redis_connection import RedisConnection
from config import Config


def clean_redis_db() -> None:
    # Flush all databases
    flush_db(Config.redis_sets_db)
    flush_db(Config.redis_actions_db)
    flush_db(Config.redis_workflows_db)


def flush_db(db_number) -> None:
    with RedisConnection(db_number) as db:
        db.flush_db()
