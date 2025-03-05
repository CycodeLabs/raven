from colorama import Fore, Style
from tests.utils import (
    get_graph_structure,
    assert_graph_structures,
)
from tests.integration.integration_consts import TESTS_CONFIGS
from tests.tests_init import init_integration_single_env


def test_single_workflow_download() -> None:
    init_integration_single_env(only_workflows=["demo-workflow.yml"])

    test_config = next((item for item in TESTS_CONFIGS if item["test_name"] == "test_demo_index_single_repo"), None)

    print(
        f"{Fore.CYAN}Running integration test: {test_config['test_name']}.{Style.RESET_ALL}"
    )

    # Get the queries from the test config
    query_config = test_config["queries"]
    nodes_query = query_config["nodes_query"].format(**query_config["to_format"])
    relationships_query = query_config["relationships_query"].format(
        **query_config["to_format"]
    )

    # Get the graph structure from the queries and assert it
    graph_structure = get_graph_structure(nodes_query, relationships_query)
    assert_graph_structures(graph_structure, test_config["json_path"])
