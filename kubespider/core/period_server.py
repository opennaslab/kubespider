import time
import logging
import queue

from api import types
from core import download_trigger
from utils import helper
from utils.helper import Config
from source_provider import general_rss_source_provider, provider as pd
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
                if provider.get_provider_name() == "general_rss_source_provider":
                    err = self.rss_deal_provider(provider)
                else:
                    err = self.run_single_provider(provider)

            if err is not None:
                # If error, try again
                self.queue.put(True)

    def trigger_run(self) -> None:
        self.queue.put(True)


    def rss_deal_provider(self, provider: sp.SourceProvider) -> TypeError:
        configs = pd.load_source_provide_config(provider.get_provider_name()).get("rss")
        logging.info("-------------------")
        logging.info(configs)
        logging.info("-------------------")
        err_flag = None
        for rss_config in configs:
            if rss_config.get("provider_enabled"):
                rss_provider = general_rss_source_provider.provider.GeneralRssSourceProvider(rss_config)
                general_rss_source_provider_disposable = self.load_state("general_rss_source_provider_disposable")
                if rss_provider.get_provider_type() != types.SOURCE_PROVIDER_PERIOD_TYPE and rss_provider.get_rss_hub_link() not in general_rss_source_provider_disposable:
                    download_links_with_provider("", rss_provider)
                    self.save_state(rss_provider.get_rss_hub_link(), general_rss_source_provider_disposable)
                else:
                    err = self.rss_single_provider(provider)
                    if err is not None:
                        err_flag = False
        return err_flag


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

def download_links_with_provider(source: str, source_provider: sp.SourceProvider):
    link_type = source_provider.get_link_type()
    links = source_provider.get_links(source)
    specific_download_provider = source_provider.get_download_provider()
    for download_link in links:
        # The path rule should be like: {file_type}/{file_title}
        download_final_path = helper.convert_file_type_to_path(download_link['file_type']) + '/' + download_link['path']
        err = download_trigger.kubespider_downloader.\
            download_file(download_link['link'], \
                          download_final_path, link_type,\
                            specific_download_provider)
        if err is not None:
            return err
    return None

kubespider_period_server = PeriodServer(None, None)
