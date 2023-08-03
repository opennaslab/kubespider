import json
from urllib.parse import urljoin
import logging

from notification_provider import provider
from utils.config_reader import AbsConfigReader
from utils.helper import get_request_controller


class PushDeerNotificationProvider(provider.NotificationProvider):

    def __init__(self, name: str, config_reader: AbsConfigReader) -> None:
        self.name = name
        self.enable, self.host, self.push_keys, self.type = \
            self._init_conf(config_reader)
        self.request_handler = get_request_controller()

    @staticmethod
    def _init_conf(config_reader):
        conf = config_reader.read()
        return conf.get("enable", True), conf.get("host"), conf.get("push_keys", []), conf.get("type", [])

    def get_provider_name(self) -> str:
        return self.name

    def provider_enabled(self) -> bool:
        return self.enable

    def push(self, title, **kwargs) -> bool:
        try:
            push_result = self.circularly_push(self.format_message(title, **kwargs))
            return any(push_result)
        except Exception as err:
            logging.error("[Pushdeer] push failed : %s", err)
            return False

    def _push(self, key: str, message: str) -> bool:
        data = {
            "pushkey": key,
            "text": message,
            "type": "markdown",
            "desp": "",
        }
        url = urljoin(self.host, "message/push")
        resp = self.request_handler.post(url, data=data, timeout=5).json()
        if resp.get('code') != 0:
            resp['key'] = key
            logging.error("[Pushdeer] push failed : %s", json.dumps(resp, ensure_ascii=False))
            return False
        return True

    def circularly_push(self, message: str) -> list:
        push_result = []
        if isinstance(self.push_keys, str):
            res = self._push(self.push_keys, message)
            push_result.append(res)
        else:
            for key in self.push_keys:
                res = self._push(key, message)
                push_result.append(res)
        return push_result

    def format_message(self, title, **kwargs) -> str:
        message = [f"### {title}"] if title else []
        for key, value in kwargs.items():
            message.append(f"* `{key}`: {value}")
        return "\n".join(message)
