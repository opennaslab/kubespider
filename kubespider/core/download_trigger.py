import logging
import time

from utils import helper
from api import types
import download_provider.provider as dp
import source_provider.provider as sp


class KubespiderDownloader:
    def __init__(self, download_providers: dp.DownloadProvider):
        self.download_providers: dp.DownloadProvider = download_providers

    def period_run(self):
        while True:
            # For certain download providers, the task start time is not available.
            # Therefore, specifying a time here would be futile.
            time.sleep(180)
            self.handle_defective_downloade()

    def handle_defective_downloade(self):
        provider_len = len(self.download_providers)
        if provider_len <= 1:
            return

        # Start from the last one, the task in laster downloder will never be removed
        for index in range(provider_len - 2, -1, -1):
            # load config
            provider_now = self.download_providers[index]
            provider_next = self.download_providers[index+1]

            err = provider_now.load_config()
            if err is not None:
                continue

            err = provider_next.load_config()
            if err is not None:
                continue

            tasks = provider_now.get_defective_task()
            logging.info("Find defective tasks:%d/%s", len(tasks), provider_now.get_provider_name())
            for task in tasks:
                self.download_file(task['url'], task['path'], task['linkType'],
                                   download_provoder=provider_next)

    def filter_downloader_by_source(self, source_provider: sp.SourceProvider=None) -> list:
        if source_provider is None:
            return self.download_providers
        name_list = source_provider.get_prefer_download_provider()
        provider_type = source_provider.get_download_provider_type()
        if name_list is not None:
            provider = list(filter(lambda p: p.get_provider_name() in name_list, self.download_providers))
        else:
            provider = self.download_providers
        if provider_type is not None:
            provider = list(filter(lambda p: p.get_provider_type() == provider_type, provider))
        name = list(map(lambda p: p.get_provider_name(), provider))
        logging.info('filtering downloader by name %s type %s, result %s', str(name_list), str(provider_type), str(name))
        return provider

    def filter_downloader_by_name(self, name: str) -> dp.DownloadProvider:
        provider = list(filter(lambda p: p.get_provider_name() == name, self.download_providers))
        if len(provider) == 0:
            logging.warning('Downloader %s not found', name)
            return None
        return provider[0]

    def download_file(self, url, path, link_type, \
                      source_provider: sp.SourceProvider=None, \
                        download_provoder: dp.DownloadProvider=None) -> TypeError:
        downloader_list = []
        if download_provoder is not None:
            downloader_list = [download_provoder]
        else:
            downloader_list = self.filter_downloader_by_source(source_provider)
        extra_param = None
        if source_provider is not None:
            extra_param = source_provider.get_download_param()

        logging.info('download link type %s, with provider size %s', link_type, len(downloader_list))
        if len(downloader_list) == 0:
            logging.error('Downloader for %s not found, check your configuration!!!', source_provider.get_provider_name())
        if link_type == types.LINK_TYPE_TORRENT:
            return self.handle_torrent_download(url, path, downloader_list, extra_param)

        if link_type == types.LINK_TYPE_MAGNET:
            return self.handle_magnet_download(url, path, downloader_list, extra_param)

        if link_type == types.LINK_TYPE_GENERAL:
            return self.handle_general_download(url, path, downloader_list, extra_param)

        logging.warning("Unknown link type:%s", link_type)

        return None

    def handle_torrent_download(self, url: str, path: str, downloader_list: list, extra_param=None) -> TypeError:
        tmp_file = None

        if url.startswith('http'):
            tmp_file = helper.get_tmp_file_name(url)
            req = helper.get_request_controller()
            try:
                torrent_data = req.open(url, timeout=10).read()
            except Exception as err:
                logging.info('Download torrent error:%s', err)
                return err
            with open(tmp_file, 'wb') as torrent_file:
                torrent_file.write(torrent_data)
                torrent_file.close()
        else:
            tmp_file = url

        err = None
        for provider in downloader_list:
            logging.info('Download torrent file with downloader(%s)', provider.get_provider_name())
            provider.load_config()
            err = provider.send_torrent_task(tmp_file, path, extra_param)
            if err is not None:
                logging.warning('Download torrent file error:%s', err)
                continue
            break
        return err

    def handle_magnet_download(self, url, path, downloader_list=None, extra_param=None) -> TypeError:
        err = None
        for provider in downloader_list:
            logging.info('Download mangent file with downloader(%s)', provider.get_provider_name())
            provider.load_config()
            err = provider.send_magnet_task(url, path, extra_param)
            if err is not None:
                logging.warning('Download torrent file error:%s', err)
                continue
            break
        return err

    def handle_general_download(self, url, path, downloader_list=None, extra_param=None) -> TypeError:
        err = None
        for provider in downloader_list:
            logging.info('Download general file with downloader(%s)', provider.get_provider_name())
            provider.load_config()
            err = provider.send_general_task(url, path, extra_param)
            if err is not None:
                logging.warning('Download torrent file error:%s', err)
                continue
            break
        return err

    def handle_download_remove(self, downloader_list=None, extra_param=None):
        for provider in downloader_list:
            provider.load_config()
            provider.remove_tasks(extra_param)

kubespider_downloader = KubespiderDownloader(None)
