from tests.utils import (
    get_graph_structure,
    assert_graph_structures,
)
from tests.integration.integration_consts import (
    INTEGRAION_1_NODES_PATHS,
    GET_NODES_BY_PATH_QUERY,
    GET_RELATIONSHIPS_BY_PATH_QUERY,
    INTEGRAION_1_JSON_PATH,
    DEMO_INDEX_REPOS_WORKFLOW_PATHS,
    DEMO_INDEX_REPOS_JSON_PATH,
)


def test_graph_tree() -> None:
    test_demo_index_repos()
    test_integration_1()


def test_integration_1() -> None:
    """
    Tests Integration 1's graph structure
    This is a repository with a single workflow.
    The workflow has Jobs, Steps, and StepCodeDependency.
    It uses a composite action which is also in the organization.
    The Composite Action has Steps and StepCodeDependency.
    These are all the node types that we currently support.
    """
    nodes_query = GET_NODES_BY_PATH_QUERY.format(paths_list=INTEGRAION_1_NODES_PATHS)
    relationships_query = GET_RELATIONSHIPS_BY_PATH_QUERY.format(
        paths_list=INTEGRAION_1_NODES_PATHS
    )

    graph_structure = get_graph_structure(nodes_query, relationships_query)
    assert_graph_structures(graph_structure, INTEGRAION_1_JSON_PATH)


def test_demo_index_repos() -> None:
    """
    Tests Demo-[1-4]'s graph structures combined.
    These are four different repositories that have similar workflows.
    They all have a workflow that uses the checkout action.
    """
    nodes_query = GET_NODES_BY_PATH_QUERY.format(
        paths_list=DEMO_INDEX_REPOS_WORKFLOW_PATHS
    )
    relationships_query = GET_RELATIONSHIPS_BY_PATH_QUERY.format(
        paths_list=DEMO_INDEX_REPOS_WORKFLOW_PATHS
    )

    graph_structure = get_graph_structure(nodes_query, relationships_query)
    assert_graph_structures(graph_structure, DEMO_INDEX_REPOS_JSON_PATH)
