import os
from enum import Enum
from typing import Optional

from src.common.utils import get_repo_name_from_path


class UsesStringType(Enum):
    ACTION = 1
    REUSABLE_WORKFLOW = 2
    DOCKER = 3


class UsesString:
    def __init__(
        self,
        absolute_path: str,
        type: UsesStringType,
        is_relative: bool = False,
        ref: Optional[str] = None,
    ):
        self.type = type
        self.absolute_path = absolute_path
        self.ref = ref
        self.is_relative = is_relative

    @property
    def absolute_path_with_ref(self):
        """
        If the resource has a ref, it will be appended to the path.
        """
        return f"{self.absolute_path}@{self.ref}" if self.ref else self.absolute_path

    @staticmethod
    def analyze(uses_string: str, extratct_repo_path: str = None) -> "UsesString":
        """
        Parses the uses string to extract relevant information.

        The uses string could point to:
        - uses: actions/checkout@v3 (normal usage of external action)
        - uses: github/codeql-action/analyze@v1 (external action in a directory)
        - uses: ./.github/actions/action-setup (local external action pointing to action.yml)
        - uses: ./.github/actions/action-install (local external action pointing to a Dockerfile)
        - uses: ./.github/actions/build.yml (reusable workflow in local directory)
        - uses: octo-org/this-repo/.github/workflows/workflow-1.yml@latest (reusable workflow in other directory)
        - uses: docker://docker.io/library/golang:1.17.1-alpine@sha256:... (nothing to download)

        Parameters:
        - uses_string (str): The input uses string from a workflow file.

        Returns:
        - UsesString: An object containing the parsed information.
        """
        raw_path, ref = UsesString.split_path_and_ref(uses_string)
        type = UsesString.determine_type(raw_path)
        is_relative = raw_path.startswith("./")
        absolute_path = UsesString.calculate_absolute_path(
            raw_path, extratct_repo_path, is_relative
        )

        return UsesString(absolute_path, type, is_relative=is_relative, ref=ref)

    @staticmethod
    def split_path_and_ref(uses_string: str) -> (str, Optional[str]):
        """Split the uses string into path and reference."""
        parts = uses_string.split("@")
        ref = parts[1] if len(parts) > 1 else None
        return (parts[0], ref)

    @staticmethod
    def determine_type(path: str) -> UsesStringType:
        """Determine the type based on the path."""
        if path.startswith("docker://"):
            return UsesStringType.DOCKER
        if path.endswith((".yml", ".yaml")):
            return UsesStringType.REUSABLE_WORKFLOW
        return UsesStringType.ACTION

    @staticmethod
    def calculate_absolute_path(
        file_path: str, extratct_repo_path: str, is_relative: bool
    ) -> str:
        """
        Calculates the full path for a given action or reusable workflow.
        It will get rid of the relative path (e.g., "..", "./", etc.) and return the full path.
        It will include the repo if the path is relative.
        """

        if not is_relative:
            return file_path

        # Extract repository path and evaluate relative path (e.g., "..", "./", etc.).
        repo = get_repo_name_from_path(extratct_repo_path)
        return os.path.relpath(os.path.abspath(os.path.join(repo, file_path)))
