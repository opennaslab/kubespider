import time
import hmac
import hashlib
import base64
import urllib.parse
import logging

from notification_provider import provider
from utils.config_reader import AbsConfigReader
from utils.helper import get_request_controller


class DingtalkNotificationProvider(provider.NotificationProvider):
    def __init__(self, name: str, config_reader: AbsConfigReader) -> None:
        super().__init__(name, config_reader)
        self.name = name
        self.magnet_name = ""
        self.webhook_url = "https://oapi.dingtalk.com/robot/send?access_token="
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
        # 如果存在secret，则使用加密方式发送
        if self.secret != "none":
            timestamp, sign = self.build_sign(self.secret)
            webhook_url = self.webhook_url + self.token + "&timestamp=" + timestamp + "&sign=" + sign
        else:
            webhook_url = self.webhook_url + self.token

        headers = {
            'Content-Type': 'application/json; charset=utf-8'
        }
        post_data = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": "#### **" + title + "**" + " \n \n" + "**" + self.magnet_name + "**" + " \n \n" + message
            }
        }
        response = self.request_handler.post(
            webhook_url, json=post_data, timeout=5, headers=headers).json()
        if response['errcode'] != 0:
            logging.error("Dingtalk push failed : %s", response['errmsg'])
            return False
        logging.info("Dingtalk push success : %s", response['errmsg'])
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
        timestamp = str(round(time.time() * 1000))
        secret_enc = secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return timestamp, sign

