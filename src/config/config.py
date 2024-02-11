from src.storage.neo4j_graph import GraphDb

# Default Values
DEBUG_DEFAULT = False
MIN_STARS_DEFAULT = 1000
REDIS_CLEAN_DEFAULT = False
NEO4J_CLEAN_DEFAULT = False
QUERIES_PATH_DEFAULT = "library"
REPORT_RAW_FORMAT = "raw"
REPORT_JSON_FORMAT = "json"
SLACK_REPORTER = "slack"

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
REDIS_REF_POINTERS_HASH = "ref_pointers"
# Field names to use in the hash of Actions and Workflows in the DB
REDIS_DATA_HASH_FIELD_NAME = "data"
REDIS_URL_HASH_FIELD_NAME = "url"
REDIS_IS_PUBLIC_HASH_FIELD_NAME = "is_public"

# The DB which contains the objects operations history (downloaded, indexed, etc.) and the ref pointers
REDIS_OBJECTS_OPS_DB = 0
# The DB which contains the downloaded workflows
REDIS_WORKFLOWS_DB = 1
# The DB which contains the downloaded actions
REDIS_ACTIONS_DB = 2

# CLI commands
DOWNLOAD_COMMAND = "download"
DOWNLOAD_ACCOUNT_COMMAND = "account"
DOWNLOAD_CRAWL_COMMAND = "crawl"
INDEX_COMMAND = "index"
REPORT_COMMAND = "report"
SEVERITY_LEVELS = {
    "info": 0,
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}
QUERY_TAGS = [
    "injection",
    "unauthenticated",
    "fixed",
    "priv-esc",
    "supply-chain",
    "best-practice",
    "endoflife",
    "reconnaissance",
]
LAST_QUERY_ID = 16
QUERY_IDS = [f"RQ-{num}" for num in range(1, LAST_QUERY_ID + 1)]


def load_downloader_config(args) -> None:
    """Loading downloader subcommand config.
    Includes redis config.
    """
    Config.debug = args.get("debug", DEBUG_DEFAULT)
    Config.github_token = args.get("token")
    Config.min_stars = args.get("min_stars", MIN_STARS_DEFAULT)
    Config.max_stars = args.get("max_stars")
    Config.account_name = args.get("account_name")
    Config.clean_redis = args.get("clean_redis", REDIS_CLEAN_DEFAULT)

    load_redis_config(args)

    if Config.clean_redis:
        from src.storage.redis_utils import clean_redis_db

        clean_redis_db()


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

    if Config.clean_neo4j or Config.graph.is_graph_empty():
        from src.storage.redis_utils import clean_index
        from src.storage.neo4j_utils import clean_graph

        clean_graph()
        clean_index()


def load_redis_config(args) -> None:
    Config.redis_host = args.get("redis_host", REDIS_HOST_DEFAULT)
    Config.redis_port = args.get("redis_port", REDIS_PORT_DEFAULT)


def load_neo4j_config(args) -> None:
    Config.neo4j_uri = args.get("neo4j_uri", NEO4J_URI_DEFAULT)
    Config.neo4j_username = args.get("neo4j_user", NEO4J_USERNAME_DEFAULT)
    Config.neo4j_password = args.get("neo4j_pass", NEO4J_PASSWORD_DEFAULT)

    # Initializing the neo4j graph connection
    Config.graph = GraphDb(
        uri=Config.neo4j_uri,
        user=Config.neo4j_username,
        password=Config.neo4j_password,
    )


def load_reporter_config(args):
    Config.tags = args.get("tag")
    Config.severity = args.get("severity")
    Config.query_ids = args.get("query_ids")
    Config.queries_path = args.get("queries_path")
    Config.format = args.get("format")
    Config.reporter = args.get("report_command")
    Config.slack_token = args.get("slack_token")
    Config.channel_id = args.get("channel_id")

    load_redis_config(args)
    load_neo4j_config(args)


class Config:
    # Global Config
    debug: bool = None

    # Downloader Config
    github_token: str = None
    min_stars: int = None
    max_stars: int = None
    account_name: list[str] = []

    # Indexer Configs
    clean_neo4j: bool = None

    # Redis Config
    redis_host: str = None
    redis_port: int = None
    clean_redis: bool = None

    # Redis Config Constants
    redis_objects_ops_db: int = REDIS_OBJECTS_OPS_DB
    redis_workflows_db: int = REDIS_WORKFLOWS_DB
    redis_actions_db: int = REDIS_ACTIONS_DB
    redis_data_hash_field_name: str = REDIS_DATA_HASH_FIELD_NAME
    redis_url_hash_field_name: str = REDIS_URL_HASH_FIELD_NAME
    redis_is_public_hash_field_name: str = REDIS_IS_PUBLIC_HASH_FIELD_NAME
    workflow_download_history_set: str = REDIS_WORKFLOW_DOWNLOAD_HISTORY_SET
    action_download_history_set: str = REDIS_ACTION_DOWNLOAD_HISTORY_SET
    workflow_index_history_set: str = REDIS_WORKFLOW_INDEX_HISTORY_SET
    action_index_history_set: str = REDIS_ACTION_INDEX_HISTORY_SET
    ref_pointers_hash: str = REDIS_REF_POINTERS_HASH

    # Report Config Constants
    tags: list = []
    severity: str = None
    query_ids: list = []
    format: str = None
    queries_path: str = QUERIES_PATH_DEFAULT
    reporter: str = None
    slack_token: str = None
    channel_id: str = None

    # Neo4j Config
    neo4j_uri: str = None
    neo4j_username: str = None
    neo4j_password: str = None
    graph: GraphDb = None
