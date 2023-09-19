import io
import os
from traceback import print_exc

import concurrent.futures

import yaml
from yaml.constructor import Constructor

from redis_connection import RedisConnection
from config import Config
from workflow import Workflow
from composite_action import CompositeAction


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
    # with concurrent.futures.ProcessPoolExecutor(
    #     max_workers=Config.num_workers
    # ) as executor:
    #     futures = []
    #     for fname in os.listdir(Config.action_data_path):
    #         fpath = os.path.join(Config.action_data_path, fname)
    #         futures.append(executor.submit(index_action_file, fpath))

    #     num_results = len(futures)
    #     for k, _ in enumerate(concurrent.futures.as_completed(futures)):
    #         print(f"[*] Indexing actions. {k+1}/{num_results}", end="\r")
    with RedisConnection(Config.redis_actions_db) as actions_db:
        actions = [a.decode() for a in actions_db.get_all_keys()]
        for action in actions:
            index_action_file(action)
            print(
                f"[*] Indexing actions. {actions.index(action) + 1}/{len(actions)}", end="\r"
            )


def index_downloaded_workflows() -> None:
    # with concurrent.futures.ProcessPoolExecutor(
    #     max_workers=Config.num_workers
    # ) as executor:
    #     futures = []
    #     for fname in os.listdir(Config.workflow_data_path):
    #         # fpath = os.path.join(Config.workflow_data_path, fname)
    #         fpath = fname
    #         futures.append(executor.submit(index_workflow_file, fpath))

    #     num_results = len(futures)
    #     for k, _ in enumerate(concurrent.futures.as_completed(futures)):
    #         print(f"[*] Indexing workflows. {k+1}/{num_results}", end="\r")

    with RedisConnection(Config.redis_workflows_db) as workflows_db:
        workflows = [w.decode() for w in workflows_db.get_all_keys()] 
        for workflow in workflows:
            index_workflow_file(workflow)
            print(
                f"[*] Indexing workflows. {workflows.index(workflow) + 1}/{len(workflows)}", end="\r"
            )


def index_action_file(action: str) -> None:
    try:
        with RedisConnection(Config.redis_sets_db) as sets_db:
            if sets_db.exists_in_set(Config.action_index_history_set, action):
                return

            with RedisConnection(Config.redis_actions_db) as actions_db:
                content = actions_db.get_string(action).decode()


            # PyYAML has issues with tabs.
            content = content.replace("\t", "  ")

            with io.StringIO() as f:
                f.write(content)
                f.seek(0)
                try:
                    obj = yaml.load(f, yaml.loader.Loader)
                except yaml.scanner.ScannerError as e:
                    print(f"[-] Failed loading: {action}. Exception: {e}. Skipping")
                    return

            # Could happen if the YAML is empty.
            if not obj:
                return

            if isinstance(obj, str):
                # Treat it as a symlink
                # TODO
                print(f"[-] Symlink detected: {content}. Skipping...")
                return

            obj["path"] = action

            Config.graph.push_object(CompositeAction.from_dict(obj))
            sets_db.insert_to_set(Config.action_index_history_set, action)
    except Exception as e:
        print(f"[-] Error while indexing {action}. {e}")
        print_exc()


def index_workflow_file(workflow: str) -> None:
    try:
        with RedisConnection(Config.redis_sets_db) as sets_db:
            if sets_db.exists_in_set(Config.workflow_index_history_set, workflow):
                return

            with RedisConnection(Config.redis_workflows_db) as workflows_db:
                content = workflows_db.get_string(workflow).decode()

            # PyYAML has issues with tabs.
            content = content.replace("\t", "  ")

            with io.StringIO() as f:
                f.write(content)
                f.seek(0)
                try:
                    obj = yaml.load(f, yaml.loader.Loader)
                except yaml.scanner.ScannerError as e:
                    print(f"[-] Failed loading: {workflow}. Exception: {e}. Skipping")
                    return

            # Could happen if the YAML is empty.
            if not obj:
                return

            if isinstance(obj, str):
                # Treat it as a symlink
                # TODO
                print(f"[-] Symlink detected: {content}. Skipping...")
                return
            obj["path"] = workflow
            Config.graph.push_object(Workflow.from_dict(obj))
            sets_db.insert_to_set(Config.workflow_index_history_set, workflow)
    
    except Exception as e:
        print(f"[-] Error while indexing {workflow}. {e}")
        print_exc()


def clean_index() -> None:
    Config.graph.clean_graph()
    with RedisConnection(Config.redis_sets_db) as sets_db:
        sets_db.delete_key(Config.workflow_index_history_set)
        sets_db.delete_key(Config.action_index_history_set)