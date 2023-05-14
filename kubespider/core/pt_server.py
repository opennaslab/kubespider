# -*- coding: utf-8 -*-

import time
import os

import logging

from core import download_trigger
from pt_provider import provider
from utils.config_reader import AbsConfigReader
from utils.config_reader import YamlFileConfigReader
from api.values import Config
from api.values import PT_BOT_PATH


class PTServer:
    def __init__(self, config_reader: AbsConfigReader, pt_providers: list) -> None:
        self.pt_providers = pt_providers

        self.single_file_threshold = config_reader.read().get('pt_single_max_size', 100.0)
        self.sum_file_threshold = config_reader.read().get('pt_sum_max_size', 100.0)
        self.seeding_time = config_reader.read().get('pt_seeding_time') * 3600

        self.state_config = YamlFileConfigReader(Config.STATE.config_path())
        state = self.state_config.read().get('pt_state', {})
        self.time = state.get('last_start_time', 0)
        self.size = state.get('download_sum_size', 0.0)


    def run(self):
        while True:
            logging.info("Downloading size is:%f, threshold:%f", self.size, self.sum_file_threshold)
            current_time = int(time.time())
            if current_time - self.time > self.seeding_time:
                for iter_provider in self.pt_providers:
                    self.trigger_remove_tasks(iter_provider)
                self.size = 0.0
                self.time = current_time

            for iter_provider in self.pt_providers:
                iter_provider.go_attendance()

                links = iter_provider.get_links()
                for link in links:
                    link_size = float(link['size'])
                    if link_size < self.single_file_threshold and \
                        link_size + self.size < self.sum_file_threshold:
                        self.trigger_download_tasks(link['torrent'], iter_provider)
                        self.size += link_size
                        logging.info('Add one task(%fGB), now is %fGB', link_size, self.size)

            self.save_state()
            time.sleep(3600)

    def trigger_download_tasks(self, pt_source: str, pt_provider: provider.PTProvider):
        logging.info("Start downloading: %s", pt_source)
        provider_name = pt_provider.get_download_provider()
        download_provider = download_trigger.kubespider_downloader.filter_downloader_by_name(provider_name)
        if download_provider is None:
            logging.error('Downloader not found: %s', provider_name)
            return

        download_path = os.path.join(PT_BOT_PATH, provider_name)
        err = download_trigger.kubespider_downloader.handle_torrent_download(pt_source, download_path, [download_provider])
        if err is not None:
            logging.error('Download error: %s', err)

    def trigger_remove_tasks(self, pt_provider: provider.PTProvider):
        provider_name = pt_provider.get_download_provider()
        download_provider = download_trigger.kubespider_downloader.filter_downloader_by_name(provider_name)
        if download_provider is None:
            logging.error('Downloader not found: %s', provider_name)
            return

        download_trigger.kubespider_downloader.handle_download_remove([download_provider])

    def save_state(self):
        state = {'pt_state': {
                    'last_start_time': self.time, 
                    'download_sum_size': self.size
                }
        }
        self.state_config.parcial_update(lambda all_state: all_state.update(state))

kubespider_pt_server: PTServer = None
