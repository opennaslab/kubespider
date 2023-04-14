import logging
import time
from urllib import request

from utils import helper
from api import types
import download_provider.provider as dp


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
            logging.info("%s,%s", provider_now.get_provider_name(), provider_next.get_provider_name())
            provider_now.load_config()
            provider_next.load_config()

            tasks = provider_now.get_defective_task()
            logging.info("Find defective tasks:%d/%s", len(tasks), provider_now.get_provider_name())
            for task in tasks:
                self.download_file(task['url'], task['path'], task['linkType'], provider_next.get_provider_name())

    def filter_downloader(self, name_list=None, provider_type=None) -> list:
        if name_list is not None:
            provider = list(filter(lambda p: p.get_provider_name() in name_list, self.download_providers))
        else:
            provider = self.download_providers
        
        if provider_type is not None:
            provider = list(filter(lambda p: p.get_provider_type() == provider_type, provider))
        name = list(map(lambda p: p.get_provider_name(), provider))
        logging.info('filtering downloader by name %s type %s, result %s', str(name_list), str(provider_type), str(name))
        return provider

    def download_file(self, url, path, link_type, provider_name=None, provider_type=None, extra_param=None) -> TypeError:        
        downloader = self.filter_downloader(provider_name, provider_type)
        logging.info('download link type %s, with provider size %s', link_type, len(downloader))
        if link_type == types.LINK_TYPE_TORRENT:
            return self.handle_torrent_download(url, path, downloader, extra_param)

        if link_type == types.LINK_TYPE_MAGNET:
            return self.handle_magnet_download(url, path, downloader, extra_param)

        if link_type == types.LINK_TYPE_GENERAL:
            return self.handle_general_download(url, path, downloader, extra_param)

        logging.warning("Unknown link type:%s", link_type)

        return None

    def handle_torrent_download(self, url, path, downloader: list, extra_param=None) -> TypeError:
        tmp_file = helper.get_tmp_file_name(url)

        headers = ("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE")
        req = request.build_opener()
        req.addheaders = [headers]
        try:
            torrent_data = req.open(url, timeout=10).read()
        except Exception as err:
            logging.info('Download torrent error:%s', err)
            return err
        with open(tmp_file, 'wb') as torrent_file:
            torrent_file.write(torrent_data)
            torrent_file.close()

        err = None
        for provider in downloader:
            logging.info('Download torrent file with downloader(%s)', provider.get_provider_name())
            provider.load_config()
            err = provider.send_torrent_task(tmp_file, path, extra_param)
            if err is not None:
                logging.warning('Download torrent file error:%s', err)
                continue
            break
        return err

    def handle_magnet_download(self, url, path, downloader=None, extra_param=None) -> TypeError:
        err = None
        for provider in downloader:
            logging.info('Download mangent file with downloader(%s)', provider.get_provider_name())
            provider.load_config()
            err = provider.send_magnet_task(url, path, extra_param)
            if err is not None:
                logging.warning('Download torrent file error:%s', err)
                continue
            break
        return err

    def handle_general_download(self, url, path, downloader=None, extra_param=None) -> TypeError:
        err = None
        for provider in downloader:
            logging.info('Download general file with downloader(%s)', provider.get_provider_name())
            provider.load_config()
            err = provider.send_general_task(url, path, extra_param)
            if err is not None:
                logging.warning('Download torrent file error:%s', err)
                continue
            break
        return err

kubespider_downloader = KubespiderDownloader(None)
