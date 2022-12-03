import logging
import urllib
import socketserver
import json
import os
from http.server import BaseHTTPRequestHandler
from core import kubespider
from api import types

class WebhookServer(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server) -> None:
        self.source_provider = kubespider.enabled_source_provider
        super().__init__(request, client_address, server)
    
    def do_POST(self):
        args = self.rfile.read(int(self.headers['content-length'])).decode("utf-8")
        data = json.loads(args)
        source = data['dataSource']
        path = ''
        if 'path' in data.keys():
            path = data['path']
        logging.info(f'Get webhook trigger:{source}')

        matchOneProvider = False
        matchProvider = None
        for provider in self.source_provider:
            if provider.is_webhook_enable() and provider.should_handle(source):
                matchProvider = provider
                # Do not break here, in order to check whether it matchs multiple provider
                matchOneProvider = True
        
        if matchOneProvider == False:
            file_type = self.get_file_type(source)
            kubespider.kubespider_downloader.download_file(source, path, file_type)

        if matchOneProvider == True and \
            matchProvider.get_provider_type() == types.SOURCE_PROVIDER_DISPOSABLE_TYPE:
            file_type = matchProvider.get_file_type()
            links = matchProvider.get_links(source)
            download_final_path = os.path.join(matchProvider.get_download_path(), path)
            for download_link in links:
                kubespider.kubespider_downloader.download_file(source, download_final_path, file_type)

        self.send_ok_response()
    
    def get_file_type(self, url):
        if url.endswith("torrent"):
            return 'torrent'
        return 'general'

    def send_ok_response(self):
        self.send_response(200)
        self.send_header("Content-type", "application/text")
        self.end_headers()
        self.wfile.write(bytes('ok', "utf-8")) 