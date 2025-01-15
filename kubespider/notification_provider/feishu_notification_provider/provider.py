import time
import hashlib
import base64
import hmac
import logging

from notification_provider import provider
from utils.config_reader import AbsConfigReader
from utils.helper import get_request_controller


class FeishuNotificationProvider(provider.NotificationProvider):
    def __init__(self, name: str, config_reader: AbsConfigReader) -> None:
        super().__init__(name, config_reader)
        self.name = name
        self.magnet_name = ""
        self.webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/"
        self.enable, self.token, self.secret = self._init_conf(config_reader)
        self.request_handler = get_request_controller()

    @staticmethod
    def _init_conf(config_reader: AbsConfigReader):
        conf = config_reader.read()
        return conf.get("enable", True), conf.get("token"), conf.get("secret")

    def get_provider_name(self) -> str:
        return self.name

    def provider_enabled(self) -> bool:
        return self.enable

    def push(self, title, **kwargs) -> bool:
        message = self.format_message(title, **kwargs)
        webhook_url = self.webhook_url + self.token
        post_data = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": title,
                        "content": [
                            [
                                {
                                    "tag": "text",
                                    "text": self.magnet_name
                                }
                            ],
                            [
                                {
                                    "tag": "text",
                                    "text": message
                                }
                            ]
                        ]
                    }
                }
            }
        }
        if self.secret != "none":
            timestamp, sign = self.build_sign(self.secret)
            sgin_data = {"timestamp": timestamp, "sign": sign}
            post_data = {**sgin_data, **post_data}

        headers = {
            'Content-Type': 'application/json; charset=utf-8'
        }
        response = self.request_handler.post(
            webhook_url, json=post_data, timeout=5, headers=headers).json()
        if response.status_code != 200:
            logging.error("Slack push failed : %s", response.text)
            return False
        logging.info("Slack push success : %s", response.text)
        return True

    def format_message(self, title, **kwargs) -> str:
        message = []
        for key, value in kwargs.items():
            if key == "name":
                self.magnet_name = "name: " + value
                continue
            message.append(f"{key}: {value}")
        return "\n".join(message)

    def build_sign(self, secret: str):
        # 计算加签后的密钥
        timestamp = str(round(time.time()))
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code).decode('utf-8')
        return timestamp, sign
