# -*- coding: utf-8 -*-
import queue
import time
import logging

from flask import Flask

import notification_provider
from utils.config_reader import YamlFileConfigReader
from utils.values import Config, Extra


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
        return [provider.definitions().serializer() for provider in notification_provider.providers]

    def get_confs(self) -> dict:
        notification_config = self.notification_config.read()
        return dict(notification_config.items())

    def create_or_update(self, reload=True, **kwargs):
        name = kwargs.get("name")
        config = self.notification_config.read()
        exists = config.get(name)
        extra_params = {}
        if exists:
            extra_params.update(exists)
        extra_params.update(kwargs)
        config_type = extra_params.pop('type')
        enable = extra_params.pop('enable')
        notification_config = NotificationConfig(config_type, enable, **extra_params)
        notification_config.validate()

        config[name] = notification_config.to_dict()
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
                    cls = NotificationConfig.get_provider_by_type(conf.get("type"))
                    definitions = cls.definitions()
                    params = {}
                    for arg_name in definitions.arguments.keys():
                        params[arg_name] = conf.get(arg_name)
                    if not params.get("name"):
                        params["name"] = name
                    # pylint: disable=E1102
                    instance = cls(**params)
                    self.instance[name] = instance
                    logging.info('[NotificationManager] %s enabled...', name)
            except Exception as err:
                logging.warning('[NotificationManager] %s enabled failed, %s', name, err)
        logging.info("[NotificationManager] instance reload success ...")

    def run_consumer(self) -> None:
        while True:
            try:
                title, kwargs = self.queue.get(block=False)
                for instance in self.instance.values():
                    instance.push(title, **kwargs)
            except queue.Empty:
                time.sleep(1)
            except Exception as err:
                logging.error("[NotificationManager] Message queue consume failed: %s", err)

    def send_message(self, title: str, **kwargs) -> None:
        if self.instance:
            self.queue.put((title, kwargs))


class NotificationConfig(Extra):
    def __init__(self, config_type: str, enable: bool, **kwargs) -> None:
        super().__init__(**kwargs)
        self.name = kwargs.get("name")
        self.type = config_type
        self.enable = enable

    @classmethod
    def get_provider_by_type(cls, _type: str):
        _type: str = cls.translate_type(_type)
        provider_cls = getattr(notification_provider, _type, None)
        if not provider_cls:
            raise ValueError("type missing or invalid")
        return provider_cls

    def validate(self):
        provider = self.get_provider_by_type(self.type)
        definition = provider.definitions()
        definition.validate(**self.extra_params())

    @staticmethod
    def translate_type(_type: str) -> str:
        type_split = _type.split("_")
        if len(type_split) > 1:
            return "".join([i.capitalize() for i in type_split])
        return _type

    def to_dict(self) -> dict:
        provider = self.get_provider_by_type(self.type)
        return {
            "type": provider.__name__,
            "enable": bool(self.enable),
            **self.extra_params()
        }


kubespider_notification_server: NotificationManager = None
