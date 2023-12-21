import logging
from urllib.parse import urljoin
from requests import Response

from core.middleware.notification_provider.provider import NotificationProvider
from utils.helper import get_request_controller


class QQNotificationProvider(NotificationProvider):

    def __init__(self, name: str, host: str, access_token: str, target_qq: str) -> None:
        self.name = name
        self.host = host
        self.access_token = access_token
        self.target_qq = target_qq
        self.request_handler = get_request_controller()

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
