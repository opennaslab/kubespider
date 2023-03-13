import logging
import time
from urllib import request

from utils import helper
from api import types
import download_provider.provider as download_provider


class KubespiderDownloader:
    def __init__(self, download_providers: download_provider.DownloadProvider):
        self.download_providers = download_providers

    def period_run(self):
        while True:
            time.sleep(120)
            self.handle_defective_downloade()

    def handle_defective_downloade(self):
        provider_len = len(self.download_providers)
        if provider_len <= 1:
            return

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

    def download_file(self, url, path, link_type, provider_name=None):
        if link_type == types.LINK_TYPE_TORRENT:
            return self.handle_torrent_download(url, path, provider_name)

        if link_type == types.LINK_TYPE_MAGNET:
            return self.handle_magnet_download(url, path, provider_name)

        if link_type == types.LINK_TYPE_GENERAL:
            return self.handle_general_download(url, path, provider_name)

        return None

    def handle_torrent_download(self, url, path, provider_name=None):
        logging.info('Download torrent file')
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
        for provider in self.download_providers:
            if provider_name is not None and \
                provider_name != provider.get_provider_name():
                continue
            provider.load_config()
            err = None
            err = provider.send_torrent_task(tmp_file, path)
            if err is not None:
                return err
            break
        return err

    def handle_magnet_download(self, url, path, provider_name=None):
        logging.info('Download mangent file')
        err = None
        for provider in self.download_providers:
            if provider_name is not None and \
                provider_name != provider.get_provider_name():
                continue
            provider.load_config()
            err = provider.send_magnet_task(url, path)
            if err is not None:
                continue
            break
        return err

    def handle_general_download(self, url, path, provider_name=None):
        logging.info('Download general file')
        err = None
        for provider in self.download_providers:
            if provider_name is not None and \
                provider_name != provider.get_provider_name():
                continue
            provider.load_config()
            err = provider.send_general_task(url, path)
            if err is not None:
                continue
            break
        return err

kubespider_downloader = KubespiderDownloader(None)
