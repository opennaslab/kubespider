import source_provider.mikanani_source_provider.provider as mikanani_source_provider
import source_provider.btbtt12_disposable_source_provider.provider as btbtt12_disposable_source_provider
import source_provider.meijutt_source_provider.provider as meijutt_source_provider
import source_provider.bilibili_source_provider.provider as bilibili_source_provider
import source_provider.youtube_source_provider.provider as youtube_source_provider
import source_provider.general_rss_source_provider.provider as general_rss_source_provider

import download_provider.aria2_download_provider.provider as aria2_download_provider
import download_provider.xunlei_download_provider.provider as xunlei_download_provider
import download_provider.qbittorrent_download_provider.provider as qbittorrent_download_provider
import download_provider.youget_download_provider.provider as youget_download_provider
import download_provider.ytdlp_download_provider.provider as ytdlp_download_provider

from utils import helper
from utils.helper import Config

source_provider_init_func = {
    'bilibili_source_provider': bilibili_source_provider.BilibiliSourceProvider,
    'btbtt12_disposable_source_provider': btbtt12_disposable_source_provider.Btbtt12DisposableSourceProvider,
    'meijutt_source_provider': meijutt_source_provider.MeijuttSourceProvider,
    'mikanani_source_provider': mikanani_source_provider.MikananiSourceProvider,
    'youtube_source_provider': youtube_source_provider.YouTubeSourceProvider,
    'general_rss_source_provider': general_rss_source_provider.GeneralRssSourceProvider
}

def get_source_provider(provider_name: str, config: dict):
    provider_type = config['type']
    try:
        return source_provider_init_func[provider_type](provider_name)
    except Exception as exc:
        raise Exception(str('unknown source provider type %s', provider_type)) from exc

source_providers = []

source_config = helper.load_config(Config.SOURCE_PROVIDER)
for name in source_config:
    source_providers.append(get_source_provider(name, source_config[name]))

downloader_provider_init_func = {
    'aria2_download_provider': aria2_download_provider.Aria2DownloadProvider,
    'qbittorrent_download_provider': qbittorrent_download_provider.QbittorrentDownloadProvider,
    'xunlei_download_provider': xunlei_download_provider.XunleiDownloadProvider,
    'youget_download_provider': youget_download_provider.YougetDownloadProvider,
    'ytdlp_download_provider': ytdlp_download_provider.YTDlpDownloadProvider,
}

def get_download_provider(provider_name: str, config: dict):
    provider_type = config['type']
    try:
        return downloader_provider_init_func[provider_type](provider_name)
    except Exception as exc:
        raise Exception(str('unknown download provider type %s', provider_type)) from exc


download_providers = []

download_config = helper.load_config(Config.DOWNLOAD_PROVIDER)
for name in download_config:
    download_providers.append(get_download_provider(name, download_config[name]))

enabled_source_provider = []
enabled_download_provider = []
