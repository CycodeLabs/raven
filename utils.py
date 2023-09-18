import os
import re
import io
import yaml
from typing import List, Optional, Tuple, Dict, Union

from py2neo.ogm import GraphObject

import config


def save_file(fpath: str, content: str):
    if not os.path.exists(fpath):
        with open(fpath, "w") as f:
            f.write(content)


def get_dependencies_in_code(code: str) -> List[str]:
    re_fmt = r"\$\{\{\s*([a-zA-Z0-9\-\._]*)\s*\}\}"
    return [match.group(1) for match in re.finditer(re_fmt, code)]


def convert_dict_to_list(d: Union[Dict, str]) -> List:
    if isinstance(d, dict):
        return [f"{key}:{value}" for key, value in d.items()]
    else:
        return [d]


def find_workflow_path_by_name(repo_full_name: str, workflow_name: str) -> str:
    """Tries to find workflow in specified repo,
    with the given workflow name

    Used to create connection based on "workflow_run" trigger (which gives workflow name)
    """
    for fname in os.listdir(config.Config.workflow_data_path):
        if get_repo_full_name_from_fname(fname) == repo_full_name:
            fpath = os.path.join(config.Config.workflow_data_path, fname)
            with open(fpath, "r") as f:
                data = f.read()

            # PyYAML has issues with tabs.
            data = data.replace("\t", "  ")

            with io.StringIO() as f:
                f.write(data)
                f.seek(0)
                try:
                    obj = yaml.load(f, yaml.loader.Loader)
                except yaml.scanner.ScannerError as e:
                    print(f"[-] Failed loading: {fpath}. Exception: {e}. Skipping")
                    return

            # Could happen if the YAML is empty.
            if not obj:
                return

            if isinstance(obj, str):
                # Treat it as a symlink
                # TODO
                print(f"[-] Symlink detected: {fpath}. Skipping...")
                return

            if obj["name"] == workflow_name:
                return fpath


def get_repo_full_name_from_fname(fname: str) -> str:
    """
    edgedb|edgedb-pkg|integration|linux|test|ubuntu-jammy|action.yml ->
    edgedb/edgedb-pkg

    slsa-framework|slsa-github-generator|.github|workflows|builder_go_slsa3.yml ->
    slsa-framework/slsa-github-generator
    """
    return "/".join(fname.split("|")[:2])


def get_repo_full_name_from_fpath(fpath: str) -> str:
    """
    data/action/edgedb|edgedb-pkg|integration|linux|test|ubuntu-jammy|action.yml ->
    edgedb/edgedb-pkg

    data/workflows/slsa-framework|slsa-github-generator|.github|workflows|builder_go_slsa3.yml ->
    slsa-framework/slsa-github-generator
    """
    return get_repo_full_name_from_fname(os.path.basename(fpath))


def find_uses_strings(workflow_content: str) -> List[str]:
    """Find patterns of usages for composite actions inside the workflow.
    E.g. if it uses "actions/checkout", so "actions/checkout"
    will be part of the returned list.
    """
    re_fmt = r"[ \t]uses:\s*[\'\"]?([0-9a-zA-Z_\:\-/@\.]*)[\'\"]?"
    return [match.group(1) for match in re.finditer(re_fmt, workflow_content)]


def save_workflow(repo_full_name: str, workflow_name: str, content: str) -> None:
    fpath = convert_workflow_to_file_path(repo_full_name, workflow_name)
    save_file(fpath, content)


def save_action_or_reusable_workflow(full_path: str, content: str) -> None:
    fpath = convert_action_or_reusable_workflow_path_to_file_path(full_path)
    save_file(fpath, content)


def convert_action_or_reusable_workflow_path_to_file_path(full_path: str) -> str:
    # "actions-rs/toolschain" -> "data/actions/actions-rs|toolchain|action.yml"
    # "github/codeql-action/analyze" -> "data/actions/github|codeql-action|analyze|action.yml"
    # "octo/repo/.github/workflows/ci.yml" -> "data/workflows/octo|repo|.github|workflows|ci.yml"

    fname = full_path.replace("/", "|")
    if full_path.endswith((".yml", ".yaml")):
        # Reference to a workflow (including reusable workflow)
        return os.path.join(config.Config.workflow_data_path, fname)
    else:
        # Reference to an action
        fname = fname + "|action.yml"
        return os.path.join(config.Config.action_data_path, fname)


def convert_workflow_to_file_path(repo_full_name: str, workflow_name: str) -> str:
    fname = f"{repo_full_name}|.github|workflows|{workflow_name}"
    fname = fname.replace("/", "|")
    fpath = os.path.join(config.Config.workflow_data_path, fname)
    return fpath


def parse_uses_string(
    uses_string: str, relative_repo_full_name: Optional[str]
) -> Tuple[str, str, str]:
    """Parses the uses string, and extract three variables:
    full_path - absolute path for the file/action
    repo_full_name - repository full name for the file/action
    path_in_repo - relative path in the repository where we can find the file/action

    The uses string could point to:
    - uses: actions/checkout@v3 (normal usage of external action)
    - uses: github/codeql-action/analyze@v1 (external action in a directory)
    - uses: ./.github/actions/action-setup (local external action pointing to action.yml)
    - uses: ./.github/actions/action-install (local external action pointing to a Dockerfile)
    - uses: ./.github/actions/build.yml (reusable workflow in local directory)
    - uses: octo-org/this-repo/.github/workflows/workflow-1.yml@latest (reusable workflow in other directory)
    - uses: docker://docker.io/library/golang:1.17.1-alpine@sha256:... (nothing to download)
    """
    # Ignoring the version
    uses_string_path = uses_string.split("@")[0]
    repo_full_name = None
    path_in_repo = None

    # Get rid of the irrelevant cases
    if uses_string_path.startswith("docker://"):
        # docker image
        repo_full_name = None
        path_in_repo = None
        full_path = None
    # now we need to change the action path to be absolute.
    elif uses_string_path.startswith("./"):
        # local action or local reusable worflow.
        repo_full_name = relative_repo_full_name
        path_in_repo = uses_string_path[2:]
        full_path = repo_full_name + "/" + path_in_repo
    elif len(uses_string_path.split("/")) >= 3:
        # remote action or remote workflow
        repo_full_name = "/".join(uses_string_path.split("/")[:2])
        path_in_repo = "/".join(uses_string_path.split("/")[2:])
        full_path = repo_full_name + "/" + path_in_repo
    else:
        # Regular action: actions/checkout@v3
        repo_full_name = uses_string_path
        path_in_repo = "."
        full_path = repo_full_name

    return repo_full_name, path_in_repo, full_path


def get_obj_from_uses_string(
    uses_string: str, relative_repo_full_name: Optional[str]
) -> Optional[GraphObject]:
    """The uses string can point to many places, and could be found in several places,
    so we decided to exclude it from the main logic.

    It could appear in both composite actions and in workflows (or reusable workflows which have same syntax)
    """
    _, _, full_path = parse_uses_string(
        uses_string=uses_string, relative_repo_full_name=relative_repo_full_name
    )
    if full_path is None:
        print(f"[-] Failed to index {full_path}. Continuing.")
        return None

    fpath = convert_action_or_reusable_workflow_path_to_file_path(full_path)

    if fpath.startswith(config.Config.workflow_data_path):
        # Reusable workflow
        import workflow
        import indexer

        w = workflow.Workflow(None, fpath)
        obj = config.Config.graph.get_object(w)
        if not obj:
            if not os.path.exists(fpath):
                print(
                    f"[-] Failed to index reusable workflow {full_path}. Creating stub node."
                )
                config.Config.graph.push_object(w)
                obj = w
            else:
                indexer.index_workflow_file(fpath)
                obj = config.Config.graph.get_object(w)
    else:
        # CompositeAction
        import composite_action
        import indexer

        ca = composite_action.CompositeAction(None, fpath)
        obj = config.Config.graph.get_object(ca)
        if not obj:
            if not os.path.exists(fpath):
                print(f"[-] Failed to index action {full_path}. Creating stub node.")
                config.Config.graph.push_object(ca)
                obj = ca
            else:
                indexer.index_action_file(fpath)
                obj = config.Config.graph.get_object(ca)
    return obj


def find_or_index_workflow(fpath: str) -> GraphObject:
    import workflow
    import indexer

    w = workflow.Workflow(None, fpath)
    obj = config.Config.graph.get_object(w)
    if not obj:
        indexer.index_workflow_file(fpath)
        obj = config.Config.graph.get_object(w)

    return obj
