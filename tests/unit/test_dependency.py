from tests.utils import load_test_config
import src.workflow_components.dependency as dependency

load_test_config()


def test_uses_string_analyze():
    test_cases = [
        (
            "actions/checkout@v2",
            False,
            "actions/checkout",
        ),
        (
            "github/codeql-action/analyze@v1",
            False,
            "github/codeql-action/analyze",
        ),
        (
            "./.github/actions/action-setup",
            True,
            "./.github/actions/action-setup",
        ),
        (
            "./.github/actions/build.yml",
            True,
            "./.github/actions/build.yml",
        ),
        (
            "octo-org/this-repo/.github/workflows/workflow-1.yml@latest",
            False,
            "octo-org/this-repo/.github/workflows/workflow-1.yml",
        ),
        (
            "docker://docker.io/library/golang:1.17.1-alpine@sha256:abcd",
            False,
            "docker://docker.io/library/golang:1.17.1-alpine",
        ),
    ]

    for test_case in test_cases:
        uses_string_obj = dependency.UsesString.analyze(test_case[0])
        assert (
            uses_string_obj.is_relative == test_case[1]
            and uses_string_obj.path == test_case[2]
        )
