from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class Client(object):
    def __init__(self, token) -> None:
        self.client = WebClient(token=token)

    def send_report(self, channel_id, message):
        try:
            self.client.files_upload_v2(
                channel=channel_id,
                filename=f"raven_report",
                content=message,
                initial_comment="RAVEN Security Report",
            )
            print(f"[x] Report sent successfully")

        except SlackApiError as e:
            print(f"[x] Failed to send report: {e.response['error']}")
