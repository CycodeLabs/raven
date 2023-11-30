import io

import yaml
from yaml.constructor import Constructor

from src.indexer.utils import (
    get_object_full_name_from_ref_pointers_set,
    REF_INDEX_IN_USES_STRING_SPLIT,
)
from src.storage.redis_connection import RedisConnection
from src.config.config import Config
from src.workflow_components.workflow import Workflow
from src.workflow_components.composite_action import (
    CompositeAction,
    get_composite_action,
)
from tqdm import tqdm
import src.logger.log as log
from src.common.utils import str_to_bool
from src.workflow_components.dependency import UsesString


# A hack to deny PyYAML to convert "on" tags into Python boolean values.
def add_bool(self, node):
    return self.construct_scalar(node)


Constructor.add_constructor("tag:yaml.org,2002:bool", add_bool)


def index_downloaded_workflows_and_actions() -> None:
    index_downloaded_actions()
    index_downloaded_workflows()


def index_downloaded_actions() -> None:
    with RedisConnection(Config.redis_objects_ops_db) as ops_db:
        actions = [
            a.decode()
            for a in ops_db.get_set_values(Config.action_download_history_set)
        ]
        log.info(f"[*] Indexing actions...")
        for action in tqdm(actions, desc="Indexing actions"):
            index_action_file(action)


def index_downloaded_workflows() -> None:
    with RedisConnection(Config.redis_objects_ops_db) as ops_db:
        workflows = [
            w.decode()
            for w in ops_db.get_set_values(Config.workflow_download_history_set)
        ]
        log.info(f"[*] Indexing workflows...")
        for workflow in tqdm(workflows, desc="Indexing workflows"):
            index_workflow_file(workflow)


def index_action_file(action: str) -> None:
    try:
        with RedisConnection(Config.redis_objects_ops_db) as ops_db:
            if ops_db.exists_in_set(Config.action_index_history_set, action):
                return

            action_full_name = get_object_full_name_from_ref_pointers_set(action)

            # In case we already indexed the action with a different ref, we will add the ref and push the object to the neo4j DB to update it
            ca = get_composite_action(*UsesString.split_path_and_ref(action_full_name))
            if ca:
                # Add data or change the node as you wish
                ref = UsesString.split_path_and_ref(action)[1]
                if ref:
                    ca.refs.append(ref)
                Config.graph.push_object(ca)

            # Create new composite action object from the data in redis.
            else:
                with RedisConnection(Config.redis_actions_db) as actions_db:
                    content = actions_db.get_value_from_hash(
                        action_full_name, Config.redis_data_hash_field_name
                    ).decode()
                    url = actions_db.get_value_from_hash(
                        action_full_name, Config.redis_url_hash_field_name
                    ).decode()
                    is_public = str_to_bool(
                        actions_db.get_value_from_hash(
                            action_full_name, Config.redis_is_public_hash_field_name
                        ).decode()
                    )

                # PyYAML has issues with tabs.
                content = content.replace("\t", "  ")

                with io.StringIO() as f:
                    f.write(content)
                    f.seek(0)
                    try:
                        obj = yaml.load(f, yaml.loader.Loader)
                    except yaml.scanner.ScannerError as e:
                        log.error(
                            f"[-] Failed loading: {action_full_name}. Exception: {e}. Skipping..."
                        )
                        return

                # Could happen if the YAML is empty.
                if not obj:
                    return

                if isinstance(obj, str):
                    # TODO: This is a symlink. We should handle it.
                    # Only examples at the moment are for https://github.com/edgedb/edgedb-pkg
                    # E.g., https://github.com/edgedb/edgedb-pkg/blob/master/integration/linux/build/centos-8/action.yml
                    log.debug(f"[-] Symlink detected: {content}. Skipping...")
                    return

                obj["path"], obj["commit_sha"] = UsesString.split_path_and_ref(
                    action_full_name
                )
                obj["url"] = url
                obj["is_public"] = is_public

                ref = UsesString.split_path_and_ref(action)[1]
                if ref:
                    obj["ref"] = ref

                Config.graph.merge_object(CompositeAction.from_dict(obj))
            ops_db.insert_to_set(Config.action_index_history_set, action)
    except Exception as e:
        log.error(f"[-] Error while indexing {action}. {e}")


def index_workflow_file(workflow: str) -> None:
    try:
        with RedisConnection(Config.redis_objects_ops_db) as ops_db:
            if ops_db.exists_in_set(Config.workflow_index_history_set, workflow):
                return

            workflow_full_name = get_object_full_name_from_ref_pointers_set(workflow)
            # In case we already indexed the workflow with a different ref, we will add the ref and push the object to the neo4j DB to update it
            w = get_composite_action(*UsesString.split_path_and_ref(workflow_full_name))
            if w:
                # Add data or change the node as you wish
                ref = UsesString.split_path_and_ref(workflow)[
                    REF_INDEX_IN_USES_STRING_SPLIT
                ]
                if ref:
                    w.refs.append(ref)
                Config.graph.push_object(w)

            with RedisConnection(Config.redis_workflows_db) as workflows_db:
                content = workflows_db.get_value_from_hash(
                    workflow_full_name, Config.redis_data_hash_field_name
                ).decode()
                url = workflows_db.get_value_from_hash(
                    workflow_full_name, Config.redis_url_hash_field_name
                ).decode()
                is_public = str_to_bool(
                    workflows_db.get_value_from_hash(
                        workflow_full_name, Config.redis_is_public_hash_field_name
                    ).decode()
                )

            # PyYAML has issues with tabs.
            content = content.replace("\t", "  ")

            with io.StringIO() as f:
                f.write(content)
                f.seek(0)
                try:
                    obj = yaml.load(f, yaml.loader.Loader)
                except yaml.scanner.ScannerError as e:
                    log.error(
                        f"[-] Failed loading: {workflow_full_name}. Exception: {e}. Skipping..."
                    )
                    return

            # Could happen if the YAML is empty.
            if not obj:
                return

            if isinstance(obj, str):
                # TODO: This is a symlink. We should handle it.
                # Only examples at the moment are for https://github.com/edgedb/edgedb-pkg
                # E.g., https://github.com/edgedb/edgedb-pkg/blob/master/integration/linux/build/centos-8/action.yml
                log.debug(f"[-] Symlink detected: {content}. Skipping...")
                return

            obj["path"], obj["commit_sha"] = UsesString.split_path_and_ref(
                workflow_full_name
            )
            obj["url"] = url
            obj["is_public"] = is_public
            ref = UsesString.split_path_and_ref(workflow)[
                REF_INDEX_IN_USES_STRING_SPLIT
            ]
            if ref:
                obj["ref"] = ref

            Config.graph.merge_object(Workflow.from_dict(obj))
            ops_db.insert_to_set(Config.workflow_index_history_set, workflow)

    except Exception as e:
        log.error(f"[-] Error while indexing {workflow}. {e}")
