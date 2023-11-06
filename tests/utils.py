from py2neo.ogm import GraphObject
import json

from src.config.config import Config
from typing import Tuple, List, Dict, Optional


class GraphDbMock(object):
    def __init__(self):
        pass

    def push_object(self, obj: GraphObject):
        pass

    def get_object(self, obj: GraphObject) -> Optional[GraphObject]:
        return None

    def get_or_create(self, obj: GraphObject) -> Tuple[GraphObject, bool]:
        return None, True


def load_test_config() -> None:
    Config.graph = GraphDbMock()


def get_nodes_as_dicts(node_type: str, paths: Optional[List[str]] = []) -> List[Dict]:
    """
    - node_type (str): The type of the node to filter by.
    - path (list, str, optional): List of all the paths to filter nodes by.

    Returns A list of nodes as dictionaries that match the given type and paths.
    """
    nodes = Config.graph.get_all_nodes(node_type)
    if paths:
        return [dict(node) for node in nodes if node.get("path") in paths]
    else:
        return [dict(node) for node in nodes]


def query_graph_for_nodes(query: str) -> List[Dict]:
    """
    Returns dictionary representations of the nodes returned by the query.
    """
    nodes_query = Config.graph.run_query(query)
    nodes = []
    for node in nodes_query:
        node_obj = node.values()[0]
        extracted_node = dict(node_obj)
        extracted_node["labels"] = list(node_obj._labels)
        nodes.append(extracted_node)
    return nodes


def query_graph_for_relationships(query: str) -> List[Dict]:
    """
    Returns dictionary representations of the relationships returned by the query.
    """
    relationships_query = Config.graph.run_query(query)
    relationships = []
    for rq in relationships_query:
        r_dict = {
            "start_node": rq[0].get("_id"),
            "type": rq[1].__class__.__name__,
            "end_node": rq[2].get("_id"),
        }
        relationships.append(r_dict)
    return relationships


def get_graph_structure(nodes_query: str, relationships_query: str) -> Dict:
    """
    Recieves a query for nodes and a query for relationships.
    Returns a dictionary representation of the graph structure.
    """
    nodes = query_graph_for_nodes(nodes_query)
    relationships = query_graph_for_relationships(relationships_query)
    return {"nodes": nodes, "relationships": relationships}


def get_sorted_lists_of_nodes_and_relationships(
    graph_structure: Dict,
) -> Tuple[List, List]:
    """
    Recieves a graph structure and returns sorted lists of nodes and relationships.
    """
    nodes = graph_structure.get("nodes")
    relationships = graph_structure.get("relationships")

    nodes.sort(key=lambda x: x.get("_id"))
    relationships.sort(key=lambda x: (x.get("start_node"), x.get("end_node")))

    return nodes, relationships


def assert_graph_structures(graph_structure: Dict, snapshot_path: str) -> None:
    """
    Recieves a graph structure and a path to a json file containing a graph structure snapshot.
    """
    with open(snapshot_path, "r") as f:
        snapshot_structure = json.load(f)

    snapshot_nodes, snapshot_relations = get_sorted_lists_of_nodes_and_relationships(
        snapshot_structure
    )
    graph_nodes, graph_relations = get_sorted_lists_of_nodes_and_relationships(
        graph_structure
    )

    # Asserting nodes
    for node in snapshot_nodes:
        assert (
            node == graph_nodes[snapshot_nodes.index(node)]
        ), f"Node {node}\nin snapshot is not equal to graph node on the same index\n{graph_nodes[snapshot_nodes.index(node)]}"

    # Asserting relationships
    for relationship in snapshot_relations:
        assert (
            relationship == graph_relations[snapshot_relations.index(relationship)]
        ), f"Relationship {relationship}\nin snapshot is not equal to graph relationship on the same index\n{graph_relations[snapshot_relations.index(relationship)]}"
