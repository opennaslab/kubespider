import logging
from urllib.parse import urljoin
from requests import Response

from utils.config_reader import AbsConfigReader
from utils.helper import get_request_controller
from notification_provider import provider

class QQNotificationProvider(provider.NotificationProvider):

    def __init__(self, name: str, config_reader: AbsConfigReader) -> None:
        super().__init__(name, config_reader)
        self.name = name
        self.enable, self.host, self.access_token, self.target_qq = self._init_conf(config_reader)
        self.request_handler = get_request_controller()

    @staticmethod
    def _init_conf(config_reader: AbsConfigReader):
        conf = config_reader.read()
        enable, host, access_token, target_qq = conf.get("enable", False), conf.get("host"), conf.get("accessToken"), conf.get("target_qq")
        target_qq = int(target_qq)
        return enable, host, access_token, target_qq

    def get_provider_name(self) -> str:
        return self.name

    def provider_enabled(self) -> bool:
        return self.enable

    def push(self, title: str, **kwargs) -> bool:
        message = self.format_message(title, **kwargs)
        data = {
            'user_id': self.target_qq,
            'message': message
        }
        url = urljoin(self.host, "send_msg")
        headers = {
            'Content-Type': 'application/json'
        }
        if self.access_token != "":
            headers['Authorization'] = f'Bearer {self.access_token}'
        resp = self.request_handler.post(url, json=data, timeout=5, headers=headers)
        if resp.status_code != 0:
            self.handle_status_code(resp)
            return False
        data = resp.json()
        status = data['status']
        msg = data['msg']
        if status == 'failed':
            logging.error("[QQ] push failed: %s", msg)
            return False
        return True

    def format_message(self, title, **kwargs) -> str:
        message = [f"[CQ:face,id=204]{title}"]
        for key, value in kwargs.items():
            message.append(f"{key}: {value}")
        return "\n".join(message)

    def handle_status_code(self, resp: Response):
        status = resp.status_code
        if status == 401:
            logging.error("[QQ] accessToken not found")
        elif status == 403:
            logging.error("[QQ] accessToken error")
