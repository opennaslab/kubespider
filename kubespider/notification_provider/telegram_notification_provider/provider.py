import logging
import time
from urllib.parse import urljoin

from notification_provider import provider
from utils.config_reader import AbsConfigReader
from utils.helper import get_request_controller, retry


class TelegramNotificationProvider(provider.NotificationProvider):
    def __init__(self, name: str, config_reader: AbsConfigReader) -> None:
        self.config_reader = config_reader
        self.name = name
        self.request_handler = get_request_controller()
        self.type, self.enable, self.host, self.token, self.channel_name, self.chat_id = \
            self._init_conf(config_reader)
        if not self.chat_id and self.enable:
            self.chat_id = self.get_channel_chat_id(self.channel_name)
            if self.chat_id:
                self.save_conf(channel_chat_id=self.chat_id)

    @staticmethod
    def _init_conf(config_reader: AbsConfigReader) -> tuple:
        conf = config_reader.read()
        return conf.get("type"), conf.get("enable", False), conf.get("host"), conf.get("bot_token"), conf.get(
            "channel_name"), conf.get("channel_chat_id")

    def get_provider_name(self) -> str:
        return self.name

    def provider_enabled(self) -> bool:
        return self.enable

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
        self.config_reader.parcial_update(lambda notification_conf: notification_conf["telegram"].update(kwargs))
