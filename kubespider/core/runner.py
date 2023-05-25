# -*- coding: utf-8 -*-

import time
import logging
import _thread
from watchdog.observers import Observer
import waitress

from api import values
from core.kubespider_controller import kubespider_controller
from core import config_handler
from core import webhook_server
from utils import global_config


def run_webhook_server() -> None:
    webhook_server_port = global_config.get_server_port()
    logging.info('Webhook Server start running...')
    waitress.serve(webhook_server.kubespider_server, host='0.0.0.0', port=webhook_server_port)


def run() -> None:
    kubespider_controller.config()
    kubespider_controller.run()

    # webhook doesn't belong to kubespider_controller, so let's extract it here
    _thread.start_new_thread(run_webhook_server, ())

def run_with_config_handler():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s-%(levelname)s: %(message)s')
    config_handler.prepare_config()
    logging.info('File handler start running...')
    event_handler = config_handler.ConfigHandler(run)
    observer = Observer()
    observer.schedule(event_handler, values.CFG_BASE_PATH, recursive=True)
    observer.start()
    while True:
        time.sleep(10)
