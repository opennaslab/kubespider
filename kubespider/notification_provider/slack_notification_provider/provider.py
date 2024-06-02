import logging

from notification_provider import provider
from utils.config_reader import AbsConfigReader
from utils.helper import get_request_controller


class SlackNotificationProvider(provider.NotificationProvider):
    def __init__(self, name: str, config_reader: AbsConfigReader) -> None:
        super().__init__(name, config_reader)
        self.name = name
        self.enable, self.host, self.channel, self.username, self.title_lan = self._init_conf(
            config_reader)
        self.request_handler = get_request_controller()

    @staticmethod
    def _init_conf(config_reader: AbsConfigReader):
        conf = config_reader.read()
        return conf.get("enable", True), conf.get("host"), conf.get("channel"), conf.get("username"), conf.get("title_lan")

    def get_provider_name(self) -> str:
        return self.name

    def provider_enabled(self) -> bool:
        return self.enable

    def push(self, title, **kwargs) -> bool:
        message = self.format_message(title, **kwargs)
        # Slack APP弹窗通知的标题
        push_title = "Kubespider收到新下载请求."
        # Slack APP里正文的标题
        body_title = "收到下载请求"
        url = self.host
        headers = {
            'Content-Type': 'application/json; charset=utf-8'
        }
        if self.title_lan == "en":
            push_title = "Kubespider has received a new download request."
            body_title = "Received Download request"
        slack_data = {
            "username": self.username,
            "channel": "#" + self.channel,
            "text": push_title,
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": body_title,
                    }
                },
                # 正文内容主体text
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "\n:small_blue_diamond:" + message
                    }
                },
                {
                    "type": "divider"
                }
            ]
        }
        response = self.request_handler.post(
            url, json=slack_data, timeout=5, headers=headers).json()
        if response.status_code != 200:
            logging.error("Slack push failed : %s", response.text)
            return False
        logging.info("Slack push success : %s", response.text)
        return True

    def format_message(self, title, **kwargs) -> str:
        message = []
        for key, value in kwargs.items():
            message.append(f"{key}: {value}")
        return "\n".join(message)
