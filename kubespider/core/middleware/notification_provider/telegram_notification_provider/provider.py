import logging
import time
from urllib.parse import urljoin

from flask import current_app

from core.middleware.notification_provider.provider import NotificationProvider
from utils.helper import get_request_controller, retry


class TelegramNotificationProvider(NotificationProvider):
    """Telegram channel notification tool"""

    def __init__(self, name: str, channel_name, bot_token: str, channel_chat_id: str = None) -> None:
        """
        :param name: provider instance name
        :param channel_name: channel name
        :param bot_token: bot token
        :param channel_chat_id: channel id
        """
        self.name = name
        self.request_handler = get_request_controller()
        self.host = "https://api.telegram.org"
        self.token = bot_token
        self.channel_name = channel_name
        self.channel_chat_id = channel_chat_id

    @property
    def chat_id(self):
        if not self.channel_chat_id:
            self.channel_chat_id = self.get_channel_chat_id(self.channel_name)
            if self.chat_id:
                self.update_instance_conf(channel_chat_id=self.chat_id)
        return self.channel_chat_id

    def get_channel_chat_id(self, channel_name) -> str:
        url = urljoin(self.host, f"/bot{self.token}/getUpdates")
        resp = self.request_handler.get(url, timeout=5).json()
        for res in resp.get("result", [])[::-1]:
            for value in res.values():
                if isinstance(value, dict):
                    chat = value.get("chat", {})
                    if chat.get("type") == "channel" and chat.get("title") == channel_name:
                        return chat.get("id")
        logging.error("[Telegram] chat_id not found, response: %s", resp)
        return ""

    @retry()
    def push(self, title, **kwargs) -> bool:
        url = urljoin(self.host, f"/bot{self.token}/sendMessage")
        text = self.format_message(title, **kwargs)
        data = {
            'chat_id': self.chat_id,
            'text': text,
            'parse_mode': 'Markdown'}
        resp = self.request_handler.post(url, data=data, timeout=5).json()
        if resp.get("ok"):
            return True
        if resp.get("error_code") == 400:
            logging.error(
                "[Telegram] push failed, exc:%s, text:%s", resp.get("description"), text
            )
        if resp.get("error_code") == 429:
            retry_after = resp.get("parameters", {}).get("retry_after", 5)
            time.sleep(retry_after)
            raise Exception("time sleep require")
        return False

    def format_message(self, title, **kwargs) -> str:
        message = [f"*{title}*"] if title else []
        for key, value in kwargs.items():
            message.append(f"`{key}`: {value}")
        return "\n".join(message)

    def update_instance_conf(self, **kwargs) -> None:
        manager = current_app.extensions['notification_manager']
        manager.partial_update_conf(self.name, **kwargs)
