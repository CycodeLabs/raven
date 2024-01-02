import os
import urllib
from requests import get
from typing import Dict, Any, Optional, Iterator, Optional
from http import HTTPStatus
from src.config.config import Config
import src.logger.log as log

"""
Current rate limiting:

Search API:
- No token: 10 per minute
- With token: 30 per minute

Other standard API (contents):
- With token: 5000 per hour
githubusercontent API - None
"""

BASE_URL = "https://api.github.com"
REPOSITORY_SEARCH_URL = (
    BASE_URL
    + "/search/repositories?q={query}&sort=stars&order=desc&per_page=100&page={page}"
)
ACCOUNT_INFO_URL = BASE_URL + "/users/{account_name}"
USER_REPOSITORY_URL = BASE_URL + "/users/{user_name}/repos?per_page=100&page={page}"
ORGANIZATION_REPOSITORY_URL = (
    BASE_URL + "/orgs/{organization_name}/repos?per_page=100&page={page}"
)
CONTENTS_URL = BASE_URL + "/repos/{repo_path}/contents/{file_path}"

REPOSITORY_QUERY_MIN = "stars:>={min_stars}"
REPOSITORY_QUERY_MIN_MAX = "stars:{min_stars}..{max_stars}"

headers = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.42",
}


def get_account_generator(account_name: str) -> Iterator[str]:
    account_info = get_account_info(account_name=account_name)
    account_type = account_info.get("type")

    if account_type == "User":
        log.info(f"[+] Scanning user: {account_name}")
        return get_user_repository_generator(account_name)

    elif account_type == "Organization":
        log.info(f"[+] Scanning organization: {account_name}")
        return get_organization_repository_generator(account_name)

    else:
        log.error(f"[-] Failed to get account type for {account_name}")
        return None


def get_user_repository_generator(user_name: str) -> Iterator[str]:
    # Quering user repositories is not limited. We loop over each page,
    # and look for more repos. If there are no more repos, we break
    page = 1
    while True:
        log.info(f"[*] Querying page: {page}")
        repos = get_user_repository(user_name=user_name, page=page)
        if repos:
            for repo in repos:
                repo_star_count = int(repo["stargazers_count"])
                log.debug(
                    f"[+] About to download repository: {repo['full_name']}, Stars: {repo_star_count}"
                )
                yield repo["full_name"]
        else:
            break

        page += 1


def get_organization_repository_generator(organization_name: str) -> Iterator[str]:
    # Quering organization repositories is not limited. We loop over each page,
    # and look for more repos. If there are no more repos, we break
    page = 1
    while True:
        log.info(f"[*] Querying page: {page}")
        repos = get_organization_repository(
            organization_name=organization_name, page=page
        )
        if repos:
            for repo in repos:
                repo_star_count = int(repo["stargazers_count"])
                log.debug(
                    f"[+] About to download repository: {repo['full_name']}, Stars: {repo_star_count}"
                )
                yield repo["full_name"]
        else:
            break

        page += 1


def get_repository_generator(
    min_stars: int,
    max_stars: Optional[int] = 0,
) -> Iterator[str]:
    # Github allows only querying up to 1000 results, means 10 pages.

    # In addition, to make wider queries, we going to change the query after each 10 pages.
    # Because our query only do stars count, we can just narrow the stars, and keep querying.
    last_star_count = 0
    while True:
        more_results = False
        for page in range(1, 11):
            log.info(f"[*] Querying page: {page}")
            if not max_stars:
                query = REPOSITORY_QUERY_MIN.format(min_stars=min_stars)
            else:
                query = REPOSITORY_QUERY_MIN_MAX.format(
                    min_stars=min_stars, max_stars=max_stars
                )

            repos = get_repository_search(
                query=query,
                page=page,
            )

            if repos:
                more_results = True
                for repo in repos:
                    last_star_count = int(repo["stargazers_count"])
                    log.debug(
                        f"[+] About to download repository: {repo['full_name']}, Stars: {last_star_count}"
                    )
                    yield repo["full_name"]
            else:
                more_results = False
                break

            page += 1

        if not more_results:
            # Recieved no results. can quit.
            break
        else:
            max_stars = last_star_count + 1


def get_account_info(account_name: str) -> Dict[str, Any]:
    """
    Returns a dictionary with the account information.
    The objects look like this:
    {
        "login": "CycodeLabs",
        "type": "Organization",
        ...
    }
    """
    headers["Authorization"] = f"Token {Config.github_token}"
    r = get(ACCOUNT_INFO_URL.format(account_name=account_name), headers=headers)

    if r.status_code != HTTPStatus.OK:
        log.error(f"[-] Failed fetching repositories for {account_name}")
        raise Exception(f"status code: {r.status_code}. Response: {r.text}")

    return r.json()


def get_user_repository(user_name: str, page: int) -> list[dict]:
    """
    Returns a list of all repositories for the specified user.
    The objects look like this:
    {
        "id": 000000000,
        "node_id": "R_...",
        "name": "example",
        "full_name": "example/example",
        "private": true,
        ...
    }
    """
    headers["Authorization"] = f"Token {Config.github_token}"

    r = get(
        USER_REPOSITORY_URL.format(user_name=user_name, page=page),
        headers=headers,
    )
    if r.status_code != HTTPStatus.OK:
        log.error(f"[-] Failed fetching repositories for {user_name}")
        raise Exception(f"status code: {r.status_code}. Response: {r.text}")

    return r.json()


def get_organization_repository(organization_name: str, page: int) -> list[dict]:
    """
    Returns a list of all repositories for the specified organization.
    The objects look like this:
    {
        "id": 000000000,
        "node_id": "R_...",
        "name": "example",
        "full_name": "example/example",
        "private": true,
        ...
    }
    """
    headers["Authorization"] = f"Token {Config.github_token}"

    r = get(
        ORGANIZATION_REPOSITORY_URL.format(
            organization_name=organization_name, page=page
        ),
        headers=headers,
    )
    if r.status_code != HTTPStatus.OK:
        log.error(f"[-] Failed fetching repositories for {organization_name}")
        raise Exception(f"status code: {r.status_code}. Response: {r.text}")

    return r.json()


def get_repository_search(query: str, page: int = 1) -> Dict[str, Any]:
    headers["Authorization"] = f"Token {Config.github_token}"

    r = get(
        REPOSITORY_SEARCH_URL.format(query=urllib.parse.quote_plus(query), page=page),
        headers=headers,
    )
    if r.status_code != 200:
        log.error(f"status code: {r.status_code}. Response: {r.text}")
        return {}

    return r.json()["items"]


def get_repository_workflows(repo: str) -> Dict[str, str]:
    """Returns list of workflows for the specified repository.
    Returns a dictionary that maps workflow file name, to its donwloadable URL.

    e.g.: crowdin-upload.curriculum.yml ->
    https://raw.githubusercontent.com/freeCodeCamp/freeCodeCamp/main/
    .github/workflows/crowdin-upload.curriculum.yml
    """

    headers["Authorization"] = f"Token {Config.github_token}"

    file_path = ".github/workflows"
    r = get(CONTENTS_URL.format(repo_path=repo, file_path=file_path), headers=headers)
    if r.status_code == 404:
        return {}
    if r.status_code == 403 and int(r.headers["X-RateLimit-Remaining"]) == 0:
        import time

        time_to_sleep = int(r.headers["X-RateLimit-Reset"]) - time.time() + 1
        log.error(
            f"[*] Ratelimit for for contents API depleted. Sleeping {time_to_sleep} seconds"
        )
        time.sleep(time_to_sleep)
        return get_repository_workflows(repo)
    if r.status_code != 200:
        log.error(f"status code: {r.status_code}. Response: {r.text}")
        return {}

    # When we have a single entry, the contents API returns dict instead of list.
    entries = None
    if isinstance(r.json(), list):
        entries = r.json()
    else:
        entries = [r.json()]

    workflows = {}
    for entry in entries:
        if entry["name"].endswith((".yml", ".yaml")):
            workflows[entry["name"]] = entry["download_url"]

    return workflows


def get_repository_composite_action(path: str) -> str:
    """Returns downloadble URL for a composite action in the specific path.

    receives 'path_in_repo' relative path to the repository root to where search the action.yml.
    It should be a directory and not a file. (if file this is a reusable workflow)

    Raises exception if network error occured.
    """
    path_splitted = path.split("/")
    repo = "/".join(path_splitted[:2])
    relative_path = "/".join(path_splitted[2:])

    headers["Authorization"] = f"Token {Config.github_token}"

    for suffix in ["action.yml", "action.yaml"]:
        file_path = os.path.join(relative_path, suffix)
        r = get(
            CONTENTS_URL.format(repo_path=repo, file_path=file_path),
            headers=headers,
        )
        if r.status_code == 404:
            # can be both yml and yaml
            continue

        if r.status_code != 200:
            log.error(f"status code: {r.status_code}. Response: {r.text}")
            continue

        return r.json()["download_url"]


def get_repository_reusable_workflow(path: str) -> str:
    """Returns downlodable URL for a reusable workflows in the specific path.

    Raises exception if network error occured.
    """
    path_splitted = path.split("/")
    repo = "/".join(path_splitted[:2])
    relative_path = "/".join(path_splitted[2:])

    headers["Authorization"] = f"Token {Config.github_token}"

    r = get(
        CONTENTS_URL.format(repo_path=repo, file_path=relative_path),
        headers=headers,
    )
    if r.status_code == 404:
        return
    if r.status_code != 200:
        log.error(f"status code: {r.status_code}. Response: {r.text}")
        return

    return r.json()["download_url"]
