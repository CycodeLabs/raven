from tests.utils import load_test_config
import src.common.utils as utils

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


def test_get_repo_full_name_from_path():
    assert (
        utils.get_repo_name_from_path(
            "edgedb/edgedb-pkg/integration/linux/test/ubuntu-jammy/action.yml"
        )
        == "edgedb/edgedb-pkg"
    )
    assert (
        utils.get_repo_name_from_path(
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
