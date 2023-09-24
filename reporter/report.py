from config import Config
from tabulate import tabulate
from reporter import slack


def generate() -> None:
    detections = Config.graph.run_predefined_queries()
    table_data = []

    for detection in detections:
        for result in detection.get("results"):
            table_data.append(
                [
                    detection.get("name"),
                    detection.get("description"),
                    result.get("w.path"),
                ]
            )

    headers = ["Detection", "Description", "Workflow File"]
    table = tabulate(table_data, headers=headers, tablefmt="github")

    print(f"{table}\n")

    if Config.slack:
        if Config.slack_token and Config.channel_id:
            client = slack.Client(Config.slack_token)
            message = f"RAVEN Security Report\n```\n{table}\n```"
            client.send_message(Config.channel_id, message)

        else:
            print(
                "[x] Please provide slack token and channel id to send report to slack."
            )
