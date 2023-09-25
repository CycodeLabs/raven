from config import Config
from typing import Tuple, Optional

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
