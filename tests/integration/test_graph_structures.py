import json

from tests.utils import (
    get_graph_structure,
    assert_graph_structures,
)
from tests.integration.integration_consts import (
    INTEGRAION_1_NODES_PATHS,
    GET_NODES_BY_PATH_QUERY,
    GET_RELATIONSHIPS_BY_PATH_QUERY,
    INTEGRAION_1_JSON_PATH,
)


def test_graph_tree() -> None:
    test_integration_1()


def test_integration_1() -> None:
    nodes_query = GET_NODES_BY_PATH_QUERY.format(paths_list=INTEGRAION_1_NODES_PATHS)
    relationships_query = GET_RELATIONSHIPS_BY_PATH_QUERY.format(
        paths_list=INTEGRAION_1_NODES_PATHS
    )

    graph_structure = get_graph_structure(nodes_query, relationships_query)

    assert_graph_structures(graph_structure, INTEGRAION_1_JSON_PATH)
