import os
import logging
import json

from http.server import BaseHTTPRequestHandler

from core import download_trigger
from core import kubespider_global
from core import period_server
from api import types


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
            file_type = self.get_file_type(source)
            # If we not match the source provider, just download to common path
            path = os.path.join('common', path)
            err = download_trigger.kubespider_downloader.download_file(source, path, file_type)

        if match_one_provider is True:
            if match_provider.get_provider_type() == types.SOURCE_PROVIDER_DISPOSABLE_TYPE:
                file_type = match_provider.get_file_type()
                links = match_provider.get_links(source)
                download_final_path = os.path.join(match_provider.get_download_path(), path)
                for download_link in links:
                    err = download_trigger.kubespider_downloader.download_file(download_link, \
                        download_final_path, file_type)
                    if err is not None:
                        break
            else:
                match_provider.update_config(source)
                period_server.kubespider_period_server.trigger_run(match_provider.get_provider_name())

        if err is None:
            self.send_ok_response()
        else:
            self.send_bad_response(err)

    def get_file_type(self, url):
        if url.endswith("torrent"):
            return 'torrent'
        if url.startswith('magnet:'):
            return 'magnet'

        return 'general'

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
