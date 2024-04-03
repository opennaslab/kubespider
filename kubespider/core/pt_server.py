# -*- coding: utf-8 -*-

import time
import os
import _thread

import logging

from core import download_manager
from pt_provider import provider
from utils.config_reader import YamlFileConfigReader
from utils.values import Config, FILE_TYPE_TO_PATH
from utils.types import FILE_TYPE_PT, LINK_TYPE_TORRENT
from utils.values import Resource, Downloader


class PTServer:
    def __init__(self, pt_providers: list) -> None:
        self.pt_providers: list[provider.PTProvider] = pt_providers
        self.state_config = YamlFileConfigReader(Config.STATE.config_path())

    def run_single_pt(self, current_provider: provider.PTProvider):
        while True:
            provider_name = current_provider.get_provider_name()
            provider_state = self.load_state(provider_name)
            keeping_time = current_provider.get_keeping_time()
            cost_sum_size = current_provider.get_cost_sum_size()
            max_sum_size = current_provider.get_max_sum_size()

            logging.info("PT provider(%s) downloading size is:%f/%s, cost downloading size:%f/%f",
                         provider_name, provider_state['download_sum_size'],
                         max_sum_size, provider_state['costs_sum_size'], cost_sum_size)

            current_time = int(time.time())
            if current_time - provider_state['last_start_time'] > keeping_time:
                logging.info("PT provider(%s) time reached, remove all downlaod tasks, current time is %d, last start time is %d", provider_name, current_time, provider_state['last_start_time'])
                self.trigger_remove_tasks(current_provider)
                provider_state['last_start_time'] = current_time
                provider_state['download_sum_size'] = 0.0
                provider_state['costs_sum_size'] = 0.0

            current_provider.go_attendance()
            links = current_provider.get_links()
            for link in links:
                link_size = float(link['size'])
                if link['torrent'] in provider_state['torrent_list']:
                    logging.info("PT provider(%s) already download torrent:%s, skip it", provider_name,
                                 link['torrent'])
                    continue

                if link['free']:
                    if link_size + provider_state['download_sum_size'] < max_sum_size:
                        self.trigger_download_tasks(link['torrent'], current_provider)
                        provider_state['download_sum_size'] += link_size
                        provider_state['torrent_list'].append(link['torrent'])
                        logging.info('Add one task(%fGB), now is %fGB', link_size,
                                     provider_state['download_sum_size'])
                else:
                    if provider_state['costs_sum_size'] <= 0.0:
                        continue

                    # In order to meet the download requirements, we need to make the threshold higher
                    if link_size + provider_state['costs_sum_size'] < cost_sum_size + 5.0:
                        self.trigger_download_tasks(link['torrent'], current_provider)
                        provider_state['costs_sum_size'] += link_size
                        provider_state['torrent_list'].append(link['torrent'])
                        logging.info('Add one task(%fGB), now is %fGB', link_size, provider_state['costs_sum_size'])

            self.save_state(provider_name, provider_state)
            time.sleep(3600)

    def run(self):
        for iter_provider in self.pt_providers:
            _thread.start_new_thread(self.run_single_pt, (iter_provider,))
        while True:
            time.sleep(3600)

    @staticmethod
    def trigger_download_tasks(pt_source: str, pt_provider: provider.PTProvider):
        logging.info("Start downloading: %s", pt_source)
        download_provider_name = pt_provider.get_download_provider()
        download_path = os.path.join(FILE_TYPE_TO_PATH[FILE_TYPE_PT], download_provider_name)
        err = download_manager.kubespider_download_server.download_file(Resource(
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
        download_manager.kubespider_download_server.handle_download_remove(Downloader(
            download_provider_names=[download_provider_name]
        ))

    def save_state(self, provider_name: str, provider_state: dict):
        all_pt_state = self.state_config.read().get('pt_state', {})
        if all_pt_state is None:
            all_pt_state = {}
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
