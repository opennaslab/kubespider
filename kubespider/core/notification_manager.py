# -*- coding: utf-8 -*-
import queue
import time
import logging
from flask import Flask

import notification_provider
from utils.config_reader import YamlFileConfigReader
from utils.types import ParamsType
from utils.values import Config


class NotificationManager:
    def __init__(self, app=None) -> None:
        self.notification_config = YamlFileConfigReader(Config.NOTIFICATION_PROVIDER.config_path())
        self.queue = queue.Queue(maxsize=100)
        self.instance = {}
        if app:
            self.init_app(app)
        self.reload_instance()

    def init_app(self, app: Flask):
        if "notification_manager" in app.extensions:
            raise RuntimeError(
                "A 'Notification' instance has already been registered on this Flask app."
                " Import and use that instance instead."
            )
        app.extensions["notification_manager"] = self

    @staticmethod
    def get_definitions():
        return [provider.definitions() for provider in notification_provider.providers]

    def get_confs(self) -> dict:
        notification_config = self.notification_config.read()
        return dict(notification_config.items())

    def create_or_update(self, name, reload=True, **kwargs):
        config = self.notification_config.read()
        config[name] = kwargs
        self.notification_config.save(config)
        if reload:
            self.reload_instance()

    def remove(self, name, reload=True):
        config = self.notification_config.read()
        config.pop(name, None)
        self.notification_config.save(config)
        if reload:
            self.reload_instance()

    def reload_instance(self):
        for name, conf in self.get_confs().items():
            try:
                if conf.get("enable"):
                    cls = NotificationConfigValidation.get_provider_by_type(conf.get("type"))
                    definitions = cls.definitions()
                    params = {}
                    for item in definitions.get("arguments", []):
                        param_name = item.get("name")
                        params[param_name] = conf.get(item.get("name"))
                    instance = cls(**params)
                    instance.NAME = name
                    self.instance[name] = instance
                    logging.info('[NotificationManager] %s enabled...', name)
            except Exception as err:
                logging.warning('[NotificationManager] %s enabled failed', name, err)
        logging.info("[NotificationManager] instance reload success ...")

    def run_consumer(self) -> None:
        while True:
            try:
                title, kwargs = self.queue.get(block=False)
                for instance_id, instance in self.instance.items():
                    instance.push(title, **kwargs)
            except queue.Empty:
                time.sleep(1)
            except Exception as err:
                logging.error("[NotificationManager] Message queue consume failed: %s", err)

    def send_message(self, title: str, **kwargs) -> None:
        if self.instance:
            self.queue.put((title, kwargs))


class NotificationConfigValidation:

    def __init__(self, **kwargs):
        self.arguments = kwargs
        self._validated_data = None

    @classmethod
    def get_provider_by_type(cls, _type: str) -> notification_provider.NotificationProvider:
        _type: str = cls.translate_type(_type)
        provider_cls: notification_provider.NotificationProvider = getattr(notification_provider, _type, None)
        if not provider_cls:
            raise ValueError("type missing or invalid")
        return provider_cls

    def validate(self) -> bool:
        validated_data = {}
        provider = self.get_provider_by_type(self.arguments.get("type", ""))
        validated_data['type'] = provider.__name__
        validated_data["enable"] = True if self.arguments.get("enable") else False
        for arg_item in provider.definitions().get("arguments", []):
            name = arg_item.get("name")
            required = arg_item.get("required", False)
            if required:
                if name not in self.arguments.keys():
                    raise ValueError(f"Argument {name} missing")
                else:
                    field_type = arg_item.get("type")
                    if not isinstance(self.arguments.get(name), ParamsType.sting_to_type(field_type)):
                        raise ValueError(f"Argument {name} filed_type error, accept {field_type}")
            validated_data[name] = self.arguments.get(name, "")
        self._validated_data = validated_data
        return True

    @staticmethod
    def translate_type(_type: str) -> str:
        type_split = _type.split("_")
        if len(type_split) > 1:
            return "".join([i.capitalize() for i in type_split])
        return _type

    @property
    def data(self):
        if self._validated_data is not None:
            return self._validated_data
        raise ValueError("NotificationConfig not yet verified")


kubespider_notification_server: NotificationManager = None
