from os import getenv
import src.common.utils as utils
import pytest
import src.logger.log as log
from src.downloader.downloader import download_org_workflows_and_actions
from src.indexer.index import index_downloaded_workflows_and_actions
from src.config.config import load_downloader_config, load_indexer_config


def load_integration_tests_config() -> None:
    load_downloader_config(
        {"debug": False, "token": getenv("GITHUB_TOKEN"), "org_name": "RavenDemo"}
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


def get_nodes(node_type: str) -> (int, list):
    nodes = utils.get_all(node_type)
    indexed_nodes = 0
    nodes_details = []
    for node in nodes:
        if node.get("path").endswith("demo-workflow.yml"):
            indexed_nodes += 1
            node = dict(node)
            nodes_details.append(node)

    return indexed_nodes, nodes_details


def test_all_workflows() -> None:
    indexed_workflows, nodes_details = get_nodes("Workflow")

    for node in nodes_details:
        assert node.get("name") == "run"
        assert node.get("trigger") == ["workflow_dispatch"]

    assert indexed_workflows == 4


def test_all_jobs() -> None:
    indexed_jobs, nodes_details = get_nodes("Job")

    for node in nodes_details:
        assert node.get("name") == "demo_test"
        assert node.get("machine") == "ubuntu-latest"

    assert indexed_jobs == 4


def test_all_composite_actions() -> None:
    indexed_composite_actions, _ = get_nodes("CompositeAction")

    assert indexed_composite_actions == 0


def test_all_steps() -> None:
    indexed_steps, nodes_details = get_nodes("Step")

    for node in nodes_details:
        assert node.get("name", "PrintEnv") == "PrintEnv"
        assert node.get("ref", "v4") == "v4"

    assert indexed_steps == 8


def init_env():
    load_integration_tests_config()
    download_org_workflows_and_actions()
    index_downloaded_workflows_and_actions()


def test():
    log.info("[x] Starting Integration testing")
    init_env()
    tests = [
        test_all_workflows,
        test_all_jobs,
        test_all_composite_actions,
        test_all_steps,
    ]

    for test in tests:
        test()

    pytest.main(["-v", "tests/unit"])


if __name__ == "__main__":
    test()
