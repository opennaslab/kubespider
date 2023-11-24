# -*- coding: utf-8 -*-
import _thread
import queue
import time
import logging
from flask import Flask

from core.middleware.manager import AbsManager
from core.middleware.notification_provider import providers
from utils.types import ProviderType


class NotificationManager(AbsManager):
    def __init__(self, app=None) -> None:
        self.provider_type = ProviderType.notification_provider
        self.queue = queue.Queue(maxsize=100)
        self.instance = {}
        if app:
            self.init_app(app)

    def init_app(self, app: Flask):
        if "notification_manager" in app.extensions:
            raise RuntimeError(
                "A 'Notification' instance has already been registered on this Flask app."
                " Import and use that instance instead."
            )
        with app.app_context():
            app.extensions["notification_manager"] = self
            self.reload_instance()
            _thread.start_new_thread(self._run_consumer, (app,))

    @staticmethod
    def get_specs():
        return [np.spec() for np in providers]

    def reload_instance(self):
        instance = {}
        providers_map = {nd.__name__: nd for nd in providers}
        for ins_conf in self.get_instance_confs():
            if ins_conf.get("enable"):
                conf = ins_conf["conf"]
                provider_cls = providers_map.get(conf["provider_name"])
                init_params = {item.get("name"): item.get("value") for item in conf.get("instance_params")}
                instance[ins_conf["id"]] = provider_cls(**init_params)
                logging.info(f"[NotificationManager] {ins_conf.get('instance_name')} enabled ...")
        self.instance = instance
        logging.info("[NotificationManager] instance reload success ...")

    def _run_consumer(self, app: Flask) -> None:
        with app.app_context():
            while True:
                try:
                    title, kwargs = self.queue.get(block=False)
                    for instance_id, instance in self.instance.items():
                        instance.push(title, **kwargs)
                except queue.Empty:
                    time.sleep(1)
                except Exception as err:
                    logging.error("Message queue consume failed: %s", err)

    def send_message(self, title: str, **kwargs) -> None:
        if self.instance:
            self.queue.put((title, kwargs))
