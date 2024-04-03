# -*- coding: utf-8 -*-

import logging
import _thread

from core import download_manager
from core import period_server
from core import pt_server
from core import config_handler
from core import notification_manager
from core import source_manager
from core import plugin_manager
from core import plugin_binding
from source_provider.provider import SourceProvider
from download_provider.provider import DownloadProvider
from pt_provider.provider import PTProvider
from notification_provider.provider import NotificationProvider


class Kubespider:

    def __init__(self) -> None:
        self.source_providers: list[SourceProvider] = []
        self.pt_providers: list[PTProvider] = []
        self.notifications_providers: list[NotificationProvider] = []
        self.enabled_source_providers: list[SourceProvider] = []
        self.enabled_download_providers: list[DownloadProvider] = []
        self.enabled_pt_providers: list[PTProvider] = []
        self.enabled_notifications_providers: list[NotificationProvider] = []

    def config(self) -> None:
        self.source_providers = config_handler.init_source_config()
        self.pt_providers = config_handler.init_pt_config()

        for provider in self.source_providers:
            provider_name = provider.get_provider_name()
            try:
                if provider.provider_enabled():
                    logging.info('Source Provider:%s enabled...', provider_name)
                    self.enabled_source_providers.append(provider)
            except KeyError:
                logging.warning('Source Provider:%s not exists, treat as disabled', provider_name)

        for provider in self.pt_providers:
            provider_name = provider.get_provider_name()
            try:
                if provider.provider_enabled():
                    logging.info('PT Provider:%s enabled...', provider_name)
                    self.enabled_pt_providers.append(provider)
            except KeyError:
                logging.warning('PT Provider:%s not exists, treat as disabled', provider_name)

        # source provider aggregate
        source_manager.source_provider_manager = source_manager.SourceProviderManager(self.enabled_source_providers)

        period_server.kubespider_period_server = period_server.PeriodServer(self.enabled_source_providers)

        pt_server.kubespider_pt_server = pt_server.PTServer(self.enabled_pt_providers)
        download_manager.kubespider_download_server = download_manager.DownloadManager()
        notification_manager.kubespider_notification_server = notification_manager.NotificationManager()
        # plugin manager
        plugin_manager.kubespider_plugin_manager = plugin_manager.PluginManager()
        # plugin binding
        plugin_binding.kubespider_plugin_binding = plugin_binding.PluginBinding()

    def run_pt_server(self) -> None:
        logging.info('PT Server start running...')
        pt_server.kubespider_pt_server.run()

    def run_period_job_consumer(self) -> None:
        logging.info('Period Server Queue handler start running...')
        period_server.kubespider_period_server.run_consumer()

    def run_period_job_producer(self) -> None:
        logging.info("Period Server producer start running...")
        period_server.kubespider_period_server.run_producer()

    def run_download_trigger_job(self) -> None:
        logging.info('Download trigger job start running...')
        download_manager.kubespider_download_server.period_run()

    def run_notification_consumer(self) -> None:
        logging.info('Notification Server Queue handler start running...')
        notification_manager.kubespider_notification_server.run_consumer()

    def run_plugin_manager(self) -> None:
        logging.info('Plugin Manager start running...')
        plugin_manager.kubespider_plugin_manager.load_local()
        plugin_binding.kubespider_plugin_binding.load_store()

    def run(self) -> None:
        _thread.start_new_thread(self.run_period_job_producer, ())
        _thread.start_new_thread(self.run_period_job_consumer, ())
        _thread.start_new_thread(self.run_download_trigger_job, ())
        _thread.start_new_thread(self.run_pt_server, ())
        _thread.start_new_thread(self.run_notification_consumer, ())
        _thread.start_new_thread(self.run_plugin_manager, ())


kubespider_controller = Kubespider()
