from src.storage.redis_connection import RedisConnection
from src.config.config import Config


def clean_redis_db() -> None:
    # Flush all databases
    flush_db(Config.redis_objects_ops_db)
    flush_db(Config.redis_actions_db)
    flush_db(Config.redis_workflows_db)


def clean_index() -> None:
    with RedisConnection(Config.redis_objects_ops_db) as ops_db:
        ops_db.delete_key(Config.workflow_index_history_set)
        ops_db.delete_key(Config.action_index_history_set)


def flush_db(db_number) -> None:
    with RedisConnection(db_number) as db:
        db.flush_db()
