from requests import get
from typing import Optional

from config import Config
from redis_connection import RedisConnection
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
    convert_workflow_to_unix_path
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
    
    # Clean redis
    if Config.clean_redis:
        flush_db(Config.redis_sets_db)
        flush_db(Config.redis_actions_db)
        flush_db(Config.redis_workflows_db)

    for repo_full_name in generator:
        download_workflows_and_actions(repo_full_name)

def download_workflows_and_actions(repo_full_name: str) -> None:
    """The flow is the following:

    - First we enumerate .github/workflows directory for workflows
    - For each such workflow we download it
    - If that workflow contains uses:..., we go to that repository, and download the action.
    """
    with RedisConnection(Config.redis_sets_db) as sets_db:
        if sets_db.exists_in_set(Config.workflow_download_history_set, repo_full_name):
            print("[!] Already downloaded")
            return

        workflows = get_repository_workflows(repo_full_name)
        print(f"[+] Found {len(workflows)} workflows for {repo_full_name}")

        for name, url in workflows.items():
            print(f"[+] Fetching {name}")
            resp = get(url, timeout=10)
            if resp.status_code != 200:
                raise Exception(f"status code: {resp.status_code}. Response: {resp.text}")

            # We look for dependant external actions.
            uses_strings = find_uses_strings(resp.text)
            for uses_string in uses_strings:
                download_action_or_reusable_workflow(
                    uses_string=uses_string, current_repo_full_path=repo_full_name
                )
            
            with RedisConnection(Config.redis_workflows_db) as workflows_db:
                workflow_unix_path = convert_workflow_to_unix_path(repo_full_name, name)
                workflows_db.insert_to_string(workflow_unix_path, resp.text)
                
        sets_db.insert_to_set(Config.workflow_download_history_set, repo_full_name)
        

        # Config.workflow_download_cache.insert_to_cache(repo_full_name)

def download_action_or_reusable_workflow(
    uses_string: str, current_repo_full_path: Optional[str]
) -> None:
    """Whenever we find that workflow is using a "uses:" string,
    it means we are referencing a composite action or reusable workflow, we try to fetch it.

    Action full name includes the reference,
    and could also be referencing a local action, or even reusable workflow.

    We use out utilitiy tooling to parse the uses string, because it can be quite complex.
    """
    with RedisConnection(Config.redis_sets_db) as sets_db:
        repo_full_name, path_in_repo, full_path = parse_uses_string(
            uses_string, current_repo_full_path
        )
        if repo_full_name is None or full_path is None or path_in_repo is None:
            print(
                f"[-] Failed to to parse and get action path from '{uses_string}' (Probably docker image path?)"
            )
            return

        # If already scanned action
        if sets_db.exists_in_set(Config.action_download_history_set, full_path):
            return
        # If already scanned workflow - Have to check workflow db because only it contains the full workflow path.
        with RedisConnection(Config.redis_workflows_db) as workflows_db:
            if workflows_db.get_string(full_path) is not None:
                return
    
        if path_in_repo.endswith((".yml", ".yaml")):
            # indicates a reusable workflow
            is_workflow = True
            url = get_repository_reusable_workflow(repo_full_name, path_in_repo)
        else:
            # indicates an action
            is_workflow = False
            url = get_repository_composite_action(repo_full_name, path_in_repo)

        if url is None:
            print(
                f"[-] Couldn't download the action.yml for the dependent action referenced by '{uses_string}' (Maybe runs a local action that was checked out previously? Maybe the action is executed through a Dockerfile?)"
            )
            return

        resp = get(url, timeout=10)
        if resp.status_code != 200:
            raise Exception(f"status code: {resp.status_code}. Response: {resp.text}")

        # We look for dependant external actions.
        uses_strings = find_uses_strings(resp.text)

        for new_uses_string in uses_strings:
            # Some infinite loop I met in several repositories
            _, _, new_full_path = parse_uses_string(new_uses_string, repo_full_name)
            if new_full_path == full_path:
                continue

            download_action_or_reusable_workflow(
                uses_string=new_uses_string, current_repo_full_path=repo_full_name
            )

        if is_workflow:
            sets_db.insert_to_set(Config.workflow_download_history_set, full_path)
            with RedisConnection(Config.redis_workflows_db) as workflows_db:
                workflows_db.insert_to_string(full_path, resp.text)
        else:
            sets_db.insert_to_set(Config.action_download_history_set, full_path)
            with RedisConnection(Config.redis_actions_db) as workflows_db:
                workflows_db.insert_to_string(full_path, resp.text)
        

def flush_db(db_number) -> None:
# TODO: Move to utils
    with RedisConnection(db_number) as db:
        db.flush_db()