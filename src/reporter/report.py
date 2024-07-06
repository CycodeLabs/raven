from src.config.config import (
    Config,
    REPORT_RAW_FORMAT,
    REPORT_JSON_FORMAT,
    REPORT_SARIF_FORMAT,
    SLACK_REPORTER,
)
from src.reporter import slack_reporter
from src.logger.log import success_exit
from os import listdir
from os.path import join
import yaml
import json
from src.queries import Query
from typing import List


def raw_reporter(queries: List[Query]) -> str:
    report = "\n"

    for query in queries:
        report += f"{query.to_raw()}\n"

    return report


def json_reporter(queries: List[Query]) -> str:
    return json.dumps([query.to_json() for query in queries], indent=4)


def sarif_reporter(queries: List[Query]) -> str:
    # Get the JSON first as it's easier to parse, then create the sarif result.
    json_report = json.loads(json_reporter(queries))
    return json.dumps(convert_json_to_sarif(json_report), indent=4)


def get_queries() -> List[Query]:
    queries = []
    for query_file in listdir(Config.queries_path):
        with open(join(Config.queries_path, query_file), "r") as raw_query:
            yml_query = yaml.safe_load(raw_query)
            detection_info = yml_query.get("info")

            query = Query(
                id=yml_query.get("id"),
                name=detection_info.get("name"),
                description=detection_info.get("description"),
                full_description=detection_info.get("full-description"),
                tags=detection_info.get("tags"),
                severity=detection_info.get("severity"),
                query=yml_query.get("query"),
            )

            if query.filter():
                queries.append(query)

    return queries


def generate() -> None:
    queries = get_queries()
    for query in queries:
        query.run()

    filtered_queries = [query for query in queries if query.result]
    report = ""
    if Config.format == REPORT_RAW_FORMAT:
        report = raw_reporter(filtered_queries)
    elif Config.format == REPORT_JSON_FORMAT:
        report = json_reporter(filtered_queries)
    elif Config.format == REPORT_SARIF_FORMAT:
        report = sarif_reporter(filtered_queries)

    if Config.reporter == SLACK_REPORTER:
        if Config.slack_token and Config.channel_id:
            client = slack_reporter.Client(Config.slack_token)
            message = f"\n{report}\n"
            client.send_report(Config.channel_id, message)

        else:
            print(
                "[x] Please provide slack token and channel id to send report to slack."
            )

    else:
        print(report)

    success_exit()


def convert_json_to_sarif(findings: dict) -> dict:
    all_rules = []
    all_results = []

    # Match severity to CVSS score.
    scores = {
        'critical': 10,
        'high': 8,
        'medium': 6,
        'low': 3,
        'info': 0
    }

    for finding in findings:
        # First add the rules.
        rule = {
            "id": finding["id"],
            "name": finding["name"],
            "shortDescription": {
                "text": finding["description"]
            },
            "fullDescription": {
                "text": finding["full_description"]
            },
            "properties": {
                "security-severity": scores[finding["severity"]],
                "tags": [
                    "security"
                ]
            }
        }

        all_rules.append(rule)

        # Now for each file mentioned in the "result" list, add a finding.
        for result in finding["result"]:
            item = {
                "ruleId": finding["id"],
                "message": {
                    "text": finding["description"]
                },
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": result
                            }
                        }
                    }
                ]
            }

            all_results.append(item)

    return {
        "version": "2.1.0",
        "$schema": "http://json.schemastore.org/sarif-2.1.0.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Raven Security Analyzer",
                        "version": "1.0.0",
                        "informationUri": "https://github.com/CycodeLabs/raven/",
                        "rules": all_rules
                    }
                },
                "results": all_results
            }
        ]
    }
