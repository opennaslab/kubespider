# -*- coding: utf-8 -*-

import logging
import waitress

from core.api import create_app
from core import config_handler
from utils.global_config import Config


def run() -> None:
    logging.info('Webhook Server start running...')
    waitress.serve(create_app(), host='0.0.0.0', port=Config.SERVER_PORT)


def run_with_config_handler():
    config_handler.prepare_config()
    logging.info('Config Prepare finish...')
    run()
