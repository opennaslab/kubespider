import json
import logging
from urllib.parse import urljoin

from core.middleware.notification_provider.provider import NotificationProvider
from utils.helper import get_request_controller


class PushDeerNotificationProvider(NotificationProvider):
    """An open-source notification tool pushDeer"""

    def __init__(self, name: str, host: str, push_keys: list[str]) -> None:
        """
        :param name: provider instance name
        :param host: pushdeer`s host
        :param push_keys: pushdeer`s push key
        """
        self.name = name
        self.host = host
        self.push_keys = push_keys
        self.request_handler = get_request_controller()

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
