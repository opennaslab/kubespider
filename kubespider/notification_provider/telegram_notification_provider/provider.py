import logging
import os
import time
from urllib.parse import urljoin

from notification_provider import provider
from utils.config_reader import YamlFileConfigReader
from utils.helper import get_request_controller, retry
from utils.values import Config


class TelegramNotificationProvider(provider.NotificationProvider):
    """Telegram channel notification tool"""
    LOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")

    def __init__(self, name: str, channel_name: str, bot_token: str, channel_chat_id: str = None) -> None:
        """
        :param name: unique instance name
        :param channel_name: channel name
        :param bot_token: bot token
        :param channel_chat_id: channel id
        """
        super().__init__(name=name)
        self.request_handler = get_request_controller()
        self.host = "https://api.telegram.org"
        self.token = bot_token
        self.channel_name = channel_name
        self.channel_chat_id = channel_chat_id

    @property
    def chat_id(self):
        if self.channel_chat_id:
            return self.channel_chat_id
        return self.get_channel_chat_id(self.channel_name)

    def get_channel_chat_id(self, channel_name) -> str:
        channel_chat_id = ""
        url = urljoin(self.host, f"/bot{self.token}/getUpdates")
        resp = self.request_handler.get(url, timeout=5).json()
        for res in resp.get("result", [])[::-1]:
            for value in res.values():
                if isinstance(value, dict):
                    chat = value.get("chat", {})
                    if chat.get("type") == "channel" and chat.get("title") == channel_name:
                        channel_chat_id = chat.get("id")
        logging.error("[Telegram] chat_id not found, response: %s", resp)
        if channel_chat_id:
            self.save_conf(channel_chat_id=channel_chat_id)
        return channel_chat_id

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
            # 格式化之后的 markdown 文本格式识别出错,记录下来用于分析
            logging.error(
                "[Telegram] push failed, exc:%s, text:%s", resp.get("description"), text
            )
        if resp.get("error_code") == 429:
            # 请求过于频繁,等待提示时间
            retry_after = resp.get("parameters", {}).get("retry_after", 5)
            time.sleep(retry_after)
            raise Exception("time sleep require")
        return False

    def format_message(self, title, **kwargs) -> str:
        message = [f"*{title}*"] if title else []
        for key, value in kwargs.items():
            message.append(f"`{key}`: {value}")
        return "\n".join(message)

    def save_conf(self, **kwargs) -> None:
        logging.info("[Telegram] update telegram conf: %s", kwargs)
        config_reader = YamlFileConfigReader(Config.NOTIFICATION_PROVIDER.config_path())
        config_reader.parcial_update(lambda notification_conf: notification_conf[self.name].update(kwargs))
