import json
from urllib.parse import urljoin
import logging

from notification_provider import provider
from utils.config_reader import AbsConfigReader
from utils.helper import get_request_controller


class MessagePusherNotificationProvider(provider.NotificationProvider):

    def __init__(self, name: str, config_reader: AbsConfigReader) -> None:
        self.name = name
        self.enable, self.host, self.push_keys, self.type = \
            self._init_conf(config_reader)
        self.request_handler = get_request_controller()

    @staticmethod
    def _init_conf(config_reader):
        conf = config_reader.read()
        return conf.get("enable", True), conf.get("host"), conf.get("token", []), conf.get("type", [])

    def get_provider_name(self) -> str:
        return self.name

    def provider_enabled(self) -> bool:
        return self.enable

    def push(self, title, **kwargs) -> bool:
        try:
            # POST 方式
            message = self.format_message(title, **kwargs)
            res = self.request_handler.post(urljoin(self.host, f"/push/{USERNAME}"), json={
                "title": title,
                "description": description,
                "content": content,
                "token": TOKEN
            })
            res = res.json()
            if res["success"]:
                return None
            else:
                return res["message"]

            return any(push_result)
        except Exception as err:
            logging.error("[Pushdeer] push failed : %s", err)
            return False

    def format_message(self, title, **kwargs) -> str:
        message = [f"### {title}"] if title else []
        for key, value in kwargs.items():
            message.append(f"* `{key}`: {value}")
        return "\n".join(message)
