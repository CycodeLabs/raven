from pathlib import Path
import tempfile
import os
from src.config.config import load_downloader_config, load_indexer_config, load_reporter_config
from src.downloader.download import download_account_workflows_and_actions, download_repo_workflows_and_actions
from src.indexer.index import index_downloaded_workflows_and_actions
from src.config.config import LAST_QUERY_ID, QUERIES_PATH_DEFAULT, Config


def init_integration_env():
    load_integration_tests_config()
    download_account_workflows_and_actions()
    index_downloaded_workflows_and_actions()


def init_integration_single_env(only_workflows: list = []):
    load_integration_tests_config()
    Config.workflow = only_workflows
    download_repo_workflows_and_actions()
    index_downloaded_workflows_and_actions()


def load_integration_tests_config() -> None:
    load_downloader_config(
        {
            "debug": False,
            "token": os.getenv("GITHUB_TOKEN"),
            "account_name": ["RavenIntegrationTests"],
            "repo_name": ["RavenIntegrationTests/Demo-1"],
            "redis_host": "raven-redis-test",
            "redis_port": 6379,
            "clean_redis": True,
        }
    )

    load_indexer_config(
        {
            "debug": False,
            "redis_host": "raven-redis-test",
            "redis_port": 6379,
            "clean_redis": True,
            "neo4j_uri": "neo4j://raven-neo4j-test:7687",
            "neo4j_user": "neo4j",
            "neo4j_pass": "123456789",
            "threads": 1,
            "clean_neo4j": True,
        }
    )

    load_reporter_config(
        {
            "format": "sarif",
            "queries_path": Path(__file__).parent.parent / QUERIES_PATH_DEFAULT,
            "output": os.path.join(tempfile.gettempdir(), next(tempfile._get_candidate_names()))
        }
    )
