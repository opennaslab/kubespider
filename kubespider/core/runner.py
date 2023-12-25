# -*- coding: utf-8 -*-

import logging
import waitress

from core.api import create_app
from utils.global_config import Config, initdirs


def run() -> None:
    logging.info('Webhook Server start running...')
    initdirs()
    waitress.serve(create_app(), host='0.0.0.0', port=Config.SERVER_PORT)
