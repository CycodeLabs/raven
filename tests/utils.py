import os
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


def load_test_config():
    Config.load_default_redis_config()
    Config.input_data_dir = "data"
    Config.graph = GraphDbMock()
    Config.workflow_data_path = os.path.join(Config.input_data_dir, "workflows")
    Config.action_data_path = os.path.join(Config.input_data_dir, "actions")
