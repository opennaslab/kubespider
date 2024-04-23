# -*- coding: utf-8 -*-
import queue
import time
import logging
import notification_provider
from models import Notification, session_context


class NotificationManager:
    def __init__(self) -> None:
        self.queue = queue.Queue(maxsize=100)
        self.instances = {}

    @staticmethod
    def get_definitions():
        return [provider.definitions().serializer() for provider in notification_provider.providers]

    @staticmethod
    def get_notification_models(enable=None):
        with session_context() as session:
            if enable is not None:
                return session.query(Notification).filter_by(enable=enable).all()
            return session.query(Notification).all()

    def get_confs(self) -> dict:
        data = {}
        for instance in self.get_notification_models():
            _id = instance.id
            config = instance.config
            name = instance.name
            _type = instance.type
            enable = instance.enable
            is_alive = self.instances[name].is_alive if name in self.instances.keys() else False
            config.update(name=name, type=_type, enable=enable, is_alive=is_alive, id=_id)
            data[name] = config
        return data

    def create_or_update(self, reload=True, **kwargs):
        with session_context() as session:
            _id = kwargs.get("id")
            name = kwargs.get("name")
            config_type = kwargs.pop('type')
            enable = kwargs.pop('enable')
            download_conf = session.query(Notification).filter_by(id=_id).first() or Notification()
            self.validate_config(config_type, **kwargs)
            download_conf.name = name
            download_conf.type = config_type
            download_conf.config = kwargs
            download_conf.enable = enable
            session.add(download_conf)
            session.commit()
            if reload:
                self.reload_instance()

    def remove(self, _id, reload=True):
        with session_context() as session:
            config_model = session.query(Notification).filter_by(id=_id).first()
            if config_model:
                session.delete(config_model)
                session.commit()
                self.reload_instance()
                if reload:
                    self.reload_instance()

    def reload_instance(self):
        for notification_model in self.get_notification_models(enable=True):
            try:
                config = notification_model.config
                cls = self.get_provider_by_type(notification_model.type)
                definitions = cls.definitions()
                params = {}
                for arg_name in definitions.arguments.keys():
                    params[arg_name] = config.get(arg_name)
                if not params.get("name"):
                    params["name"] = notification_model.name
                # pylint: disable=E1102
                instance = cls(**params)
                self.instances[notification_model.name] = instance
                logging.info('[NotificationManager] %s enabled...', notification_model.name)
            except Exception as err:
                logging.warning('[NotificationManager] %s enabled failed, %s', notification_model.name, err)
        logging.info("[NotificationManager] instance reload finish ...")

    def run_consumer(self) -> None:
        logging.info('Notification Server Queue handler start running...')
        while True:
            try:
                title, kwargs = self.queue.get(block=False)
                for instance in self.instances.values():
                    instance.push(title, **kwargs)
            except queue.Empty:
                time.sleep(1)
            except Exception as err:
                logging.error("[NotificationManager] Message queue consume failed: %s", err)

    def send_message(self, title: str, **kwargs) -> None:
        if self.instances:
            self.queue.put((title, kwargs))

    @staticmethod
    def get_provider_by_type(notification_type: str):
        provider_cls = getattr(notification_provider, notification_type, None)
        if not provider_cls:
            raise ValueError("type missing or invalid")
        return provider_cls

    def validate_config(self, _type, **arguments):
        provider = self.get_provider_by_type(_type)
        definition = provider.definitions()
        definition.validate(**arguments)


notification_manager: NotificationManager = NotificationManager()
