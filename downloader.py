from requests import get
from typing import Optional

from config import Config
from gh_api import (
    get_organization_repository_generator,
    get_repository_generator,
    get_repository_workflows,
    get_repository_composite_action,
    get_repository_reusable_workflow,
)
from utils import (
    find_uses_strings,
    save_workflow,
    save_action_or_reusable_workflow,
    parse_uses_string,
)


def download_org_workflows_and_actions() -> None:
    """Iterating all organization repositories through Github API.

    For each repository we enumerating the .github/workflows directory,
    and downloading all the workflows.
    In addition if the repository contains action.yml file, it means it is a composite action,
    so we download it as well.

    For each such workflow we also scan if it uses additional external actions.
    If so, we download these as well.

    We are trying to cache the downloads as much as we can to reduce redundant download attempts.
    """
    repositories = get_organization_repository_generator(Config.org_name)

    for repository in repositories:
        download_workflows_and_actions(repository.get('full_name'))


def download_all_workflows_and_actions() -> None:
    """Iterating all repositories through Github search API.

    For each repository we enumerating the .github/workflows directory,
    and downloading all the workflows.
    In addition if the repository contains action.yml file, it means it is a composite action,
    so we download it as well.

    For each such workflow we also scan if it uses additional external actions.
    If so, we download these as well.

    We are trying to cache the downloads as much as we can to reduce redundant download attempts.
    """
    print("[+] Starting repository iterator")
    generator = get_repository_generator(Config.min_stars, Config.max_stars)

    for repo_full_name in generator:
        download_workflows_and_actions(repo_full_name)


def download_workflows_and_actions(repo_full_name: str) -> None:
    """The flow is the following:

    - First we enumerate .github/workflows directory for workflows
    - For each such workflow we download it
    - If that workflow contains uses:..., we go to that repository, and download the action.
    """
    if Config.workflow_download_cache.exists_in_cache(repo_full_name):
        print("[!] Already downloaded")
        return

    workflows = get_repository_workflows(repo_full_name)
    print(f"[+] Found {len(workflows)} workflows for {repo_full_name}")

    for name, url in workflows.items():
        print(f"[+] Fetching {name}")
        r = get(url, timeout=10)
        if r.status_code != 200:
            raise Exception(f"status code: {r.status_code}. Response: {r.text}")

        # We look for dependant external actions.
        uses_strings = find_uses_strings(r.text)
        for uses_string in uses_strings:
            download_action_or_reusable_workflow(
                uses_string=uses_string, current_repo_full_path=repo_full_name
            )
        save_workflow(repo_full_name, name, r.text)

    Config.workflow_download_cache.insert_to_cache(repo_full_name)


def download_action_or_reusable_workflow(
    uses_string: str, current_repo_full_path: Optional[str]
) -> None:
    """Whenever we find that workflow is using a "uses:" string,
    it means we are referencing a composite action or reusable workflow, we try to fetch it.

    Action full name includes the reference,
    and could also be referencing a local action, or even reusable workflow.

    We use out utilitiy tooling to parse the uses string, because it can be quite complex.
    """
    repo_full_name, path_in_repo, full_path = parse_uses_string(
        uses_string, current_repo_full_path
    )
    if repo_full_name is None or full_path is None or path_in_repo is None:
        print(
            f"[-] Failed to to parse and get action path from '{uses_string}' (Probably docker image path?)"
        )
        return

    if Config.action_download_cache.exists_in_cache(full_path):
        return

    if path_in_repo.endswith((".yml", ".yaml")):
        # indicates a reusable workflow
        url = get_repository_reusable_workflow(repo_full_name, path_in_repo)
    else:
        # indicates an action
        url = get_repository_composite_action(repo_full_name, path_in_repo)

    if url is None:
        print(
            f"[-] Couldn't download the action.yml for the dependent action referenced by '{uses_string}' (Maybe runs a local action that was checked out previously? Maybe the action is executed through a Dockerfile?)"
        )
        return

    r = get(url, timeout=10)
    if r.status_code != 200:
        raise Exception(f"status code: {r.status_code}. Response: {r.text}")

    # We look for dependant external actions.
    uses_strings = find_uses_strings(r.text)

    for new_uses_string in uses_strings:
        # Some infinite loop I met in several repositories
        _, _, new_full_path = parse_uses_string(new_uses_string, repo_full_name)
        if new_full_path == full_path:
            continue

        download_action_or_reusable_workflow(
            uses_string=new_uses_string, current_repo_full_path=repo_full_name
        )

    save_action_or_reusable_workflow(full_path, r.text)
    Config.action_download_cache.insert_to_cache(full_path)