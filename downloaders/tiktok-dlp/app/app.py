import _thread
import logging
import time

from core import webhook
from core import tasks

logging.basicConfig(level=logging.INFO, format='%(asctime)s-%(levelname)s: %(message)s')


def tiktok_dlp_main():
    _thread.start_new_thread(run_tiktok_dlp_webhook, ())
    _thread.start_new_thread(run_tiktok_dlp_tasks, ())
    while True:
        time.sleep(1)


def run_tiktok_dlp_webhook():
    logging.info("tiktok-dlp webhook is running...")
    webhook.tiktok_dlp.run(host='0.0.0.0', port=3083)


def run_tiktok_dlp_tasks():
    logging.info("tiktok-dlp tasks is running...")
    tasks.tiktok_dlp_tasks.run()


if __name__ == "__main__":
    tiktok_dlp_main()
