from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class Client(object):
    def __init__(self, token) -> None:
        self.client = WebClient(token=token)

    def send_message(self, channel_id, message):
        try:
            self.client.chat_postMessage(channel=channel_id, text=message)
            print(f"Report send successfully")

        except SlackApiError as e:
            print(f"Failed to send report: {e.response['error']}")