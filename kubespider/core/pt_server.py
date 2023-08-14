# -*- coding: utf-8 -*-

import time
import os

import logging

from core import download_trigger
from pt_provider import provider
from utils.config_reader import YamlFileConfigReader
from api.values import Config, FILE_TYPE_TO_PATH
from api.types import FILE_TYPE_PT, LINK_TYPE_TORRENT
from api.values import Resource, Downloader


class PTServer:
    def __init__(self, pt_providers: list) -> None:
        self.pt_providers: list[provider.PTProvider] = pt_providers
        self.state_config = YamlFileConfigReader(Config.STATE.config_path())

    def run(self):
        while True:
            for iter_provider in self.pt_providers:
                provider_name = iter_provider.get_provider_name()
                provider_state = self.load_state(provider_name)
                keeping_time = iter_provider.get_keeping_time()
                cost_sum_size = iter_provider.get_cost_sum_size()
                max_sum_size = iter_provider.get_max_sum_size()

                logging.info("PT provider(%s) downloading size is:%f/%s, cost downloading size:%f/%f",
                             provider_name, provider_state['download_sum_size'],
                             max_sum_size, provider_state['costs_sum_size'], cost_sum_size)

                current_time = int(time.time())
                if current_time - provider_state['last_start_time'] > keeping_time:
                    self.trigger_remove_tasks(iter_provider)
                    provider_state['last_start_time'] = current_time
                    provider_state['download_sum_size'] = 0.0
                    provider_state['costs_sum_size'] = 0.0
                    iter_provider.go_attendance()

                links = iter_provider.get_links()
                for link in links:
                    link_size = float(link['size'])
                    if link['torrent'] in provider_state['torrent_list']:
                        logging.info("PT provider(%s) already download torrent:%s, skip it", provider_name,
                                     link['torrent'])
                        continue

                    if link['free']:
                        if link_size + provider_state['download_sum_size'] < max_sum_size:
                            self.trigger_download_tasks(link['torrent'], iter_provider)
                            provider_state['download_sum_size'] += link_size
                            provider_state['torrent_list'].append(link['torrent'])
                            logging.info('Add one task(%fGB), now is %fGB', link_size,
                                         provider_state['download_sum_size'])
                    else:
                        if provider_state['costs_sum_size'] <= 0.0:
                            continue

                        # In order to meet the download requirements, we need to make the threshold higher
                        if link_size + provider_state['costs_sum_size'] < cost_sum_size + 5.0:
                            self.trigger_download_tasks(link['torrent'], iter_provider)
                            provider_state['costs_sum_size'] += link_size
                            provider_state['torrent_list'].append(link['torrent'])
                            logging.info('Add one task(%fGB), now is %fGB', link_size, provider_state['costs_sum_size'])

                self.save_state(provider_name, provider_state)

            time.sleep(3600)

    @staticmethod
    def trigger_download_tasks(pt_source: str, pt_provider: provider.PTProvider):
        logging.info("Start downloading: %s", pt_source)
        download_provider_name = pt_provider.get_download_provider()
        download_path = os.path.join(FILE_TYPE_TO_PATH[FILE_TYPE_PT], download_provider_name)
        err = download_trigger.kubespider_downloader.download_file(Resource(
            url=pt_source,
            path=download_path,
            link_type=LINK_TYPE_TORRENT,
            file_type=FILE_TYPE_PT
        ), Downloader(
            download_provider_names=[download_provider_name]
        ))
        if err is not None:
            logging.error('Download error: %s', err)

    @staticmethod
    def trigger_remove_tasks(pt_provider: provider.PTProvider):
        download_provider_name = pt_provider.get_download_provider()
        download_trigger.kubespider_downloader.handle_download_remove(Downloader(
            downloader=[download_provider_name]
        ))

    def save_state(self, provider_name: str, provider_state: dict):
        all_pt_state = self.state_config.read().get('pt_state', {})
        all_pt_state[provider_name] = provider_state
        self.state_config.parcial_update(lambda all_state: all_state.update({'pt_state': all_pt_state}))

    def load_state(self, provider_name: str) -> dict:
        empty_state = {
            'last_start_time': 0,
            'download_sum_size': 0,
            'costs_sum_size': 0,
            'torrent_list': []
        }
        all_pt_state = self.state_config.read().get('pt_state', {})
        if all_pt_state is None:
            return empty_state

        state = all_pt_state.get(provider_name, {})
        if len(state) == 0:
            return empty_state
        return state


kubespider_pt_server: PTServer = None
