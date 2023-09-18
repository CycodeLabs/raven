import os
import json
import urllib
from base64 import b64decode, b64encode
from requests import get
from typing import Dict, Any, Optional, List, Iterator, Optional

BASE_URL = "https://api.github.com"
REPOSITORY_SEARCH_URL = BASE_URL + "/search/code?q={query}&per_page=100&page={page}"

HEADERS = {"Authorization": f"Token {os.environ['GITHUB_TOKEN']}"}

REPOSITORY_QUERY = "codesee-map-action"

headers = {"Accept": "application/vnd.github+json"}
headers.update(HEADERS)


for page in range(11, 20):
    r = get(
        REPOSITORY_SEARCH_URL.format(
            query=urllib.parse.quote_plus(REPOSITORY_QUERY), page=page
        ),
        headers=headers,
    )
    d = r.json()

    for entry in d["items"]:
        repo = entry["repository"]
        print(repo["full_name"])
