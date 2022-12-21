import os
import logging
import _thread
import time
from http.server import HTTPServer

import source_provider.mikanani_source_provider.provider as mikanani_source_provider
import source_provider.btbtt12_disposable_source_provider.provider as btbtt12_disposable_source_provider
import source_provider.meijutt_source_provider.provider as meijutt_source_provider
import download_provider.aria2_download_provider.provider as aria2_download_provider
from core import webhook_server
from core import download_trigger
from core import period_server


source_providers = [
    mikanani_source_provider.MikananiSourceProvider(),
    btbtt12_disposable_source_provider.Btbtt12DisposableSourceProvider(),
    meijutt_source_provider.MeijuttSourceProvider(),
]

download_providers = [
    aria2_download_provider.Aria2DownloadProvider()
]

enabled_source_provider = []
enabled_download_provider = []
kubespider_downloader = download_trigger.KubespiderDownloader(enabled_download_provider)
kubespider_period_server = period_server.PeriodServer(enabled_source_provider, enabled_download_provider)


def run():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s-%(levelname)s: %(message)s')

    for provider in source_providers:
        provider_name = provider.get_provider_name()
        if provider.provider_enabled():
            logging.info('Source Provider:%s enabled...', provider_name)
            enabled_source_provider.append(provider)

    for provider in download_providers:
        provider_name = provider.get_provider_name()
        if provider.provider_enabled():
            logging.info('Download Provider:%s enabled...', provider_name)
            enabled_download_provider.append(provider)

    kubespider_downloader = \
        download_trigger.KubespiderDownloader(enabled_download_provider)
    kubespider_period_server = \
        period_server.PeriodServer(enabled_source_provider, enabled_download_provider)

    _thread.start_new_thread(run_period_job, ())
    _thread.start_new_thread(run_webhook_server, ())
    while True:
        time.sleep(30)


def run_webhook_server():
    webhook_server_port = os.getenv('WEBHOOK_SERVER_PORT')
    if webhook_server_port is None:
        webhook_server_port = 3080
    httpd = HTTPServer(('0.0.0.0', webhook_server_port), webhook_server.WebhookServer)
    logging.info('Webhook Server start running...')
    httpd.serve_forever()


def run_period_job():
    logging.info('Period Server start running...')
    kubespider_period_server.run()
