import time
import configparser
import os
import logging

from api import types
from core import kubespider
from utils import helper

class PeriodServer:
    def __init__(self, source_providers, download_providers) -> None:
        self.period_seconds = 3600
        self.source_providers = source_providers
        self.download_providers = download_providers
        self.state_file_dir = os.getenv('HOME') + '/.kubespider'

    def run(self):
        while True:
            meetError = False
            for provider in self.source_providers:
                meetError = self.run_single_provider(provider)
            
            if not meetError:
                time.sleep(self.period_seconds)
            else:
                time.sleep(20)
    
    def trigger_run(self, provider_name):
        for provider in self.source_providers:
            if provider_name != provider.get_provider_name():
                continue
            self.run_single_provider(provider)
            
    def run_single_provider(self, provider):
        meetError = False
        if provider.get_provider_type() == types.SOURCE_PROVIDER_PERIOD_TYPE:
            provider.load_config()
            links = provider.get_links("")
            file_type = provider.get_file_type()
            download_final_path = provider.get_download_path()

            provider_name = provider.get_provider_name()
            state = self.load_state(provider_name)

            downloaded_links = dict(state.items(provider_name))
            for source in links:
                if helper.get_unique_hash(source) in downloaded_links:
                    continue
                logging.info(f"Find new resource:{source}")
                if kubespider.kubespider_downloader.download_file(source, download_final_path, file_type) == False:
                    meetError = True
                    break
                downloaded_links[helper.get_unique_hash(source)] = '1'

            state[provider_name] = downloaded_links
            self.save_state(state)
        
        return meetError

    def load_state(self, provider_name):
        cfg = configparser.ConfigParser()
        if not os.path.exists(self.state_file_dir):
            os.makedirs(self.state_file_dir)
        if os.path.exists(self.state_file_dir+'/state.cfg'):
            cfg.read(self.state_file_dir+'/state.cfg')
            if provider_name not in cfg.sections():
                cfg.add_section(provider_name)
        else:
            cfg.add_section(provider_name)
        return cfg

    def save_state(self, state):
        with open(self.state_file_dir+'/state.cfg', 'w') as state_file:
            state.write(state_file)
            state_file.close()