from tests.utils import load_test_config
import src.workflow_components.dependency as dependency

load_test_config()


def test_uses_string_analyze_with_file_path():
    test_cases = [
        {
            "path": "actions/checkout@v2",
            "origin_path": "octo-org/this-repo/.github/workflows/workflow-1.yml",
            "ref": "v2",
            "is_relative": False,
            "absolute": "actions/checkout",
            "absolute_with_ref": "actions/checkout@v2",
        },
        {
            "path": ".github/codeql-action/analyze@v1",
            "origin_path": "octo-org/this-repo/.github/workflows/workflow-1.yml",
            "ref": "v1",
            "is_relative": False,
            "absolute": ".github/codeql-action/analyze",
            "absolute_with_ref": ".github/codeql-action/analyze@v1",
        },
        {
            "path": "./.github/actions/action-setup",
            "origin_path": "octo-org/this-repo/.github/workflows/workflow-1.yml",
            "ref": None,
            "is_relative": True,
            "absolute": "octo-org/this-repo/.github/actions/action-setup",
            "absolute_with_ref": "octo-org/this-repo/.github/actions/action-setup",
        },
        {
            "path": "./.github/actions/build.yml",
            "origin_path": "octo-org/this-repo/.github/workflows/workflow-1.yml",
            "ref": None,
            "is_relative": True,
            "absolute": "octo-org/this-repo/.github/actions/build.yml",
            "absolute_with_ref": "octo-org/this-repo/.github/actions/build.yml",
        },
        {
            "path": "./.github/actions/build.yml@dev",
            "origin_path": "octo-org/this-repo/.github/workflows/workflow-1.yml",
            "ref": "dev",
            "is_relative": True,
            "absolute": "octo-org/this-repo/.github/actions/build.yml",
            "absolute_with_ref": "octo-org/this-repo/.github/actions/build.yml@dev",
        },
        {
            "path": "octo-org/this-repo/.github/workflows/workflow-1.yml@latest",
            "origin_path": "octo-org/this-repo/.github/workflows/workflow-1.yml",
            "ref": "latest",
            "is_relative": False,
            "absolute": "octo-org/this-repo/.github/workflows/workflow-1.yml",
            "absolute_with_ref": "octo-org/this-repo/.github/workflows/workflow-1.yml@latest",
        },
        {
            "path": "docker://docker.io/library/golang:1.17.1-alpine@sha256:abcd",
            "origin_path": "octo-org/this-repo/.github/workflows/workflow-1.yml",
            "ref": "sha256:abcd",
            "is_relative": False,
            "absolute": "docker://docker.io/library/golang:1.17.1-alpine",
            "absolute_with_ref": "docker://docker.io/library/golang:1.17.1-alpine@sha256:abcd",
        },
    ]
    for test_case in test_cases:
        uses_string_obj = dependency.UsesString.analyze(
            test_case["path"], test_case["origin_path"]
        )
        assert test_case["ref"] == uses_string_obj.ref
        assert test_case["is_relative"] == uses_string_obj.is_relative
        assert test_case["absolute"] == uses_string_obj.absolute_path
        assert test_case["absolute_with_ref"] == uses_string_obj.absolute_path_with_ref
