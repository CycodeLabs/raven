from src.config.config import Config
from tabulate import tabulate
from src.reporter import slack_reporter
from os import listdir
from os.path import join
import yaml
from src.queries import Query
from typing import List


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
                tags=detection_info.get("tags"),
                severity=detection_info.get("severity"),
                query=yml_query.get("query"),
            )

            if query.filter():
                queries.append(query)

    return queries


def generate() -> None:
    table_data = []
    queries = get_queries()
    for query in queries:
        workflows = query.run()

        for workflow in workflows:
            table_data.append(
                [
                    query.name,
                    query.severity,
                    query.description,
                    workflow,
                ]
            )

    headers = ["Detection", "Severity", "Description", "Workflow File"]
    table = tabulate(table_data, headers=headers, tablefmt="github")

    print(f"{table}\n")

    if Config.slack:
        if Config.slack_token and Config.channel_id:
            client = slack_reporter.Client(Config.slack_token)
            message = f"RAVEN Security Report\n```\n{table}\n```"
            client.send_message(Config.channel_id, message)

        else:
            print(
                "[x] Please provide slack token and channel id to send report to slack."
            )
