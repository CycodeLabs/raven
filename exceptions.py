import functools
import sys

from redis.exceptions import (
    RedisError,
    ConnectionError,
    TimeoutError,
)
from py2neo.errors import (
    Neo4jError,
    ServiceUnavailable
)

def catch_redis_exception(f):
    @functools.wraps(f)
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        
        except ConnectionError as e:
            print(f"[x] Redis connection error, make sure Redis is running by executing:\n ==> make setup")

        except TimeoutError as e:
            print(f"[x] Redis timeout error, make sure Redis is running by executing:\n ==> make setup")

        except RedisError:
            print(f"[x] Redis error: {e}")

        sys.exit(1)

    return func


def catch_neo_exception(f):
    @functools.wraps(f)
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
          
        except ServiceUnavailable as e:
            print(f"[x] Neo4j connection error, make sure Neo4j is running by executing:\n ==> make setup")

        except Neo4jError as e:
            print(f"[x] Neo4j error: {e}")

        sys.exit(1)
            
    return func


def catch_exit() -> None:
    from config import Config
    if Config.github_token:
        print("""\n[x] Exiting, index with: python main.py index --help""")

    elif Config.neo4j_uri:
        neo4j_server = Config.neo4j_uri.split("//")[1].split(":")[0]
        print(f"""\n[x] Exiting, view results at: http://{neo4j_server}:7474""")
    
    sys.exit(0)