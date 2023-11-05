from os import getenv
import pytest
import src.logger.log as log
from src.downloader.download import download_org_workflows_and_actions
from src.indexer.index import index_downloaded_workflows_and_actions
from src.config.config import load_downloader_config, load_indexer_config
from tests.integration.test_graph_structures import test_graph_tree


def load_integration_tests_config() -> None:
    load_downloader_config(
        {
            "debug": False,
            "token": getenv("GITHUB_TOKEN"),
            "org_name": ["RavenIntegrationTests"],
            "clean_redis": False,
        }
    )

    load_indexer_config(
        {
            "debug": False,
            "redis_host": "raven-redis-test",
            "redis_port": 6379,
            "clean_redis": False,
            "neo4j_uri": "neo4j://raven-neo4j-test:7687",
            "neo4j_user": "neo4j",
            "neo4j_pass": "123456789",
            "threads": 1,
            "clean_neo4j": False,
        }
    )


def init_env():
    load_integration_tests_config()
    download_org_workflows_and_actions()
    index_downloaded_workflows_and_actions()


def test():
    init_env()

    log.info("[x] Starting Integration testing")
    test_graph_tree()

    log.info("[x] Starting unit testing")
    pytest.main(["-v", "tests/unit"])


if __name__ == "__main__":
    test()
