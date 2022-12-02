import os
import logging
import configparser
import source_provider.provider as abstract_source_provider
import source_provider.torrent_source_provider.provider as torrent_source_provider
import download_provider.provider as abstract_download_provider
import download_provider.motrix_download_provider.provider as motrix_source_provider

source_providers = [
    torrent_source_provider.TorrentSourceProvider()
]

download_providers = [
    motrix_source_provider.MotrixDownloadProvider()
]

def run():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s-%(levelname)s: %(message)s')

    enabled_source_provider = []
    enabled_download_provider = []

    source_provider_cfg = load_source_provide_config()
    download_provider_cfg = load_download_provider_config()
    for provider in source_providers:
        provider_name = provider.get_provider_name()
        if source_provider_cfg.get(provider_name, 'ENABLE') == 'true':
            logging.info(f'Source Provider:{provider_name} enabled...')
            enabled_source_provider.append(provider)
    
    for provider in download_providers:
        provider_name = provider.get_provider_name()
        if download_provider_cfg.get(provider_name, 'ENABLE') == 'true':
            logging.info(f'Download Provider:{provider_name} enabled...')
            enabled_download_provider.append(provider)

def load_source_provide_config():
    cfg = configparser.ConfigParser()
    config_path = '/Users/cesign/git/kubespider/config'
    #config_path = os.getenv('KUBESPIDER_CONFIG_PATH')
    if config_path == None:
        config_path = '~/config'
    cfg.read(os.path.join(config_path, 'source_provider.cfg'))
    return cfg

def load_download_provider_config():
    cfg = configparser.ConfigParser()
    config_path = '/Users/cesign/git/kubespider/config'
    #config_path = os.getenv('KUBESPIDER_CONFIG_PATH')
    if config_path == None:
        config_path = '~/config'
    cfg.read(os.path.join(config_path, 'download_provider.cfg'))
    return cfg