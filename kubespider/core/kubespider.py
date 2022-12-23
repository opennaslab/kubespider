import os
import logging
import _thread
import time
from http.server import HTTPServer

from core import kubespider_global
from core import webhook_server
from core import download_trigger
from core import period_server


def run():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s-%(levelname)s: %(message)s')

    for provider in kubespider_global.source_providers:
        provider_name = provider.get_provider_name()
        if provider.provider_enabled():
            logging.info('Source Provider:%s enabled...', provider_name)
            kubespider_global.enabled_source_provider.append(provider)

    for provider in kubespider_global.download_providers:
        provider_name = provider.get_provider_name()
        if provider.provider_enabled():
            logging.info('Download Provider:%s enabled...', provider_name)
            kubespider_global.enabled_download_provider.append(provider)

    download_trigger.kubespider_downloader = \
        download_trigger.KubespiderDownloader(kubespider_global.enabled_download_provider)
    period_server.kubespider_period_server = \
        period_server.PeriodServer(kubespider_global.enabled_source_provider, \
            kubespider_global.enabled_download_provider)

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
    period_server.kubespider_period_server.run()
