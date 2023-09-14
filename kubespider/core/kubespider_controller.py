# -*- coding: utf-8 -*-

import logging
import _thread

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core import download_trigger
from core import period_server
from core import pt_server
from core import config_handler
from core import notification_server
from core import source_manager

from source_provider.provider import SourceProvider
from download_provider.provider import DownloadProvider
from pt_provider.provider import PTProvider
from notification_provider.provider import NotificationProvider


class Kubespider:

    def __init__(self) -> None:
        self.source_providers: list[SourceProvider] = []
        self.download_providers: list[DownloadProvider] = []
        self.pt_providers: list[PTProvider] = []
        self.notifications_providers: list[NotificationProvider] = []
        self.enabled_source_providers: list[SourceProvider] = []
        self.enabled_download_providers: list[DownloadProvider] = []
        self.enabled_pt_providers: list[PTProvider] = []
        self.enabled_notifications_providers: list[NotificationProvider] = []

    def config(self) -> None:
        self.source_providers = config_handler.init_source_config()
        self.download_providers = config_handler.init_download_config()
        self.pt_providers = config_handler.init_pt_config()
        self.notifications_providers = config_handler.init_notification_config()

        for provider in self.source_providers:
            provider_name = provider.get_provider_name()
            try:
                if provider.provider_enabled():
                    logging.info('Source Provider:%s enabled...', provider_name)
                    self.enabled_source_providers.append(provider)
            except KeyError:
                logging.warning('Source Provider:%s not exists, treat as disabled', provider_name)

        for provider in self.download_providers:
            provider_name = provider.get_provider_name()
            try:
                if provider.provider_enabled():
                    logging.info('Download Provider:%s enabled...', provider_name)
                    self.enabled_download_providers.append(provider)
            except KeyError:
                logging.warning('Download Provider:%s not exists, treat as disabled', provider_name)
        self.enabled_download_providers.sort(key=sort_download_provider)

        for provider in self.pt_providers:
            provider_name = provider.get_provider_name()
            try:
                if provider.provider_enabled():
                    logging.info('PT Provider:%s enabled...', provider_name)
                    self.enabled_pt_providers.append(provider)
            except KeyError:
                logging.warning('PT Provider:%s not exists, treat as disabled', provider_name)

        for provider in self.notifications_providers:
            provider_name = provider.get_provider_name()
            try:
                if provider.provider_enabled():
                    logging.info('Notification Provider:%s enabled...', provider_name)
                    self.enabled_notifications_providers.append(provider)
            except KeyError:
                logging.warning('Notification Provider:%s not exists, treat as disabled', provider_name)

        # download provider aggregate
        download_trigger.kubespider_downloader = download_trigger.KubespiderDownloader(self.enabled_download_providers)
        # source provider aggregate
        source_manager.source_provider_manager = source_manager.SourceProviderManager(self.enabled_source_providers)

        period_server.kubespider_period_server = period_server.PeriodServer(self.enabled_source_providers)

        pt_server.kubespider_pt_server = pt_server.PTServer(self.enabled_pt_providers)

        notification_server.kubespider_notification_server = notification_server.NotificationServer(
            self.enabled_notifications_providers
        )

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
        download_trigger.kubespider_downloader.period_run()

    def run_notification_consumer(self) -> None:
        logging.info('Notification Server Queue handler start running...')
        notification_server.kubespider_notification_server.run_consumer()

    def run(self) -> None:
        _thread.start_new_thread(self.run_period_job_producer, ())
        _thread.start_new_thread(self.run_period_job_consumer, ())
        _thread.start_new_thread(self.run_download_trigger_job, ())
        _thread.start_new_thread(self.run_pt_server, ())
        _thread.start_new_thread(self.run_notification_consumer, ())


kubespider_controller = Kubespider()


def sort_download_provider(provider: DownloadProvider):
    return provider.provide_priority()
