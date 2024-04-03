from download_provider.provider import DownloadProvider
from download_provider.aria2_download_provider.provider import Aria2DownloadProvider
from download_provider.qbittorrent_download_provider.provider import QbittorrentDownloadProvider
from download_provider.tiktok_dlp_download_provider.provider import TiktokDownloadProvider
from download_provider.transmission_download_provider.provider import TransmissionProvider
from download_provider.xunlei_download_provider.provider import XunleiDownloadProvider
from download_provider.youget_download_provider.provider import YougetDownloadProvider
from download_provider.ytdlp_download_provider.provider import YTDlpDownloadProvider
from download_provider.yutto_download_provider.provider import YuttoDownloadProvider

providers = [
    Aria2DownloadProvider,
    QbittorrentDownloadProvider,
    TiktokDownloadProvider,
    TransmissionProvider,
    XunleiDownloadProvider,
    YougetDownloadProvider,
    YTDlpDownloadProvider,
    YuttoDownloadProvider,
]

__all__ = [
    'providers',
    'DownloadProvider',
    *map(lambda x: x.__name__, providers)
]
