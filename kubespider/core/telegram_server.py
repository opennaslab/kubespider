import _thread
import logging
import time

import telepot
from telepot.loop import MessageLoop

import utils.helper
from api.values import Event
from core import source_manager, notification_server
from urllib.parse import urlparse

from utils import global_config


def download_handler(msg):
    # Read the configured username. If there is no configuration, start processing directly. If it is configured,
    # compare whether the current message's username is the same. If it's different, skip it directly.
    valid_username = global_config.get_telegram_username()
    if valid_username is not None:
        chat = msg.get('chat', None)
        username = chat.get('username', None)
        if valid_username != username:
            return

    to_handle_text = msg.get("text", None)
    urls = utils.helper.extract_urls(to_handle_text)
    original_urls = utils.helper.convert_short_urls(urls)

    if len(original_urls) > 0:
        for url in original_urls:
            parsed_url = urlparse(url)
            clean_url = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path
            source = clean_url
            path = ""
            logging.info('Get telegram trigger:%s', source)
            event = Event(source, path)
            err = source_manager.source_provider_manager.download_with_source_provider(event)

            if err is None:
                notification_server.kubespider_notification_server.send_message(
                    title="[telegram hook] start download", source=source, path=path
                )
            else:
                notification_server.kubespider_notification_server.send_message(
                    title="[telegram hook] download failed", source=source, path=path
                )


def telegram_server(bot_token):
    bot = telepot.Bot(bot_token)
    MessageLoop(bot, download_handler).run_as_thread()


def main():
    telegram_server("test")


if __name__ == "__main__":
    _thread.start_new_thread(main, ())

    while True:
        time.sleep(30)

