import json
from typing import Optional
from urllib.parse import urljoin
import logging
import requests

from notification_provider import provider
from utils.config_reader import AbsConfigReader


class PushDeerProvider(provider.NotificationProvider):

    def __init__(self, name: str, config_reader: AbsConfigReader) -> None:
        self.name = name
        self.enable, self.host, self.push_keys, self.type = \
            self._init_conf(config_reader)

    @staticmethod
    def _init_conf(config_reader):
        conf = config_reader.read()
        return conf.get("enable", True), conf.get("host"), conf.get("push_keys", []), conf.get("type", [])

    def get_provider_name(self) -> str:
        return self.name

    def provider_enabled(self) -> bool:
        return self.enable

    def push(self, *args, **kwargs) -> bool:
        try:
            push_result = self.circularly_push(*args, **kwargs)
            return any(push_result)
        except Exception as err:
            logging.error("[Pushdeer] push failed : %s", err)
            return False

    def _push(self, key: str, text: str, description: str = "", push_type: str = "text") -> bool:
        data = {
            "pushkey": key,
            "text": text,
            "type": push_type,
            "desp": description,
        }
        url = urljoin(self.host, "message/push")
        resp = requests.post(url, data=data, timeout=5).json()
        if resp.get('code') != 0:
            resp['key'] = key
            logging.error("[Pushdeer] push failed : %s", json.dumps(resp, ensure_ascii=False))
            return False
        return True

    def circularly_push(self, *args, **kwargs) -> list:
        push_result = []
        if isinstance(self.push_keys, str):
            res = self._push(self.push_keys, *args, **kwargs)
            push_result.append(res)
        else:
            for key in self.push_keys:
                res = self._push(key, *args, **kwargs)
                push_result.append(res)
        return push_result

    def push_text(self, text: str, description: Optional[str] = None, **kwargs) -> bool:
        return self.push(text, description, 'text', **kwargs)

    def push_markdown(self, text: str, description: Optional[str] = None, **kwargs) -> bool:
        return self.push(text, description, 'markdown', **kwargs)

    def push_image(self, image_src: str, description: Optional[str] = None, **kwargs) -> bool:
        return self.push(image_src, description, 'image', **kwargs)
