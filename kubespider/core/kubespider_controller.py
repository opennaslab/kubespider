# -*- coding: utf-8 -*-

import logging
import _thread
import time

from core import download_trigger
from core import period_server
from core import pt_server
from core import config_handler
import download_provider.provider as dp
from utils import global_config


class Kubespider:

    def __init__(self) -> None:
        self.source_providers = []
        self.download_providers = []
        self.pt_providers = []
        self.enabled_source_providers = []
        self.enabled_download_providers = []
        self.enabled_pt_providers = []

    def config(self) -> None:
        self.source_providers = config_handler.init_source_config()
        self.download_providers = config_handler.init_download_config()
        self.pt_providers = config_handler.init_pt_config()

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

        download_trigger.kubespider_downloader = \
        download_trigger.KubespiderDownloader(self.enabled_download_providers)
        period_server.kubespider_period_server = \
            period_server.PeriodServer(self.enabled_source_providers, self.enabled_download_providers)
        pt_server.kubespider_pt_server = \
            pt_server.PTServer(global_config.get_global_config(), self.enabled_pt_providers)

    def run_pt_server(self) -> None:
        logging.info('PT Server start running...')
        pt_server.kubespider_pt_server.run()

    def run_period_job_consumer(self) -> None:
        logging.info('Period Server Quene handler start running...')
        period_server.kubespider_period_server.run_consumer()

    def run_period_job_producer(self) -> None:
        logging.info("Period Server producer start running...")
        period_server.kubespider_period_server.run_producer()

    def run_download_trigger_job(self) -> None:
        logging.info('Download trigger job start running...')
        download_trigger.kubespider_downloader.period_run()

    def run(self) -> None:
        _thread.start_new_thread(self.run_period_job_producer, ())
        _thread.start_new_thread(self.run_period_job_consumer, ())
        _thread.start_new_thread(self.run_download_trigger_job, ())
        _thread.start_new_thread(self.run_pt_server, ())

        while True:
            time.sleep(30)

kubespider_controller = Kubespider()

def sort_download_provider(provider: dp.DownloadProvider):
    return provider.provide_priority()
