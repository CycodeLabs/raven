import argparse
import re
import io
from typing import List, Dict, Union, Optional

import yaml
from py2neo.data import Node

from src.storage.redis_connection import RedisConnection
from src.config.config import Config, QUERY_IDS
import src.logger.log as log
from urllib.parse import urlparse, parse_qs


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


def convert_raw_github_url_to_github_com_url(raw_url: str):
    """
    Convert a GitHub raw URL to its corresponding tree URL.
    convert_raw_to_tree_url("https://raw.githubusercontent.com/myorg/myrepo/master/.github/workflows/android.yml")
        >> "https://github.com/myorg/myrepo/tree/master/.github/workflows/android.yml"
    """

    tree_url = raw_url.replace("raw.githubusercontent.com", "github.com")
    if is_url_contains_a_token(tree_url):
        tree_url = tree_url.split("?")[0]

    parts = tree_url.split("/")
    parts.insert(5, "tree")
    return "/".join(parts)


def find_workflow_by_name(repo: str, workflow_name: str) -> str:
    """Tries to find workflow in specified repo,
    with the given workflow name

    Used to create connection based on "workflow_run" trigger (which gives workflow name)
    """
    with RedisConnection(Config.redis_workflows_db) as workflows_db:
        for workflow in workflows_db.get_all_keys():
            workflow = workflow.decode()

            if workflow.startswith(repo):
                data = workflows_db.get_value_from_hash(
                    workflow, Config.redis_data_hash_field_name
                ).decode()

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


def is_url_contains_a_token(url) -> bool:
    """
    Checks if the url contains arguments.
    E.g.:
    is_url_contains_a_token("https://raw.githubusercontent.com/RavenIntegrationTests/astro/main/.github/workflows/ci.yml?token=AAABBBCCC")
        >> True
    is_url_contains_a_token("https://raw.githubusercontent.com/RavenIntegrationTests/astro/main/.github/workflows/ci.yml")
        >> False
    """
    parsed_url = urlparse(url)
    query_parameters = parse_qs(parsed_url.query)

    return "token" in query_parameters


def str_to_bool(s: str) -> bool:
    return bool(int(s))


def raw_str_to_bool(s: str) -> bool:
    return True if s == "true" else False


def validate_query_ids(ids_arg: str) -> list:
    """check if ids argument (ex: "RQ-1,RQ-3") in config.QUERY_IDS.
    return parsed list."""
    if not ids_arg:
        return []

    ids_list = ids_arg.split(",")
    if not set(ids_list).issubset(QUERY_IDS):
        raise argparse.ArgumentTypeError(
            f"Invalid choice: {ids_arg}. Choose from {','.join(QUERY_IDS)}"
        )
    return ids_list
