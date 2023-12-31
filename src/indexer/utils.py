from src.config.config import Config
from src.storage.redis_connection import RedisConnection

REF_INDEX_IN_USES_STRING_SPLIT = 1


def get_object_full_name_from_ref_pointers_set(obj_name: str) -> str:
    """
    Returns the full name of an object from the ref_pointers_hash.
    """
    try:
        with RedisConnection(Config.redis_objects_ops_db) as ops_db:
            full_name = ops_db.get_value_from_hash(Config.ref_pointers_hash, obj_name)
            return full_name.decode() if full_name else None
    except TypeError:
        # When redis is not reachable, the return value is None.
        return None
