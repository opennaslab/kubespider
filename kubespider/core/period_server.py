import time
import logging
import queue

from api import types
from core import download_trigger
from utils import helper
from utils.helper import Config
import source_provider.provider as sp

class PeriodServer:
    def __init__(self, source_providers, download_providers) -> None:
        self.period_seconds = 3600
        self.source_providers = source_providers
        self.download_providers = download_providers
        self.queue = queue.Queue()

    def run_producer(self) -> None:
        while True:
            self.queue.put(True)
            time.sleep(self.period_seconds)

    def run_consumer(self) -> None:
        while True:
            time.sleep(1)
            get_trigger = self.queue.get()
            if get_trigger is None:
                continue

            err = None
            for provider in self.source_providers:
                err = self.run_single_provider(provider)

            if err is not None:
                # If error, try again
                self.queue.put(True)

    def trigger_run(self) -> None:
        self.queue.put(True)

    def run_single_provider(self, provider: sp.SourceProvider) -> TypeError:
        if provider.get_provider_type() != types.SOURCE_PROVIDER_PERIOD_TYPE:
            return None

        provider.load_config()
        links = provider.get_links("")
        link_type = provider.get_link_type()
        specific_download_provider = provider.get_download_provider()

        provider_name = provider.get_provider_name()
        state = self.load_state(provider_name)

        err = None
        for source in links:
            if helper.get_unique_hash(source['link']) in state:
                continue

            logging.info('Find new resource:%s/%s', provider_name, helper.format_long_string(source['link']))
            download_final_path = helper.convert_file_type_to_path(source['file_type']) + '/' + source['path']
            err = download_trigger.kubespider_downloader. \
                download_file(source['link'], download_final_path, \
                              link_type, specific_download_provider)
            if err is not None:
                break
            state.append(helper.get_unique_hash(source['link']))

        self.save_state(provider_name, state)

        return err

    def load_state(self, provider_name) -> list:
        all_state = helper.load_config(Config.STATE)
        if provider_name not in all_state.keys():
            return []
        return all_state[provider_name]

    def save_state(self, provider_name, state) -> None:
        all_state = helper.load_config(Config.STATE)
        all_state[provider_name] = state
        helper.dump_config(Config.STATE, all_state)

kubespider_period_server = PeriodServer(None, None)
