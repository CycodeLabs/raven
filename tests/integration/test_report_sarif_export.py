import os
import json
from tests.tests_init import init_integration_env
from src.reporter.report import generate as report_generate
from src.config.config import Config


def test_report_sarif_export(tmp_path) -> None:
    init_integration_env()

    assert os.path.isfile(Config.output) is False
    report_generate()
    assert os.path.isfile(Config.output) is True

    with open(Config.output, "r") as file:
        content = file.read()

    os.remove(Config.output)

    sarif = json.loads(content)

    driver = sarif["runs"][0]["tool"]["driver"]
    rules = driver["rules"]
    results = sarif["runs"][0]["results"]

    assert driver["name"] == "Raven Security Analyzer"
    assert len(rules) == 1
    assert rules[0]["id"] == "RQ-11"
    assert rules[0]["name"] == "Title Context Injection"

    assert len(results) == 1
    assert results[0]["ruleId"] == "RQ-11"
    assert len(results[0]["locations"]) == 1
    assert results[0]["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] == "https://github.com/RavenIntegrationTests/Integration-1/tree/main/.github/workflows/integration-workflow.yml"