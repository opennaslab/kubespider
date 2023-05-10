import os
import logging
import _thread
import time

from core import kubespider_global
from core import webhook_server
from core import download_trigger
from core import period_server
from core import pt_server
import download_provider.provider as dp
from utils import helper
import waitress

def run():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s-%(levelname)s: %(message)s')

    for provider in kubespider_global.source_providers:
        provider_name = provider.get_provider_name()
        try:
            if provider.provider_enabled():
                logging.info('Source Provider:%s enabled...', provider_name)
                kubespider_global.enabled_source_provider.append(provider)
        except KeyError:
            logging.warning('Source Provider:%s not exists, treat as disabled', provider_name)

    for provider in kubespider_global.download_providers:
        provider_name = provider.get_provider_name()
        try:
            if provider.provider_enabled():
                logging.info('Download Provider:%s enabled...', provider_name)
                kubespider_global.enabled_download_provider.append(provider)
        except KeyError:
            logging.warning('Download Provider:%s not exists, treat as disabled', provider_name)
    kubespider_global.enabled_download_provider.sort(key=sort_download_provider)

    for provider in kubespider_global.pt_providers:
        provider_name = provider.get_provider_name()
        try:
            if provider.provider_enabled():
                logging.info('PT Provider:%s enabled...', provider_name)
                kubespider_global.enabled_pt_provider.append(provider)
        except KeyError:
            logging.warning('PT Provider:%s not exists, treat as disabled', provider_name)

    download_trigger.kubespider_downloader = \
        download_trigger.KubespiderDownloader(kubespider_global.enabled_download_provider)
    period_server.kubespider_period_server = \
        period_server.PeriodServer(kubespider_global.enabled_source_provider, \
            kubespider_global.enabled_download_provider)
    pt_server.kubespider_pt_server = \
        pt_server.PTServer(helper.global_config, kubespider_global.enabled_pt_provider)

    _thread.start_new_thread(run_period_job_producer, ())
    _thread.start_new_thread(run_period_job_consumer, ())
    _thread.start_new_thread(run_download_trigger_job, ())
    _thread.start_new_thread(run_webhook_server, ())
    _thread.start_new_thread(run_pt_server, ())

    while True:
        time.sleep(30)

def run_pt_server():
    logging.info('PT Server start running...')
    pt_server.kubespider_pt_server.run()

def run_webhook_server():
    webhook_server_port = os.getenv('WEBHOOK_SERVER_PORT')
    if webhook_server_port is None:
        webhook_server_port = 3080
    logging.info('Webhook Server start running...')
    waitress.serve(webhook_server.kubespider_server, host='0.0.0.0', port=webhook_server_port)

def run_period_job_consumer():
    logging.info('Period Server Quene handler start running...')
    period_server.kubespider_period_server.run_consumer()

def run_period_job_producer():
    logging.info("Period Server producer start running...")
    period_server.kubespider_period_server.run_producer()

def run_download_trigger_job():
    logging.info('Download trigger job start running...')
    download_trigger.kubespider_downloader.period_run()

def sort_download_provider(provider: dp.DownloadProvider):
    return provider.provide_priority()
