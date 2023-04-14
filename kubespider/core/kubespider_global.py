import source_provider.mikanani_source_provider.provider as mikanani_source_provider
import source_provider.btbtt12_disposable_source_provider.provider as btbtt12_disposable_source_provider
import source_provider.meijutt_source_provider.provider as meijutt_source_provider
import source_provider.bilibili_source_provider.provider as bilibili_source_provider
import source_provider.youtube_source_provider.provider as youtube_source_provider

import download_provider.aria2_download_provider.provider as aria2_download_provider
import download_provider.xunlei_download_provider.provider as xunlei_download_provider
import download_provider.qbittorrent_download_provider.provider as qbittorrent_download_provider
import download_provider.youget_download_provider.provider as youget_download_provider

from utils import helper
from utils.helper import Config

def get_source_provider(provider_name: str, config: dict):
    provider_type = config['type']
    if provider_type == 'bilibili_source_provider':
        return bilibili_source_provider.BilibiliSourceProvider(provider_name)
    if provider_type == 'btbtt12_disposable_source_provider':
        return btbtt12_disposable_source_provider.Btbtt12DisposableSourceProvider(provider_name)
    if provider_type == 'meijutt_source_provider':
        return meijutt_source_provider.MeijuttSourceProvider(provider_name)
    if provider_type == 'mikanani_source_provider':
        return mikanani_source_provider.MikananiSourceProvider(provider_name)
    if provider_type == 'youtube_source_provider':
        return youtube_source_provider.YouTubeSourceProvider(provider_name)
    raise Exception(str('unknown source provider type %s', provider_type))

source_providers = []

source_config = helper.load_config(Config.SOURCE_PROVIDER)
for name in source_config:
    source_providers.append(get_source_provider(name, source_config[name]))


def get_download_provider(provider_name: str, config: dict):
    provider_type = config['type']
    if provider_type == 'aria2_download_provider':
        return aria2_download_provider.Aria2DownloadProvider(provider_name)
    if provider_type == 'qbittorrent_download_provider':
        return qbittorrent_download_provider.QbittorrentDownloadProvider(provider_name)
    if provider_type == 'xunlei_download_provider':
        return xunlei_download_provider.XunleiDownloadProvider(provider_name)
    if provider_type == 'youget_download_provider':
        return youget_download_provider.YougetDownloadProvider(provider_name)
    raise Exception(str('unknown download provider type %s', provider_type))


download_providers = []

download_config = helper.load_config(Config.DOWNLOAD_PROVIDER)
for name in download_config:
    download_providers.append(get_download_provider(name, download_config[name]))

enabled_source_provider = []
enabled_download_provider = []
