from py2neo import Graph
from py2neo.ogm import GraphObject
from py2neo.data import Node
from typing import Tuple, Optional
import logger


class GraphDb(object):
    def __init__(self, uri, user, password):
        self.graph = Graph(uri, auth=(user, password))

    def push_object(self, obj: GraphObject):
        self.graph.merge(obj)

    def get_object(self, obj: GraphObject) -> Optional[GraphObject]:
        """Tries to find an object in the graph.
        Returns None if wasn't found.
        """
        matched_obj = obj.__class__.match(self.graph, obj._id)
        if not matched_obj.exists():
            return None
        else:
            return matched_obj.first()

    def get_or_create(self, obj: GraphObject) -> Tuple[GraphObject, bool]:
        """Tries to find a similar object using given object _id.
        If found one, returns it, together with True value.
        If not found, inserting the object given, and returns it with False value.
        """
        matched_obj = obj.__class__.match(self.graph, obj._id)
        if not matched_obj.exists():
            logger.warning(
                f"WARNING: We didn't found object {obj._id} of type {obj.__class__.__name__}, so we created it."
            )
            self.graph.push(obj)
            return obj, False
        else:
            return matched_obj.first(), True

    def get_all(self, node_type: str) -> list[Node]:
        """
        Returns all nodeTypes nodes in the graph.
        NodeType:
            1) Job
            2) CompositeAction
            3) Workflow
            4) Step
        """
        return list(self.graph.nodes.match(node_type))

    def clean_graph(self):
        self.graph.delete_all()
