import os
import logging
import json

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
        
        err = False
        if matchOneProvider == False:
            file_type = self.get_file_type(source)
            # If we not match the source provider, just download to common path
            path = os.path.join('common', path)
            err = kubespider.kubespider_downloader.download_file(source, path, file_type)

        if matchOneProvider == True and \
            matchProvider.get_provider_type() == types.SOURCE_PROVIDER_DISPOSABLE_TYPE:
            file_type = matchProvider.get_file_type()
            links = matchProvider.get_links(source)
            download_final_path = os.path.join(matchProvider.get_download_path(), path)
            for download_link in links:
                err = kubespider.kubespider_downloader.download_file(source, download_final_path, file_type)
                if err != None:
                    break

        if err == None:
            self.send_ok_response()
        else:
            self.send_bad_response(err)
    
    def get_file_type(self, url):
        if url.endswith("torrent"):
            return 'torrent'
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