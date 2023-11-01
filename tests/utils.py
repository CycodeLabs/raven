from src.config.config import Config
from typing import Tuple, List, Dict, Optional
import src.common.utils as utils

from py2neo.ogm import GraphObject


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
    nodes = utils.get_all(node_type)
    if paths:
        return [dict(node) for node in nodes if node.get("path") in paths]
    else:
        return [dict(node) for node in nodes]
