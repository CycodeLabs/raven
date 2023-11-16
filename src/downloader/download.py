from requests import get

from src.config.config import Config
from src.storage.redis_connection import RedisConnection
from src.downloader.utils import (
    insert_workflow_or_action_to_redis,
    add_ref_pointer_to_redis,
)
from src.downloader.gh_api import (
    get_repository_generator,
    get_repository_workflows,
    get_download_url_for_composite_action,
    get_download_url_for_workflow,
    get_organization_repository_generator,
)
from src.common.utils import (
    find_uses_strings,
    convert_workflow_to_unix_path,
    get_repo_name_from_path,
    convert_raw_github_url_to_github_com_url,
    convert_path_and_commit_sha_to_absolute_path,
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
    with RedisConnection(Config.redis_objects_ops_db) as ops_db:
        if ops_db.exists_in_set(Config.workflow_download_history_set, repo):
            log.debug(f"[!] Repo {repo} already scanned, skipping.")
            return

    workflows = get_repository_workflows(repo)
    is_public = 1
    log.debug(f"[+] Found {len(workflows)} workflows for {repo}")

    with RedisConnection(Config.redis_objects_ops_db) as ops_db:
        for name, url in workflows.items():
            workflow_path = convert_workflow_to_unix_path(repo, name)
            if ops_db.exists_in_set(Config.workflow_download_history_set, repo):
                log.debug("[!] Already downloaded")
                continue

            if is_url_contains_a_token(url):
                """
                If the URL contains a token, it means it is a private repository.
                """
                log.debug(f"[+] URL contains token argument - private repository")
                is_public = 0

            download_url, commit_sha = get_download_url_for_workflow(
                workflow_path, None
            )

            log.debug(f"[+] Fetching {workflow_path}")
            resp = get(download_url, timeout=10)

            if resp.status_code != 200:
                raise Exception(
                    f"status code: {resp.status_code}. Response: {resp.text}"
                )

            # We look for dependant external actions.
            uses_strings = find_uses_strings(resp.text)
            for uses_string in uses_strings:
                download_action_or_reusable_workflow(uses_string=uses_string, repo=repo)

            # Save workflow to redis
            commit_sha_path = convert_path_and_commit_sha_to_absolute_path(
                workflow_path, commit_sha
            )
            github_url = convert_raw_github_url_to_github_com_url(download_url)
            insert_workflow_or_action_to_redis(
                db=Config.redis_workflows_db,
                object_path=commit_sha_path,
                data=resp.text,
                github_url=github_url,
                is_public=is_public,
            )

            # In the future, ref will be with commit sha
            add_ref_pointer_to_redis(workflow_path, commit_sha_path)
            ops_db.insert_to_set(Config.workflow_download_history_set, workflow_path)


def download_action_or_reusable_workflow(uses_string: str, repo: str) -> None:
    """Whenever we find that workflow is using a "uses:" string,
    it means we are referencing a composite action or reusable workflow, we try to fetch it.

    We use out utilitiy tooling to parse the uses string, because it can be quite complex.
    """

    with RedisConnection(Config.redis_objects_ops_db) as ops_db:
        uses_string_obj = UsesString.analyze(uses_string, repo)
        absolute_path_with_ref = uses_string_obj.absolute_path_with_ref
        is_public = 1

        # If already scanned object - check in pointer db
        if (
            ops_db.get_value_from_hash(Config.ref_pointers_hash, absolute_path_with_ref)
            is not None
        ):
            return

        if uses_string_obj.type == UsesStringType.REUSABLE_WORKFLOW:
            download_url, commit_sha = get_download_url_for_workflow(
                uses_string_obj.absolute_path, uses_string_obj.ref
            )
        elif uses_string_obj.type == UsesStringType.ACTION:
            download_url, commit_sha = get_download_url_for_composite_action(
                uses_string_obj.absolute_path, uses_string_obj.ref
            )
        else:
            # Can happen with docker references.
            return

        if download_url is None:
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

        if is_url_contains_a_token(download_url):
            log.debug(f"[+] URL contains token argument - private repository")
            is_public = 0

        resp = get(download_url, timeout=10)
        if resp.status_code != 200:
            raise Exception(f"status code: {resp.status_code}. Response: {resp.text}")

        # We look for dependant external actions.
        uses_strings = find_uses_strings(resp.text)

        new_repo = get_repo_name_from_path(absolute_path_with_ref)
        for new_uses_string in uses_strings:
            # Some infinite loop I met in several repositories
            new_full_path = UsesString.analyze(
                new_uses_string, new_repo
            ).absolute_path_with_ref
            if new_full_path == absolute_path_with_ref:
                continue

            download_action_or_reusable_workflow(
                uses_string=new_uses_string, repo=new_repo
            )

        commit_sha_path = convert_path_and_commit_sha_to_absolute_path(
            uses_string_obj.absolute_path, commit_sha
        )
        if uses_string_obj.type == UsesStringType.REUSABLE_WORKFLOW:
            ops_db.insert_to_set(
                Config.workflow_download_history_set, absolute_path_with_ref
            )

            insert_workflow_or_action_to_redis(
                db=Config.redis_workflows_db,
                object_path=commit_sha_path,
                data=resp.text,
                github_url=convert_raw_github_url_to_github_com_url(download_url),
                is_public=is_public,
            )
            # In the future, ref will be with commit sha
            add_ref_pointer_to_redis(absolute_path_with_ref, commit_sha_path)
        else:  # UsesStringType.ACTION
            ops_db.insert_to_set(
                Config.action_download_history_set, absolute_path_with_ref
            )
            insert_workflow_or_action_to_redis(
                db=Config.redis_actions_db,
                object_path=commit_sha_path,
                data=resp.text,
                github_url=convert_raw_github_url_to_github_com_url(download_url),
                is_public=is_public,
            )
            # In the future, ref will be with commit sha
            add_ref_pointer_to_redis(absolute_path_with_ref, commit_sha_path)
