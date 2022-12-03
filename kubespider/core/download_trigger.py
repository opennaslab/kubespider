import logging
import os
import uuid
from urllib import request
from urllib.request import Request, urlopen
from utils import helper

class KubespiderDownloader:
    def __init__(self, download_providers) -> None:
        self.download_provider = download_providers

    def download_file(self, url, path, fileType):
        if fileType == 'torrent':
            logging.info('Download torrent file')
            tmp_file = helper.get_tmp_file_name(url)

            headers = ("User-Agent","Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE")
            req = request.build_opener()
            req.addheaders=[headers]
            torrent_data = req.open(url).read()
            with open(tmp_file, 'wb') as f:
                f.write(torrent_data)
                f.close()
            for provider in self.download_provider:
                provider.send_torrent_task(tmp_file, path)
            return


        logging.info('Download general type file')
        for provider in self.download_provider:
            provider.send_general_task(url, path)
