import re
import io
from typing import List, Dict, Union

import yaml
from py2neo.data import Node

from src.storage.redis_connection import RedisConnection
from src.config.config import Config
import src.logger.log as log


def get_dependencies_in_code(code: str) -> List[str]:
    re_fmt = r"\$\{\{\s*([a-zA-Z0-9\-\._]*)\s*\}\}"
    return [match.group(1) for match in re.finditer(re_fmt, code)]


def convert_dict_to_list(d: Union[Dict, str]) -> List:
    if isinstance(d, dict):
        return [f"{key}:{value}" for key, value in d.items()]
    else:
        return [d]


def convert_workflow_to_unix_path(repo: str, workflow_name: str) -> str:
    return f"{repo}/.github/workflows/{workflow_name}"


def find_workflow_by_name(repo: str, workflow_name: str) -> str:
    """Tries to find workflow in specified repo,
    with the given workflow name

    Used to create connection based on "workflow_run" trigger (which gives workflow name)
    """
    with RedisConnection(Config.redis_workflows_db) as workflows_db:
        for workflow in workflows_db.get_all_keys():
            workflow = workflow.decode()

            if workflow.startswith(repo):
                data = workflows_db.get_string(workflow).decode()

                # PyYAML has issues with tabs.
                data = data.replace("\t", "  ")

                with io.StringIO() as f:
                    f.write(data)
                    f.seek(0)
                    try:
                        obj = yaml.load(f, yaml.loader.Loader)
                    except yaml.scanner.ScannerError as e:
                        log.error(
                            f"[-] Failed loading: {workflow}. Exception: {e}. Skipping..."
                        )
                        return

                # Could happen if the YAML is empty.
                if not obj:
                    return

                if isinstance(obj, str):
                    # Couldn't happen on rare cases.
                    return

                if "name" in obj and obj["name"] == workflow_name:
                    return workflow


def get_repo_name_from_path(path: str) -> str:
    """
    edgedb/edgedb-pkg/integration/linux/test/ubuntu-jammy/action.yml ->
    edgedb/edgedb-pkg

    slsa-framework/slsa-github-generator/.github/workflows/builder_go_slsa3.yml ->
    slsa-framework/slsa-github-generator
    """
    return "/".join(path.split("/")[:2])


def find_uses_strings(workflow_content: str) -> List[str]:
    """Find patterns of usages for composite actions inside the workflow.
    E.g. if it uses "actions/checkout", so "actions/checkout"
    will be part of the returned list.
    """
    re_fmt = r"[ \t]uses:\s*[\'\"]?([0-9a-zA-Z_\:\-/@\.]*)[\'\"]?"
    return [match.group(1) for match in re.finditer(re_fmt, workflow_content)]


def get_all(node_type: str) -> list[Node]:
    """
    Returns all node_type nodes in the graph.
    """
    return Config.graph.get_all(node_type)
