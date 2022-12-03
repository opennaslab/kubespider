import os
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import source_provider.provider as abstract_source_provider
import source_provider.mikanani_source_provider.provider as mikanani_source_provider
import source_provider.btbtt12_disposable_source_provider.provider as btbtt12_disposable_source_provider
import download_provider.provider as abstract_download_provider
import download_provider.motrix_download_provider.provider as motrix_source_provider
from core import webhook_server
from core import download_trigger
from core import period_server
import _thread
import time

source_providers = [
    mikanani_source_provider.MikananiSourceProvider(),
    btbtt12_disposable_source_provider.Btbtt12DisposableSourceProvider(),
]

download_providers = [
    motrix_source_provider.MotrixDownloadProvider()
]

enabled_source_provider = []
enabled_download_provider = []
kubespider_downloader = download_trigger.KubespiderDownloader(enabled_download_provider)

def run():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s-%(levelname)s: %(message)s')

    for provider in source_providers:
        provider_name = provider.get_provider_name()
        if provider.provider_enabled():
            logging.info(f'Source Provider:{provider_name} enabled...')
            enabled_source_provider.append(provider)
    
    for provider in download_providers:
        provider_name = provider.get_provider_name()
        if provider.provider_enabled():
            logging.info(f'Download Provider:{provider_name} enabled...')
            enabled_download_provider.append(provider)

    kubespider_downloader = download_trigger.KubespiderDownloader(enabled_download_provider)
    _thread.start_new_thread(run_period_job, ())
    _thread.start_new_thread(run_webhook_server, ())
    while True:
        time.sleep(30)

def run_webhook_server():
    webhook_server_port = os.getenv('WEBHOOK_SERVER_PORT')
    if webhook_server_port == None:
        webhook_server_port = 3080
    httpd = HTTPServer(('0.0.0.0', webhook_server_port), webhook_server.WebhookServer)
    logging.info(f'Webhook Server start running...')
    httpd.serve_forever()

def run_period_job():
    server = period_server.PeriodServer(enabled_source_provider, enabled_download_provider)
    logging.info('Period Server start running...')
    server.run()