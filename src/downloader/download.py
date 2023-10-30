from requests import get

from src.config.config import Config
from src.storage.redis_connection import RedisConnection
from src.storage.redis_utils import clean_redis_db
from src.downloader.gh_api import (
    get_repository_generator,
    get_repository_workflows,
    get_repository_composite_action,
    get_repository_reusable_workflow,
    get_organization_repository_generator,
)
from src.common.utils import (
    find_uses_strings,
    convert_workflow_to_unix_path,
    get_repo_name_from_path,
    convert_raw_github_url_to_github_com_url,
    is_url_contains_a_token,
)
from src.workflow_components.dependency import UsesString, UsesStringType
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
    log.debug("[+] Starting organization repository iterator")

    for organization in Config.org_name:
        log.debug(f"[+] Scanning {organization}")
        generator = get_organization_repository_generator(organization)

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
        is_public = 1

        log.debug(f"[+] Found {len(workflows)} workflows for {repo}")
        for name, url in workflows.items():
            if is_url_contains_a_token(url):
                """
                If the URL contains a token, it means it is a private repository.
                """
                log.debug(f"[+] URL contains token argument - private repository")
                is_public = 0

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
                workflows_db.insert_to_hash(
                    workflow_unix_path, Config.redis_data_hash_field_name, resp.text
                )
                workflows_db.insert_to_hash(
                    workflow_unix_path,
                    Config.redis_url_hash_field_name,
                    convert_raw_github_url_to_github_com_url(url),
                )
                workflows_db.insert_to_hash(
                    workflow_unix_path,
                    Config.redis_is_public_hash_field_name,
                    is_public,
                )

        sets_db.insert_to_set(Config.workflow_download_history_set, repo)


def download_action_or_reusable_workflow(uses_string: str, repo: str) -> None:
    """Whenever we find that workflow is using a "uses:" string,
    it means we are referencing a composite action or reusable workflow, we try to fetch it.

    We use out utilitiy tooling to parse the uses string, because it can be quite complex.
    """
    with RedisConnection(Config.redis_sets_db) as sets_db:
        uses_string_obj = UsesString.analyze(uses_string=uses_string)
        absolute_path = uses_string_obj.get_absolute_path(repo)
        is_public = 1

        if uses_string_obj.type == UsesStringType.REUSABLE_WORKFLOW:
            # If already scanned workflow - Have to check workflow db because only it contains the full workflow path.
            with RedisConnection(Config.redis_workflows_db) as workflows_db:
                if (
                    workflows_db.get_value_from_hash(
                        absolute_path, Config.redis_data_hash_field_name
                    )
                    is not None
                ):
                    return

            url = get_repository_reusable_workflow(absolute_path)
        elif uses_string_obj.type == UsesStringType.ACTION:
            # If already scanned action
            if sets_db.exists_in_set(Config.action_download_history_set, absolute_path):
                return
            # TODO: Make pretier
            if uses_string_obj.ref is None:
                url = get_repository_composite_action(absolute_path, None)
            else:
                url = get_repository_composite_action(*absolute_path.split("@"))

        else:
            # Can happen with docker references.
            return

        if url is None:
            # This actions might be a local action, or a docker action.

            if uses_string.startswith("./"):
                log.warning(
                    f"[-] Local action '{uses_string}' not found in '{repo}', skipping."
                )
            elif uses_string_obj.type == UsesStringType.ACTION:
                log.warning(
                    f"[-] Action '{uses_string}' could not be found while scanning repo '{repo}', skipping."
                )
            elif uses_string_obj.type == UsesStringType.REUSABLE_WORKFLOW:
                log.warning(
                    f"[-] Reusable workflow '{uses_string}' could not be found while scanning repo '{repo}', skipping."
                )
            else:
                log.warning(
                    f"[-] Docker Action '{uses_string}' could not be found while scanning repo '{repo}', skipping."
                )
            return

        if is_url_contains_a_token(url):
            log.debug(f"[+] URL contains token argument - private repository")
            is_public = 0

        resp = get(url, timeout=10)
        if resp.status_code != 200:
            raise Exception(f"status code: {resp.status_code}. Response: {resp.text}")

        # We look for dependant external actions.
        uses_strings = find_uses_strings(resp.text)
        new_repo = get_repo_name_from_path(absolute_path)

        for new_uses_string in uses_strings:
            # Some infinite loop I met in several repositories
            new_full_path = UsesString.analyze(new_uses_string).get_absolute_path(
                new_repo
            )
            if new_full_path == absolute_path:
                continue

            download_action_or_reusable_workflow(
                uses_string=new_uses_string, repo=new_repo
            )

        if uses_string_obj.type == UsesStringType.REUSABLE_WORKFLOW:
            sets_db.insert_to_set(Config.workflow_download_history_set, absolute_path)
            with RedisConnection(Config.redis_workflows_db) as workflows_db:
                workflows_db.insert_to_hash(
                    absolute_path, Config.redis_data_hash_field_name, resp.text
                )
                workflows_db.insert_to_hash(
                    absolute_path,
                    Config.redis_url_hash_field_name,
                    convert_raw_github_url_to_github_com_url(url),
                )
                workflows_db.insert_to_hash(
                    full_path,
                    Config.redis_is_public_hash_field_name,
                    is_public,
                )
        else:  # UsesStringType.ACTION
            sets_db.insert_to_set(Config.action_download_history_set, absolute_path)
            with RedisConnection(Config.redis_actions_db) as actions_db:
                actions_db.insert_to_hash(
                    absolute_path, Config.redis_data_hash_field_name, resp.text
                )
                actions_db.insert_to_hash(
                    absolute_path,
                    Config.redis_url_hash_field_name,
                    convert_raw_github_url_to_github_com_url(url),
                )
                actions_db.insert_to_hash(
                    full_path,
                    Config.redis_is_public_hash_field_name,
                    is_public,
                )
