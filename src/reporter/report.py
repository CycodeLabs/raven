from src.config.config import Config
from tabulate import tabulate
from src.reporter import slack_reporter
from os import listdir
from os.path import join
import yaml
from src.detections import Detection
from typing import List


def get_detections() -> List[Detection]:
    detections = []
    for detection_file in listdir(Config.detections_path):
        with open(join(Config.detections_path, detection_file), "r") as raw_detection:
            yml_detection = yaml.safe_load(raw_detection)
            detection_info = yml_detection.get("info")

            detection = Detection(
                id=yml_detection.get("id"),
                name=detection_info.get("name"),
                description=detection_info.get("description"),
                tags=detection_info.get("tags"),
                severity=detection_info.get("severity"),
                query=yml_detection.get("query"),
            )

            if detection.filter():
                detections.append(detection)

    return detections


def generate() -> None:
    table_data = []
    detections = get_detections()
    for detection in detections:
        workflows = detection.run()

        for workflow in workflows:
            table_data.append(
                [
                    detection.name,
                    detection.severity,
                    detection.description,
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
