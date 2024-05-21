# -*- coding: utf-8 -*-

import _thread
import logging
import time
import waitress
from api import create_app
from core.kubespider_controller import kubespider_controller
from core.telegram_server import telegram_server
from utils import global_config


def run_webhook_server() -> None:
    webhook_server_port = global_config.get_server_port()
    logging.info('Webhook Server start running...')
    waitress.serve(create_app(), host='0.0.0.0', port=webhook_server_port)


def run_telegram_hook_server() -> None:
    bot_token = global_config.get_telegram_bot_token()
    if bot_token is not None:
        logging.info('Telegram Server start running...')
        telegram_server(bot_token)
        logging.info('Bot token set successfully, bot started running.')
    else:
        logging.warning('Failed to setup telegram bot token, telegram server not started')


def run() -> None:
    kubespider_controller.run()

    # webhook doesn't belong to kubespider_controller, so let's extract it here
    _thread.start_new_thread(run_webhook_server, ())

    _thread.start_new_thread(run_telegram_hook_server, ())

    while True:
        time.sleep(30)


logging.basicConfig(level=logging.INFO, format='%(asctime)s-%(levelname)s: %(message)s')
