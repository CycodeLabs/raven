from py2neo.ogm import GraphObject
import json
from src.config.config import Config
from src.workflow_components.composite_action import CompositeAction
from src.workflow_components.workflow import Workflow
from typing import Tuple, List, Dict, Optional
from tests.integration.integration_consts import START_NODE_INDEX, DEST_NODE_INDEX
from src.common.utils import raw_str_to_bool
from hashlib import md5


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


def get_dicts_differences(dict1: Dict, dict2: Dict) -> Dict:
    """
    Recieves two dictionaries and returns the differences between them.
    """
    keys = set(dict1.keys()).union(set(dict2.keys()))
    differences = {}
    for key in keys:
        if dict1.get(key) != dict2.get(key):
            differences[key] = [dict1.get(key), dict2.get(key)]

    return differences


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
        ), f"Properties of nodes on the same index is not equal\n{get_dicts_differences(node, graph_nodes[snapshot_nodes.index(node)])}\n\nIn snapshot:\n{node}\nIn graph:\n{graph_nodes[snapshot_nodes.index(node)]}"

    # Asserting relationships
    for relationship in snapshot_relations:
        assert (
            relationship == graph_relations[snapshot_relations.index(relationship)]
        ), f"Properties of relationships on the same index of graph and snapshot is not equal\n\n{get_dicts_differences(relationship, graph_relations[snapshot_relations.index(relationship)])}\nIn snapshot:\n{relationship}\nIn graph:\n{graph_relations[snapshot_relations.index(relationship)]}"


def assert_action_inputs(ca: CompositeAction, ca_d: Dict):
    """
    This function asserts that the action inputs are equal to those in the JSON file.
    Each composite action is connected to multiple action inputs.
    Each input contains different properties such as name, default, description, and required.

    Using `ca.inputs.triples()`, we are iterating over all the inputs of the composite action.
    For each input, we check the following:
    1) The ID, name, and URL of the composite action are equal to the ID, name, and URL of the input.
    2) The id of the composite action input is the md5 hash of the composite action id and the input name.
    3) Check that the default, description, and required properties are equal to those in the JSON file.

    Each input is a tuple containing a source node (in this case, will always be the composite action identifier)
    the relation type and the destination node (the input itself identifier).
    """
    for input in ca.composite_action_input.triples():
        ca_d_input = ca_d["inputs"][input[DEST_NODE_INDEX].name]

        assert input[START_NODE_INDEX]._id == ca._id
        assert input[DEST_NODE_INDEX].name == ca_d_input["name"]
        assert input[DEST_NODE_INDEX].url == ca_d["url"]
        assert (
            input[DEST_NODE_INDEX]._id
            == md5(f"{ca._id}_{ca_d_input.get('name')}".encode()).hexdigest()
        )

        if "required" in ca_d_input:
            assert input[DEST_NODE_INDEX].required == raw_str_to_bool(
                ca_d_input["required"]
            )

        if "default" in ca_d_input:
            assert input[DEST_NODE_INDEX].default == ca_d_input["default"]

        if "description" in ca_d_input:
            assert input[DEST_NODE_INDEX].description == ca_d_input["description"]


def assert_reusable_workflow_inputs(w: Workflow, workflow_d: Dict):
    """
    This function asserts that the reusable workflow inputs are equal to those in the JSON file.
    Each reusable workflow is connected to multiple reusable workflow inputs.
    Each input contains different properties such as name, default, description, and required.

    Using `w.reusable_workflow_input.triples()`, we are iterating over all the inputs of the reusable workflow.
    For each input, we check the following:
    1) The ID, name, and URL of the workflow are equal to the ID, name, and URL of the input.
    2) The id of the reusable workflow input is the md5 hash of the workflow id and the input name.
    3) Check that the default, description, and required properties are equal to those in the JSON file.

    Each input is a tuple containing a source node (in this case, will always be the reusable workflow)
    the relation type and the destination node (the input itself identifier).
    """
    for input in w.reusable_workflow_input.triples():
        workflow_d_input = workflow_d["on"]["workflow_call"]["inputs"][
            input[DEST_NODE_INDEX].name
        ]

        assert input[START_NODE_INDEX]._id == w._id
        assert input[DEST_NODE_INDEX].name == workflow_d_input["name"]
        assert input[DEST_NODE_INDEX].url == workflow_d["url"]
        assert (
            input[DEST_NODE_INDEX]._id
            == md5(f"{w._id}_{workflow_d_input.get('name')}".encode()).hexdigest()
        )

        if "required" in workflow_d_input:
            assert input[DEST_NODE_INDEX].required == raw_str_to_bool(
                workflow_d_input["required"]
            )

        if "default" in workflow_d_input:
            assert input[DEST_NODE_INDEX].default == workflow_d_input["default"]

        if "description" in workflow_d_input:
            assert input[DEST_NODE_INDEX].description == workflow_d_input["description"]
