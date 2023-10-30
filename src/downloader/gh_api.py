import os
import urllib
from requests import get
from typing import Dict, Any, List, Optional, Iterator
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
ORGANIZATION_REPOSITORY_URL = (
    BASE_URL + "/orgs/{organization_name}/repos?per_page=100&page={page}"
)
CONTENTS_URL = BASE_URL + "/repos/{repo_path}/contents/{file_path}"
CONTENTS_BY_REF_URL = BASE_URL + "/repos/{repo_path}/contents/{file_path}?ref={ref}"
TAGS_URL = BASE_URL + "/repos/{repo_path}/tags?per_page=9999"


REPOSITORY_QUERY_MIN = "stars:>={min_stars}"
REPOSITORY_QUERY_MIN_MAX = "stars:{min_stars}..{max_stars}"

ACTION_SUFFIXES = ["action.yml", "action.yaml"]
headers = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.42",
}


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
    # while True:
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


def get_ref_of_tag(repo: str, tag: str) -> Optional[str]:
    """
    This function is used to get the ref of a tag in a repository.
    If the tag is not found, it will return the provided tag as is since it might be a branch name that should be used as tag
    """
    r_tags = get(TAGS_URL.format(repo_path=repo), headers=headers)
    if r_tags.status_code != 200:
        log.error(
            f"Coudln't found tags for repository {repo}. status code: {r_tags.status_code}. Response: {r_tags.text}"
        )
        return

    shas = [d["commit"]["sha"] for d in r_tags.json() if d["name"] == tag]

    # Sometimes the tag is not found, but the provided reference is actually a branch name.
    return shas[0] if len(shas) > 0 else tag


def get_download_url(
    path: str,
    file_suffixes: Optional[List[str]] = None,
    tag: Optional[str] = None,
) -> Optional[str]:
    """
    Retrieves the downloadable URL for a GitHub resource located at the given path.

    Parameters:
    - path (str): The repository path containing the resource, formatted as "owner/repo/relative_path_to_resource".
    - tag (Optional[str]): The version tag of the resource. If None, the latest version is used.
    - file_suffixes (List[str]): List of possible file suffixes that the resource could have (e.g., ["action.yml", "action.yaml"]).

    Returns:
    - Optional[str]: The downloadable URL for the resource. Returns None if the resource is not found or if a network error occurs.

    Raises:
    - Logs an error message if the request to the GitHub API fails.
    """
    splitted_path = path.split("/")
    repo, relative_path = "/".join(splitted_path[:2]), "/".join(splitted_path[2:])

    headers["Authorization"] = f"Token {Config.github_token}"

    # Get ref of commit if tag is provided
    ref = get_ref_of_tag(repo, tag) if tag else None

    files_to_try = (
        [os.path.join(relative_path, fs) for fs in file_suffixes]
        if file_suffixes
        else [relative_path]
    )

    for file_path in files_to_try:
        # If we have a tag, we need to use the contents by ref API to get the correct version of the action.
        # Otherwise, we can use the normal contents API
        action_download_url = (
            CONTENTS_BY_REF_URL.format(repo_path=repo, file_path=file_path, ref=ref)
            if tag
            else CONTENTS_URL.format(repo_path=repo, file_path=file_path)
        )

        r = get(action_download_url, headers=headers)
        if r.status_code == 404:
            continue

        if r.status_code != 200:
            log.error(f"status code: {r.status_code}. Response: {r.text}")
            continue

        return r.json()["download_url"]


def get_repository_composite_action(path: str, tag: Optional[str]) -> str:
    """
    Retrieves the downloadable URL for a specific composite action located at the given path.
    """
    return get_download_url(path, tag=tag, file_suffixes=ACTION_SUFFIXES)


def get_repository_reusable_workflow(path: str, tag: str) -> str:
    """
    Retrieves the downloadable URL for a specific reusable workflow located at the given path.
    """
    return get_download_url(path, tag=tag, file_suffixes=[])
