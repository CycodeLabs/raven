import functools
import sys

from redis.exceptions import (
    RedisError,
    ConnectionError,
    TimeoutError,
)
from py2neo.errors import Neo4jError, ServiceUnavailable


def catch_exit() -> None:
    from config import Config

    if Config.github_token:
        print("""\n[x] Index results with: python main.py index""")

    elif Config.neo4j_uri:
        neo4j_server = Config.neo4j_uri.split("//")[1].split(":")[0]
        print(f"""\n[x] View results at: http://{neo4j_server}:7474""")

    sys.exit(0)
