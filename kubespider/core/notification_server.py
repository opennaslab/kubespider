# -*- coding: utf-8 -*-
import queue
import time
import logging

from notification_provider import provider
from utils.config_reader import YamlFileConfigReader
from utils.values import Config


class NotificationServer:
    def __init__(self, notification_providers: list) -> None:
        self.notification_providers = notification_providers
        self.notification_config = YamlFileConfigReader(Config.NOTIFICATION_PROVIDER.config_path())
        self.queue = queue.Queue()

    def run_consumer(self) -> None:
        while True:
            try:
                title, kwargs = self.queue.get(block=False)
                for provider_instance in self.notification_providers:
                    self.run_single_provider(provider_instance, title, **kwargs)
            except queue.Empty:
                time.sleep(1)
            except Exception as err:
                logging.error("Message queue consume failed: %s", err)

    def send_message(self, title: str, **kwargs) -> None:
        if self.notification_providers:
            self.queue.put((title, kwargs))

    @staticmethod
    def run_single_provider(provider_instance: provider.NotificationProvider, title: str, **kwargs) -> None:
        if provider_instance.provider_enabled():
            provider_instance.push(title, **kwargs)


kubespider_notification_server = NotificationServer(None)
