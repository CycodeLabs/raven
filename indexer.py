import io

import yaml
from yaml.constructor import Constructor

from redis_connection import RedisConnection
from config import Config
from workflow import Workflow
from composite_action import CompositeAction
from tqdm import tqdm
import logger


# A hack to deny PyYAML to convert "on" tags into Python boolean values.
def add_bool(self, node):
    return self.construct_scalar(node)


Constructor.add_constructor("tag:yaml.org,2002:bool", add_bool)


def index_downloaded_workflows_and_actions() -> None:
    if Config.clean_neo4j:
        clean_index()

    index_downloaded_actions()
    index_downloaded_workflows()


def index_downloaded_actions() -> None:
    with RedisConnection(Config.redis_actions_db) as actions_db:
        actions = [a.decode() for a in actions_db.get_all_keys()]
        logger.info(f"[*] Indexing actions...")
        for action in tqdm(actions, desc="Indexing actions"):
            index_action_file(action)


def index_downloaded_workflows() -> None:
    with RedisConnection(Config.redis_workflows_db) as workflows_db:
        workflows = [w.decode() for w in workflows_db.get_all_keys()]
        logger.info(f"[*] Indexing workflows...")
        for workflow in tqdm(workflows, desc="Indexing workflows"):
            index_workflow_file(workflow)


def index_action_file(action: str) -> None:
    try:
        with RedisConnection(Config.redis_sets_db) as sets_db:
            if sets_db.exists_in_set(Config.action_index_history_set, action):
                return

            with RedisConnection(Config.redis_actions_db) as actions_db:
                content = actions_db.get_value_from_hash(
                    action, Config.redis_data_hash_field_name
                ).decode()
                url = actions_db.get_value_from_hash(
                    action, Config.redis_url_hash_field_name
                ).decode()

            # PyYAML has issues with tabs.
            content = content.replace("\t", "  ")

            with io.StringIO() as f:
                f.write(content)
                f.seek(0)
                try:
                    obj = yaml.load(f, yaml.loader.Loader)
                except yaml.scanner.ScannerError as e:
                    logger.error(
                        f"[-] Failed loading: {action}. Exception: {e}. Skipping..."
                    )
                    return

            # Could happen if the YAML is empty.
            if not obj:
                return

            if isinstance(obj, str):
                # TODO: This is a symlink. We should handle it.
                # Only examples at the moment are for https://github.com/edgedb/edgedb-pkg
                # E.g. https://github.com/edgedb/edgedb-pkg/blob/master/integration/linux/build/centos-8/action.yml
                logger.debug(f"[-] Symlink detected: {content}. Skipping...")
                return

            obj["path"] = action
            obj["url"] = url

            Config.graph.push_object(CompositeAction.from_dict(obj))
            sets_db.insert_to_set(Config.action_index_history_set, action)
    except Exception as e:
        logger.error(f"[-] Error while indexing {action}. {e}")


def index_workflow_file(workflow: str) -> None:
    try:
        with RedisConnection(Config.redis_sets_db) as sets_db:
            if sets_db.exists_in_set(Config.workflow_index_history_set, workflow):
                return

            with RedisConnection(Config.redis_workflows_db) as workflows_db:
                content = workflows_db.get_value_from_hash(
                    workflow, Config.redis_data_hash_field_name
                ).decode()
                url = workflows_db.get_value_from_hash(
                    workflow, Config.redis_url_hash_field_name
                ).decode()

            # PyYAML has issues with tabs.
            content = content.replace("\t", "  ")

            with io.StringIO() as f:
                f.write(content)
                f.seek(0)
                try:
                    obj = yaml.load(f, yaml.loader.Loader)
                except yaml.scanner.ScannerError as e:
                    logger.error(
                        f"[-] Failed loading: {workflow}. Exception: {e}. Skipping..."
                    )
                    return

            # Could happen if the YAML is empty.
            if not obj:
                return

            if isinstance(obj, str):
                # TODO: This is a symlink. We should handle it.
                # Only examples at the moment are for https://github.com/edgedb/edgedb-pkg
                # E.g. https://github.com/edgedb/edgedb-pkg/blob/master/integration/linux/build/centos-8/action.yml
                logger.debug(f"[-] Symlink detected: {content}. Skipping...")
                return

            obj["path"] = workflow
            obj["url"] = url

            Config.graph.push_object(Workflow.from_dict(obj))
            sets_db.insert_to_set(Config.workflow_index_history_set, workflow)

    except Exception as e:
        logger.error(f"[-] Error while indexing {workflow}. {e}")


def clean_index() -> None:
    Config.graph.clean_graph()
    with RedisConnection(Config.redis_sets_db) as sets_db:
        sets_db.delete_key(Config.workflow_index_history_set)
        sets_db.delete_key(Config.action_index_history_set)
