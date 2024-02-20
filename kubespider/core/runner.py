# -*- coding: utf-8 -*-

import _thread
import logging
import time

import waitress
from watchdog.observers import Observer

from api import values
from core import config_handler
from core import webhook_server
from core.kubespider_controller import kubespider_controller
from core.telegram_server import telegram_server
from utils import global_config


def run_webhook_server() -> None:
    webhook_server_port = global_config.get_server_port()
    logging.info('Webhook Server start running...')
    waitress.serve(webhook_server.kubespider_server, host='0.0.0.0', port=webhook_server_port)


def run_telegram_hook_server() -> None:
    bot_token = global_config.get_telegram_bot_token()
    if bot_token is not None:
        logging.info('Telegram Server start running...')
        telegram_server(bot_token)
        logging.info('Bot token set successfully, bot started running.')
    else:
        logging.warning('Failed to setup telegram bot token, telegram server not started')


def run() -> None:
    kubespider_controller.config()
    kubespider_controller.run()

    # webhook doesn't belong to kubespider_controller, so let's extract it here
    _thread.start_new_thread(run_webhook_server, ())

    _thread.start_new_thread(run_telegram_hook_server, ())

    while True:
        time.sleep(30)


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
