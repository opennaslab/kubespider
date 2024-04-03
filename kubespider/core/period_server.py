import time
import logging
import queue
import os

from utils.values import Config, Downloader
from utils import helper, types
from utils.config_reader import YamlFileConfigReader
from source_provider.provider import SourceProvider
from core import download_manager, notification_manager


class PeriodServer:
    def __init__(self, source_providers) -> None:
        self.state_config = YamlFileConfigReader(Config.STATE.config_path())
        self.period_seconds = 3600
        self.source_providers = source_providers
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

    def run_single_provider(self, provider: SourceProvider) -> TypeError:
        if provider.get_provider_listen_type() != types.SOURCE_PROVIDER_PERIOD_TYPE:
            return None

        provider.load_config()
        links = provider.get_links(None)
        if links is None:
            return None
        link_type = provider.get_link_type()

        provider_name = provider.get_provider_name()
        state = self.load_state(provider_name)

        err = None
        for source in links:
            if source.uid in state:
                continue
            if source.link_type is None:
                source.link_type = link_type
            source.put_extra_params(provider.get_download_param())
            logging.info('Find new resource:%s/%s', provider_name, helper.format_long_string(source.url))
            source.path = os.path.join(helper.convert_file_type_to_path(source.file_type), source.path)
            err = download_manager.kubespider_download_server.download_file(source, Downloader(
                provider.get_download_provider_type(),
                provider.get_prefer_download_provider(),
            ))

            if err is not None:
                notification_manager.kubespider_notification_server.send_message(
                    title=f"[{provider_name}] download failed", url=source.url, path=source.path,
                    link_type=source.link_type, file_type=source.file_type, **source.extra_params()
                )
                break
            #  add resource to state
            state.append(source.uid)

            notification_manager.kubespider_notification_server.send_message(
                title=f"[{provider_name}] start download", url=source.url, path=source.path,
                link_type=source.link_type, file_type=source.file_type, **source.extra_params()
            )

        self.save_state(provider_name, state)

        return err

    def load_state(self, provider_name) -> list:
        return self.state_config.read().get(provider_name, [])

    def save_state(self, provider_name, state) -> None:
        self.state_config.parcial_update(lambda all_state: all_state.update({provider_name: state}))


kubespider_period_server = PeriodServer(None)
