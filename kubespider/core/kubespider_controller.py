# -*- coding: utf-8 -*-

import logging
import _thread
from core import notification_manager, download_manager
from core.plugin import manager


class Kubespider:

    @staticmethod
    def run_notification_consumer() -> None:
        logging.info('Notification Server Queue handler start running...')
        notification_manager.notification_manager.reload_instance()
        notification_manager.notification_manager.run_consumer()

    @staticmethod
    def run_download_trigger_job() -> None:
        logging.info('Download trigger job start running...')
        download_manager.download_manager.reload_instance()
        download_manager.download_manager.period_run()

    @staticmethod
    def run_plugin_manager():
        logging.info('Plugin Manager start running...')
        manager.plugin_manager.load_local()

    def run(self) -> None:
        _thread.start_new_thread(self.run_notification_consumer, ())
        _thread.start_new_thread(self.run_download_trigger_job, ())
        _thread.start_new_thread(self.run_plugin_manager, ())


kubespider_controller = Kubespider()
