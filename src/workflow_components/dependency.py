import os
from enum import Enum

from src.common.utils import get_repo_name_from_path


class UsesStringType(Enum):
    ACTION = 1
    REUSABLE_WORKFLOW = 2
    DOCKER = 3


class UsesString(object):
    type: UsesStringType
    path: str  # E.g., actions/checkout, ./.github/actions/action-setup
    ref: str  # E.g., v3. Can be a branch name, tag name, or commit SHA
    is_relative: bool

    @staticmethod
    def analyze(uses_string: str) -> "UsesString":
        """Parses the uses string, and extract relevant information:
        - Whether path is relative or absolute
        - Reference type (reusable workflow/action/docker)
        - path and ref

        If analyzed path is relative, the full path should be fetched using `get_full_path`.

        The uses string could point to:
        - uses: actions/checkout@v3 (normal usage of external action)
        - uses: github/codeql-action/analyze@v1 (external action in a directory)
        - uses: ./.github/actions/action-setup (local external action pointing to action.yml)
        - uses: ./.github/actions/action-install (local external action pointing to a Dockerfile)
        - uses: ./.github/actions/build.yml (reusable workflow in local directory)
        - uses: octo-org/this-repo/.github/workflows/workflow-1.yml@latest (reusable workflow in other directory)
        - uses: docker://docker.io/library/golang:1.17.1-alpine@sha256:... (nothing to download)
        """
        uses_string_obj = UsesString()
        uses_string_obj.is_relative = False

        uses_string_splitted = uses_string.split("@")
        uses_string_obj.path = uses_string_splitted[0]
        if len(uses_string_splitted) > 1:
            uses_string_obj.ref = uses_string_splitted[1]

        # Get rid of the irrelevant cases
        if uses_string_obj.path.startswith("docker://"):
            uses_string_obj.type = UsesStringType.DOCKER
            return uses_string_obj

        if uses_string_obj.path.endswith(".yml") or uses_string_obj.path.endswith(
            ".yaml"
        ):
            uses_string_obj.type = UsesStringType.REUSABLE_WORKFLOW
        else:
            uses_string_obj.type = UsesStringType.ACTION

        if uses_string_obj.path.startswith("./"):
            # local action or local reusable workflow
            uses_string_obj.is_relative = True
            return uses_string_obj

        # remote action or remote reusable workflow
        return uses_string_obj

    def get_full_path(self, file_path: str) -> str:
        """If the action or reusable workflow path is a relative path,
        to calculate the full path we need the current repository where is was found.
        """
        if not self.is_relative:
            return self.path
        # We care only for the repository path, so we take the first two elements.

        repo = get_repo_name_from_path(file_path)
        # This is a trick to evaluate the path (e.g., "..", "./", etc.)
        return os.path.relpath(os.path.abspath(os.path.join(repo, self.path)))
