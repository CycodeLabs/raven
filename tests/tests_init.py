from os import getenv
from src.config.config import load_downloader_config, load_indexer_config
from src.downloader.download import download_org_workflows_and_actions
from src.indexer.index import index_downloaded_workflows_and_actions


def init_integration_env():
    load_integration_tests_config()
    download_org_workflows_and_actions()
    index_downloaded_workflows_and_actions()


def load_integration_tests_config() -> None:
    load_downloader_config(
        {
            "debug": False,
            "token": getenv("GITHUB_TOKEN"),
            "org_name": ["RavenIntegrationTests"],
            "redis_host": "localhost",
            "redis_port": 6379,
            "clean_redis": True,
        }
    )

    load_indexer_config(
        {
            "debug": False,
            "redis_host": "localhost",
            "redis_port": 6379,
            "clean_redis": False,
            "neo4j_uri": "neo4j://localhost:7687",
            "neo4j_user": "neo4j",
            "neo4j_pass": "123456789",
            "threads": 1,
            "clean_neo4j": True,
        }
    )
