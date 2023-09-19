import os
import urllib
from requests import get
from typing import Dict, Any, Optional, Iterator, Optional
from http import HTTPStatus
from config import Config

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
    BASE_URL
    + "/orgs/{organization_name}/repos"
)
CONTENTS_URL = BASE_URL + "/repos/{repo_path}/contents/{file_path}"

REPOSITORY_QUERY_MIN = "stars:>={min_stars}"
REPOSITORY_QUERY_MIN_MAX = "stars:{min_stars}..{max_stars}"

headers = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.42",
}

def get_organization_repository_generator(organization_name: str) -> list[dict]:
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
        ORGANIZATION_REPOSITORY_URL.format(organization_name=organization_name),
        headers=headers,
    )

    if r.status_code != HTTPStatus.OK:
        raise Exception(f"status code: {r.status_code}. Response: {r.text}")
    
    return r.json()


def get_repository_generator(min_stars: int, max_stars: Optional[int]) -> Iterator[str]:
    # Github allows only querying up to 1000 results, means 10 pages.

    # In addition, to make wider queries, we going to change the query after each 10 pages.
    # Because our query only do stars count, we can just narrow the stars, and keep querying.

    # TODO: take care of rate-limiting depletion
    last_star_count = 0
    while True:
        more_results = False
        for page in range(1, 11):
            if not max_stars:
                query = REPOSITORY_QUERY_MIN.format(min_stars=min_stars)
            else:
                query = REPOSITORY_QUERY_MIN_MAX.format(
                    min_stars=min_stars, max_stars=max_stars
                )
            print(f"[*] Querying repository page: {page}, Query: {query}")
            repos = get_repository_search(
                query=query,
                page=page,
            )
            if repos:
                more_results = True
                for repo in repos:
                    last_star_count = int(repo["stargazers_count"])
                    print(
                        f"[+] About to download repository: {repo['full_name']}, Stars: {last_star_count}"
                    )
                    yield repo["full_name"]
            page += 1

        if not more_results:
            # Recieved no results. can quit.
            # TODO: May reached here due to rate-limiting depletion.
            break
        else:
            max_stars = last_star_count + 1


def get_repository_search(query: str, page: int = 1) -> Dict[str, Any]:
    headers["Authorization"] = f"Token {Config.github_token}"

    r = get(
        REPOSITORY_SEARCH_URL.format(query=urllib.parse.quote_plus(query), page=page),
        headers=headers,
    )
    if r.status_code != 200:
        raise Exception(f"status code: {r.status_code}. Response: {r.text}")

    return r.json()["items"]


def get_repository_workflows(repo_path: str) -> Dict[str, str]:
    """Returns list of workflows for the specified repository.
    Returns a dictionary that maps workflow file name, to its donwloadable URL.

    e.g.: crowdin-upload.curriculum.yml ->
    https://raw.githubusercontent.com/freeCodeCamp/freeCodeCamp/main/
    .github/workflows/crowdin-upload.curriculum.yml

    Raises exception if network error occured.
    """
    headers["Authorization"] = f"Token {Config.github_token}"

    file_path = ".github/workflows"
    r = get(
        CONTENTS_URL.format(repo_path=repo_path, file_path=file_path), headers=headers
    )
    if r.status_code == 404:
        return {}
    if r.status_code == 403 and int(r.headers["X-RateLimit-Remaining"]) == 0:
        import time

        time_to_sleep = int(r.headers["X-RateLimit-Reset"]) - time.time() + 1
        print(
            f"[*] Ratelimit for for contents API depleted. Sleeping {time_to_sleep} seconds"
        )
        time.sleep(time_to_sleep)
        return get_repository_workflows(repo_path)
    if r.status_code != 200:
        raise Exception(f"status code: {r.status_code}. Response: {r.text}")

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


def get_repository_composite_action(repo_path: str, path_in_repo: str = ".") -> str:
    """Returns downloadble URL for a composite action in the specific path.

    receives 'path_in_repo' relative path to the repository root to where search the action.yml.
    It should be a directory and not a file. (if file this is a reusable workflow)

    Raises exception if network error occured.
    """
    headers["Authorization"] = f"Token {Config.github_token}"

    for suffix in ["action.yml", "action.yaml"]:
        file_path = os.path.join(path_in_repo, suffix)
        r = get(
            CONTENTS_URL.format(repo_path=repo_path, file_path=file_path),
            headers=headers,
        )
        if r.status_code == 404:
            # can be both yml and yaml
            continue
        if r.status_code != 200:
            raise Exception(f"status code: {r.status_code}. Response: {r.text}")

        return r.json()["download_url"]


def get_repository_reusable_workflow(repo_path: str, path_in_repo: str = ".") -> str:
    """Returns downlodable URL for a reusable workflows in the specific path.

    receives 'path_in_repo' relative path to the repository root to where search the workflow.
    The path should end with .yml or .yaml.

    Raises exception if network error occured.
    """
    headers["Authorization"] = f"Token {Config.github_token}"

    r = get(
        CONTENTS_URL.format(repo_path=repo_path, file_path=path_in_repo),
        headers=headers,
    )
    if r.status_code == 404:
        return None
    if r.status_code != 200:
        raise Exception(f"status code: {r.status_code}. Response: {r.text}")

    return r.json()["download_url"]
