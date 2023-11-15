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


def add_ref_pointer_to_redis(uses_path: str, processed_path: str):
    """
    Adds a reference pointer to Redis for a given raw path and its path including the commit sha of the ref.
    For example:
    actions/checkout@v4 -> actions/checkout@c533a0a4cfc4962971818edcfac47a2899e69799
    repo/some/workflow.yml@master -> repo/some/workflow.yml@c533a0a4cfc4962971818edcfac47a2899e69799

    Args:
        uses_path (str): The raw path to be added as a key in the Redis hash, it is the output of dependency analysis.
        processed_path (str): The path of the object including the commit sha of the ref
    """
    with RedisConnection(Config.redis_objects_ops_db) as ops_db:
        ops_db.insert_to_hash(Config.ref_pointers_hash, uses_path, processed_path)
