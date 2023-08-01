import time
import logging
import queue

from api import types
from api.values import Config
from utils import helper
from utils.config_reader import YamlFileConfigReader
import source_provider.provider as sp
from core import download_trigger, notification_server


class PeriodServer:
    def __init__(self, source_providers, download_providers) -> None:
        self.state_config = YamlFileConfigReader(Config.STATE.config_path())
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
        if provider.get_provider_listen_type() != types.SOURCE_PROVIDER_PERIOD_TYPE:
            return None

        provider.load_config()
        links = provider.get_links("")
        link_type = provider.get_link_type()

        provider_name = provider.get_provider_name()
        state = self.load_state(provider_name)

        err = None
        for source in links:
            if helper.get_unique_hash(source['link']) in state:
                continue
            source_link_type = link_type if 'link_type' not in source.keys() else source['link_type']
            logging.info('Find new resource:%s/%s', provider_name, helper.format_long_string(source['link']))
            download_final_path = helper.convert_file_type_to_path(source['file_type']) + '/' + source['path']
            err = download_trigger.kubespider_downloader. \
                download_file(source['link'], download_final_path, \
                              source_link_type, provider)
            if err is not None:
                notification_server.kubespider_notification_server.send_message(
                    title=f"[{provider_name}] download failed", **source
                )
                break
            state.append(helper.get_unique_hash(source['link']))
            notification_server.kubespider_notification_server.send_message(
                title=f"[{provider_name}] start download", **source
            )

        self.save_state(provider_name, state)

        return err

    def load_state(self, provider_name) -> list:
        return self.state_config.read().get(provider_name, [])

    def save_state(self, provider_name, state) -> None:
        self.state_config.parcial_update(lambda all_state: all_state.update({provider_name: state}))


kubespider_period_server = PeriodServer(None, None)
