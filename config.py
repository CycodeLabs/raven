from graph_db import GraphDb
from cache import Cache
from os import getenv

# Default Values
DEBUG_DEFAULT = False
MIN_STARS_DEFAULT = 1000
REDIS_CLEAN_DEFAULT = False
NEO4J_CLEAN_DEFAULT = False
REPORT_SLACK_DEFAULT = False

NEO4J_URI_DEFAULT = "neo4j://localhost:7687"
NEO4J_USERNAME_DEFAULT = "neo4j"
NEO4J_PASSWORD_DEFAULT = "123456789"

REDIS_HOST_DEFAULT = "localhost"
REDIS_PORT_DEFAULT = 6379

# Constants
REDIS_WORKFLOW_DOWNLOAD_HISTORY_SET = "workflow_download_history"
REDIS_ACTION_DOWNLOAD_HISTORY_SET = "action_download_history"
REDIS_WORKFLOW_INDEX_HISTORY_SET = "workflow_index_history"
REDIS_ACTION_INDEX_HISTORY_SET = "action_index_history"
REDIS_SETS_DB = 0
REDIS_WORKFLOWS_DB = 1
REDIS_ACTIONS_DB = 2


def load_downloader_config(args) -> None:
    """Loading downloader subcommand config.
    Includes redis config.
    """
    Config.debug = args.get("debug", DEBUG_DEFAULT)
    Config.github_token = args.get("token")
    Config.min_stars = args.get("min_stars", MIN_STARS_DEFAULT)
    Config.max_stars = args.get("max_stars")
    Config.org_name = args.get("org_name")
    Config.clean_redis = args.get("clean_redis", REDIS_CLEAN_DEFAULT)

    load_redis_config(args)


def load_indexer_config(args) -> None:
    """Loading indexer subcommand config.
    Includes redis and neo4j config.
    """
    Config.debug = args.get("debug", DEBUG_DEFAULT)
    Config.clean_neo4j = args.get("clean_neo4j", NEO4J_CLEAN_DEFAULT)
    Config.clean_redis = args.get("clean_redis", REDIS_CLEAN_DEFAULT)

    load_redis_config(args)
    load_neo4j_config(args)
    load_reporter_config(args)


def load_redis_config(args) -> None:
    Config.redis_host = args.get("redis_host", REDIS_HOST_DEFAULT)
    Config.redis_port = args.get("redis_port", REDIS_PORT_DEFAULT)


def load_neo4j_config(args) -> None:
    Config.neo4j_uri = args.get("neo4j_uri", NEO4J_URI_DEFAULT)
    Config.neo4j_username = args.get("neo4j_username", NEO4J_USERNAME_DEFAULT)
    Config.neo4j_password = args.get("neo4j_password", NEO4J_PASSWORD_DEFAULT)

    # Initializing the neo4j graph connection
    Config.graph = GraphDb(
        uri=Config.neo4j_uri,
        user=Config.neo4j_username,
        password=Config.neo4j_password,
    )


def load_reporter_config(args):
    Config.slack = args.get("slack")
    Config.slack_token = args.get("slack_token")
    Config.channel_id = args.get("channel_id")


class Config:
    # Global Config
    debug: bool = None

    # Downloader Config
    github_token: str = None
    min_stars: int = None
    max_stars: int = None
    org_name: str = None

    # Indexer Configs
    clean_neo4j: bool = None

    # Redis Config
    redis_host: str = None
    redis_port: int = None
    clean_redis: bool = None

    # Redis Config Constants
    redis_sets_db: int = REDIS_SETS_DB
    redis_workflows_db: int = REDIS_WORKFLOWS_DB
    redis_actions_db: int = REDIS_ACTIONS_DB
    workflow_download_history_set: str = REDIS_WORKFLOW_DOWNLOAD_HISTORY_SET
    action_download_history_set: str = REDIS_ACTION_DOWNLOAD_HISTORY_SET
    workflow_index_history_set: str = REDIS_WORKFLOW_INDEX_HISTORY_SET
    action_index_history_set: str = REDIS_ACTION_INDEX_HISTORY_SET

    # Neo4j Config
    neo4j_uri: str = None
    neo4j_username: str = None
    neo4j_password: str = None
    graph: GraphDb = None
