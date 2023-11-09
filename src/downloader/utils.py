from src.config.config import Config
from src.storage.redis_connection import RedisConnection


def insert_workflow_or_action_to_redis(
    db: str, object_path: str, data: str, github_url: str, is_public: bool
) -> None:
    """
    Inserts Workflow or Composite Action data and metadata to Redis as a new hash.
    db (str): The Redis database to use.
    object_path (str): The path of the object to insert.
    data (str): Data of the object.
    github_url (str): The GitHub URL associated with the object.
    is_public (bool): Whether the object is public or not.
    """
    with RedisConnection(db) as redis_db:
        redis_db.insert_to_hash(object_path, Config.redis_data_hash_field_name, data)
        redis_db.insert_to_hash(
            object_path,
            Config.redis_url_hash_field_name,
            github_url,
        )
        redis_db.insert_to_hash(
            object_path,
            Config.redis_is_public_hash_field_name,
            is_public,
        )
