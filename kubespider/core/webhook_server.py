import logging
import json
from urllib.parse import urlparse

from http.server import BaseHTTPRequestHandler

from core import download_trigger
from core import kubespider_global
from core import period_server
from api import types
from utils import helper


class WebhookServer(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server) -> None:
        self.source_provider = kubespider_global.enabled_source_provider
        super().__init__(request, client_address, server)

    def do_POST(self):
        args = self.rfile.read(int(self.headers['content-length'])).decode("utf-8")
        data = json.loads(args)
        source = data['dataSource']
        path = ''
        if 'path' in data.keys():
            path = data['path']
        logging.info('Get webhook trigger:%s', source)

        match_one_provider = False
        match_provider = None
        for provider in self.source_provider:
            if provider.is_webhook_enable() and provider.should_handle(source):
                match_provider = provider
                # Do not break here, in order to check whether it matchs multiple provider
                match_one_provider = True

        err = None
        if match_one_provider is False:
            link_type = self.get_link_type(source)
            # If we not match the source provider, just download to common path
            # TODO: implement a better classification if no source provider match
            path = helper.convert_file_type_to_path(types.FILE_TYPE_COMMON) + '/' + path
            err = download_trigger.kubespider_downloader.download_file(source, path, link_type)

        if match_one_provider is True:
            if match_provider.get_provider_type() == types.SOURCE_PROVIDER_DISPOSABLE_TYPE:
                link_type = match_provider.get_link_type()
                links = match_provider.get_links(source)
                for download_link in links:
                    # The path rule should be like: {file_type}/{file_title}
                    download_final_path = helper.convert_file_type_to_path(download_link['file_type']) + '/' + download_link['path']
                    err = download_trigger.kubespider_downloader.download_file(download_link['link'], \
                        download_final_path, link_type)
                    if err is not None:
                        break
            else:
                match_provider.update_config(source)
                period_server.kubespider_period_server.trigger_run(match_provider.get_provider_name())

        if err is None:
            self.send_ok_response()
        else:
            self.send_bad_response(err)

    def get_link_type(self, url):
        if url.startswith('magnet:'):
            return types.LINK_TYPE_MAGNET
        if urlparse(url).path.endswith('torrent'):
            return types.LINK_TYPE_TORRENT

        # TODO: implement other type, like music mv or short video
        return types.LINK_TYPE_GENERAL

    def send_ok_response(self):
        self.send_response(200)
        self.send_header("Content-type", "application/text")
        self.end_headers()
        self.wfile.write(bytes('ok', "utf-8"))

    def send_bad_response(self, err):
        self.send_response(500)
        self.send_header("Content-type", "application/text")
        self.end_headers()
        self.wfile.write(bytes(str(err), "utf-8"))
