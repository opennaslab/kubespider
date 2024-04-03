import json
import os
from urllib.parse import urljoin
import logging

from notification_provider import provider
from utils.helper import get_request_controller


class SynologyNotificationProvider(provider.NotificationProvider):
    """Synology Chat"""
    LOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")

    def __init__(self, name: str, host: str, token: str) -> None:
        """
        :param name: unique instance name
        :param host: SynologyChat`s host
        :param token: bot`s token
        """
        super().__init__(name=name)
        self.host = host
        self.token = token
        self.request_handler = get_request_controller()

    def get_user_list(self):
        url = urljoin(self.host,
                      f"/webapi/entry.cgi?api=SYNO.Chat.External&method=user_list&version=2&token={self.token}")
        resp = self.request_handler.get(url)
        if resp.status_code == 200:
            users = resp.json().get("data", {}).get("users", []) or []
            return [user.get("user_id") for user in users]
        return []

    def push(self, title: str, **kwargs) -> bool:
        # such as
        # 'attachments': [
        #     {
        #         "callback_id": "abc",
        #         "text": "下载",
        #         "actions":
        #             [
        #                 {"type": "button",
        #                  "name": "resp",
        #                  "value": "ok",
        #                  "text": "是",
        #                  "style": "red"}
        #             ]
        #     }
        # ]
        attachments = kwargs.pop("attachments", [])
        # file_url: 'http://xxx.xxx.xxx:888/static/img/logo/logo.png'
        file_url = kwargs.pop("file_url", "")
        message = self.format_message(title, **kwargs)
        data = {
            'text': message,
            'user_ids': self.get_user_list(),
            'file_url': file_url,
            'attachments': attachments
        }
        url = urljoin(self.host,
                      f"/webapi/entry.cgi?api=SYNO.Chat.External&method=chatbot&version=2&token={self.token}")
        data = f"payload={json.dumps(data)}"
        resp = self.request_handler.post(url, data=data, timeout=30).json()
        if resp.get("success"):
            return True
        logging.error("[SynologyChat] push failed: %s", resp)
        return False

    def format_message(self, title, **kwargs) -> str:
        message = [f"*{title}*"]
        for key, value in kwargs.items():
            message.append(f"{key}: {value}")
        return "\n".join(message)
