import os
from graph_db import GraphDb
from cache import Cache


class Config:
    # Downloader Config
    github_token: str = None
    min_stars: int = None
    max_stars: int = None
    output_data_dir: str = None

    # Indexer Configs
    input_data_dir: str = None
    neo4j_uri: str = None
    neo4j_username: str = None
    neo4j_password: str = None
    num_workers: int = None
    clean_neo4j: bool = None
    graph: GraphDb = None
    workflow_index_cache: Cache = None
    action_index_cache: Cache = None
    workflow_download_cache: Cache = None
    action_download_cache: Cache = None

    # Redis Config
    redis_host: str = None
    redis_port: int = None
    redis_sets_db: int = None
    redis_workflows_db: int = None
    redis_actions_db: int = None
    clean_redis: bool = None

    # Paths to store/load data
    data_dir: str = None
    workflow_data_path: str = None
    action_data_path: str = None
    workflow_download_history_path: str = None
    action_download_history_path: str = None
    workflow_index_history_path: str = None
    action_index_history_path: str = None
    # workflow_data_hash: str = None
    # action_data_hash: str = None
    workflow_download_history_set: str = None
    action_download_history_set: str = None
    workflow_index_history_set: str = None
    action_index_history_set: str = None

    @staticmethod
    def load_downloader_config(args):
        Config.github_token = args.get("token")
        Config.output_data_dir = args.get("output")
        Config.min_stars = args.get("min_stars")
        Config.max_stars = args.get("max_stars")
        Config.org_name = args.get("org_name")

        Config.load_redis_config(args)

        # Config.load_data_dir_paths(Config.output_data_dir)

        # Cache/history that is used to optimize indexing.
        Config.workflow_download_cache = Cache(
            fpath=Config.workflow_download_history_path, num_insertions_to_backup=1
        )
        Config.action_download_cache = Cache(
            fpath=Config.action_download_history_path, num_insertions_to_backup=1
        )

    @staticmethod
    def load_indexer_config(args):
        Config.input_data_dir = args.get("input")
        Config.neo4j_uri = args.get("neo4j_uri")
        Config.neo4j_username = args.get("neo4j_user")
        Config.neo4j_password = args.get("neo4j_pass")
        Config.num_workers = args.get("threads")
        Config.clean_neo4j = args.get("clean_neo4j")

        Config.load_redis_config(args)

        # Config.load_data_dir_paths(Config.input_data_dir)

        # Cache/history that is used to optimize indexing.
        Config.workflow_index_cache = Cache(
            fpath=Config.workflow_index_history_path, clean_cache=Config.clean_neo4j
        )
        Config.action_index_cache = Cache(
            fpath=Config.action_index_history_path, clean_cache=Config.clean_neo4j
        )

        # Initializing the neo4j graph connection
        Config.graph = GraphDb(
            uri=Config.neo4j_uri,
            user=Config.neo4j_username,
            password=Config.neo4j_password,
        )

    @staticmethod
    def load_redis_config(args):
        Config.redis_host = args.get("redis_host")
        Config.redis_port = args.get("redis_port")
        Config.clean_redis = args.get("clean_redis")

        Config.redis_sets_db = 0
        Config.redis_workflows_db = 1
        Config.redis_actions_db = 2

        # Redis keys
        # Config.workflow_data_hash = "workflows"
        # Config.action_data_hash = "actions"
        Config.workflow_download_history_set = "workflow_download_history"
        Config.action_download_history_set = "action_download_history"
        Config.workflow_index_history_set = "workflow_index_history"
        Config.action_index_history_set = "action_index_history"

    @staticmethod
    def load_default_index_config() -> None:
        Config.neo4j_uri = "neo4j://localhost:7687"
        Config.neo4j_username = "neo4j"
        Config.neo4j_password = "123456789"
        Config.graph = GraphDb(
            uri=Config.neo4j_uri,
            user=Config.neo4j_username,
            password=Config.neo4j_password,
        )

    @staticmethod
    def load_default_redis_config() -> None:
        Config.redis_host = "localhost"
        Config.redis_port = "6379"

        Config.redis_sets_db = 0
        Config.redis_workflows_db = 1
        Config.redis_actions_db = 2

    @staticmethod
    def load_data_dir_paths(input_data_dir: str):
        data_dir = input_data_dir

        Config.workflow_data_path = os.path.join(data_dir, "workflows")
        Config.action_data_path = os.path.join(data_dir, "actions")
        Config.workflow_download_history_path = os.path.join(
            data_dir, "workflow_download_history.txt"
        )
        Config.action_download_history_path = os.path.join(
            data_dir, "action_download_history.txt"
        )
        Config.workflow_index_history_path = os.path.join(
            data_dir, "workflow_index_history.txt"
        )
        Config.action_index_history_path = os.path.join(
            data_dir, "action_index_history.txt"
        )

        os.makedirs(Config.workflow_data_path, exist_ok=True)
        os.makedirs(Config.action_data_path, exist_ok=True)

        if not os.path.exists(Config.workflow_download_history_path):
            with open(
                Config.workflow_download_history_path, "w", encoding="ascii"
            ) as _:
                pass
        if not os.path.exists(Config.action_download_history_path):
            with open(Config.action_download_history_path, "w", encoding="ascii") as _:
                pass
        if not os.path.exists(Config.workflow_index_history_path):
            with open(Config.workflow_index_history_path, "w", encoding="ascii") as _:
                pass
        if not os.path.exists(Config.action_index_history_path):
            with open(Config.action_index_history_path, "w", encoding="ascii") as _:
                pass
