import source_provider.mikanani_source_provider.provider as mikanani_source_provider
import source_provider.btbtt12_disposable_source_provider.provider as btbtt12_disposable_source_provider
import source_provider.meijutt_source_provider.provider as meijutt_source_provider
import source_provider.bilibili_source_provider.provider as bilibili_source_provider
import download_provider.aria2_download_provider.provider as aria2_download_provider
import download_provider.xunlei_download_provider.provider as xunlei_download_provider
import download_provider.qbittorrent_download_provider.provider as qbittorrent_download_provider
import download_provider.youget_download_provider.provider as youget_download_provider

source_providers = [
    mikanani_source_provider.MikananiSourceProvider(),
    btbtt12_disposable_source_provider.Btbtt12DisposableSourceProvider(),
    meijutt_source_provider.MeijuttSourceProvider(),
    bilibili_source_provider.BilibiliSourceProvider(),
]

download_providers = [
    aria2_download_provider.Aria2DownloadProvider(),
    xunlei_download_provider.XunleiDownloadProvider(),
    qbittorrent_download_provider.QbittorrentDownloadProvider(),
    youget_download_provider.YougetDownloadProvider(),
]

enabled_source_provider = []
enabled_download_provider = []
