from src.workflow_components.parsing_utils import (
    parse_workflow_trigger,
    parse_job_machine,
)


def test_parse_workflow_trigger():
    test_cases = [
        ("push", ["push"]),
        (["push"], ["push"]),
        (["push", "pull_request"], ["push", "pull_request"]),
        (
            {"push": {"branches": ["master"]}},
            ["push"],
        ),
        (None, []),
    ]

    for test_case in test_cases:
        assert parse_workflow_trigger(test_case[0]) == test_case[1]


def test_parse_job_machine():
    test_cases = [
        ("ubuntu-latest", ["ubuntu-latest"]),
        (
            {"labels": ["ubuntu-latest", "self-hosted"]},
            ["ubuntu-latest", "self-hosted"],
        ),
        (["ubuntu-latest", "self-hosted"], ["ubuntu-latest", "self-hosted"]),
        (None, None),
    ]

    for test_case in test_cases:
        assert parse_job_machine(test_case[0]) == test_case[1]
