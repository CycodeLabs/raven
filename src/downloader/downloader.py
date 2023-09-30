from requests import get

from src.config.config import Config
from src.storage.redis_connection import RedisConnection
from src.storage.redis_utils import clean_redis_db
from src.downloader.gh_api import (
    get_repository_generator,
    get_repository_workflows,
    get_repository_composite_action,
    get_repository_reusable_workflow,
)
from src.common.utils import (
    find_uses_strings,
    convert_workflow_to_unix_path,
    get_repo_name_from_path,
)
from src.workflow.dependency import UsesString, UsesStringType
import src.logger.log as log


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
    log.debug("[+] Starting repository iterator")
    generator = get_repository_generator(organization_name=Config.org_name)

    # Clean redis
    if Config.clean_redis:
        clean_redis_db()

    for repo in generator:
        download_workflows_and_actions(repo)


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

    log.info("[+] Starting repository iterator")
    generator = get_repository_generator(Config.min_stars, Config.max_stars)

    # Clean redis
    if Config.clean_redis:
        clean_redis_db()

    for repo in generator:
        download_workflows_and_actions(repo)


def download_workflows_and_actions(repo: str) -> None:
    """The flow is the following:

    - First we enumerate .github/workflows directory for workflows
    - For each such workflow we download it
    - If that workflow contains uses:..., we analyze the string, and download the action or the reusable workflow.
    """
    with RedisConnection(Config.redis_sets_db) as sets_db:
        if sets_db.exists_in_set(Config.workflow_download_history_set, repo):
            log.debug("[!] Already downloaded")
            return

        workflows = get_repository_workflows(repo)
        log.debug(f"[+] Found {len(workflows)} workflows for {repo}")

        for name, url in workflows.items():
            log.debug(f"[+] Fetching {name}")
            resp = get(url, timeout=10)
            if resp.status_code != 200:
                raise Exception(
                    f"status code: {resp.status_code}. Response: {resp.text}"
                )

            # We look for dependant external actions.
            uses_strings = find_uses_strings(resp.text)
            for uses_string in uses_strings:
                download_action_or_reusable_workflow(uses_string=uses_string, repo=repo)

            with RedisConnection(Config.redis_workflows_db) as workflows_db:
                workflow_unix_path = convert_workflow_to_unix_path(repo, name)
                workflows_db.insert_to_string(workflow_unix_path, resp.text)

        sets_db.insert_to_set(Config.workflow_download_history_set, repo)


def download_action_or_reusable_workflow(uses_string: str, repo: str) -> None:
    """Whenever we find that workflow is using a "uses:" string,
    it means we are referencing a composite action or reusable workflow, we try to fetch it.

    We use out utilitiy tooling to parse the uses string, because it can be quite complex.
    """
    with RedisConnection(Config.redis_sets_db) as sets_db:
        uses_string_obj = UsesString.analyze(uses_string=uses_string)
        full_path = uses_string_obj.get_full_path(repo)

        # If already scanned action
        if sets_db.exists_in_set(Config.action_download_history_set, full_path):
            return
        # If already scanned workflow - Have to check workflow db because only it contains the full workflow path.
        with RedisConnection(Config.redis_workflows_db) as workflows_db:
            if workflows_db.get_string(full_path) is not None:
                return

        if uses_string_obj.type == UsesStringType.REUSABLE_WORKFLOW:
            url = get_repository_reusable_workflow(full_path)
        elif uses_string_obj.type == UsesStringType.ACTION:
            url = get_repository_composite_action(full_path)
        else:
            # Can happen with docker references.
            return

        if url is None:
            # Maybe runs a local action that was checked out previously? Maybe the action is executed through a Dockerfile?
            log.error(
                f"[-] Couldn't download the action.yml for the dependent action referenced by '{uses_string}'"
            )
            return

        resp = get(url, timeout=10)
        if resp.status_code != 200:
            raise Exception(f"status code: {resp.status_code}. Response: {resp.text}")

        # We look for dependant external actions.
        uses_strings = find_uses_strings(resp.text)
        new_repo = get_repo_name_from_path(full_path)

        for new_uses_string in uses_strings:
            # Some infinite loop I met in several repositories
            new_full_path = UsesString.analyze(new_uses_string).get_full_path(new_repo)
            if new_full_path == full_path:
                continue

            download_action_or_reusable_workflow(
                uses_string=new_uses_string, repo=new_repo
            )

        if uses_string_obj.type == UsesStringType.REUSABLE_WORKFLOW:
            sets_db.insert_to_set(Config.workflow_download_history_set, full_path)
            with RedisConnection(Config.redis_workflows_db) as workflows_db:
                workflows_db.insert_to_string(full_path, resp.text)
        else:  # UsesStringType.ACTION
            sets_db.insert_to_set(Config.action_download_history_set, full_path)
            with RedisConnection(Config.redis_actions_db) as workflows_db:
                workflows_db.insert_to_string(full_path, resp.text)
