from tests.utils import load_test_config
import utils

load_test_config()


def test_get_dependencies_in_code():
    test_cases = [
        ("this is ${{github.event.issue.title}}", "github.event.issue.title"),
        ("this is ${{    github.event.issue.title}}", "github.event.issue.title"),
        ("this is ${{github.event.issue-title}}", "github.event.issue-title"),
        ("this is ${{github.event.issue_title}}", "github.event.issue_title"),
        ("this is\n\n${{github.event.issue.title}}\n", "github.event.issue.title"),
    ]

    for test_case in test_cases:
        assert utils.get_dependencies_in_code(test_case[0]) == [test_case[1]]


def test_convert_dict_to_list():
    test_cases = [
        ({"a": "b"}, ["a:b"]),
        ({"a": "b", "c": "d"}, ["a:b", "c:d"]),
        ("a:b", ["a:b"]),
    ]

    for test_case in test_cases:
        assert utils.convert_dict_to_list(test_case[0]) == test_case[1]


def test_get_repo_full_name_from_fname():
    assert (
        utils.get_repo_full_name_from_fname(
            "edgedb/edgedb-pkg/integration/linux/test/ubuntu-jammy/action.yml"
        )
        == "edgedb/edgedb-pkg"
    )
    assert (
        utils.get_repo_full_name_from_fname(
            "slsa-framework/slsa-github-generator/.github/workflows/builder_go_slsa3.yml"
        )
        == "slsa-framework/slsa-github-generator"
    )


def test_get_repo_full_name_from_fpath():
    assert (
        utils.get_repo_full_name_from_fpath(
            "edgedb/edgedb-pkg/integration/linux/test/ubuntu-jammy/action.yml"
        )
        == "edgedb/edgedb-pkg"
    )
    assert (
        utils.get_repo_full_name_from_fpath(
            "slsa-framework/slsa-github-generator/.github/workflows/builder_go_slsa3.yml"
        )
        == "slsa-framework/slsa-github-generator"
    )


def test_find_uses_strings():
    test_cases = [
        (" uses: actions/checkout@v2", ["actions/checkout@v2"]),
        (" uses: actions/checkout@abcd", ["actions/checkout@abcd"]),
        (" uses: actions/checkout@side-branch", ["actions/checkout@side-branch"]),
        (
            " uses: .github/workflows/my-workflow.yml@main",
            [".github/workflows/my-workflow.yml@main"],
        ),
        (
            " uses: actions/checkout@v2\n uses: actions/checkout@v1",
            ["actions/checkout@v2", "actions/checkout@v1"],
        ),
    ]

    for test_case in test_cases:
        assert utils.find_uses_strings(test_case[0]) == test_case[1]


# Deprecated
# def test_convert_action_or_reusable_workflow_path_to_file_path():
#     test_cases = [
#         ("actions-rs/toolschain", "actions/actions-rs/toolschain/action.yml"),
#         (
#             "github/codeql-action/analyze",
#             "actions/github/codeql-action/analyze/action.yml",
#         ),
#         (
#             "octo/repo/.github/workflows/ci.yml",
#             "workflows/octo/repo/.github/workflows/ci.yml",
#         ),
#     ]

#     for test_case in test_cases:
#         assert (
#             utils.convert_action_or_reusable_workflow_path_to_file_path(test_case[0])
#             == test_case[1]
#         )


# Deprecated
# def test_convert_workflow_to_file_path():
#     test_cases = [
#         (
#             "myorg/myrepo",
#             "myworkflow.yml",
#             "workflows/myorg/myrepo/.github/workflows/myworkflow.yml",
#         ),
#     ]

#     for test_case in test_cases:
#         assert (
#             utils.convert_workflow_to_file_path(test_case[0], test_case[1])
#             == test_case[2]
#         )


def test_parse_uses_string():
    test_cases = [
        (
            "actions/checkout@v2",
            "actions/checkout",
            ".",
            "actions/checkout",
        ),
        (
            "github/codeql-action/analyze@v1",
            "github/codeql-action",
            "analyze",
            "github/codeql-action/analyze",
        ),
        (
            "./.github/actions/action-setup",
            "myorg/myrepo",
            ".github/actions/action-setup",
            "myorg/myrepo/.github/actions/action-setup",
        ),
        (
            "./.github/actions/build.yml",
            "myorg/myrepo",
            ".github/actions/build.yml",
            "myorg/myrepo/.github/actions/build.yml",
        ),
        (
            "octo-org/this-repo/.github/workflows/workflow-1.yml@latest",
            "octo-org/this-repo",
            ".github/workflows/workflow-1.yml",
            "octo-org/this-repo/.github/workflows/workflow-1.yml",
        ),
        (
            "docker://docker.io/library/golang:1.17.1-alpine@sha256:abcd",
            None,
            None,
            None,
        ),
    ]

    for test_case in test_cases:
        assert utils.parse_uses_string(test_case[0], "myorg/myrepo") == (
            test_case[1],
            test_case[2],
            test_case[3],
        )
