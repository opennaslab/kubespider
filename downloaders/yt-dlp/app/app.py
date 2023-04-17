import _thread
import logging
import time

from .core import tasks
from .core import webhook

logging.basicConfig(level=logging.INFO, format='%(asctime)s-%(levelname)s: %(message)s')

def ytdlp_main():
    _thread.start_new_thread(run_ytdlp_webhook, ())
    _thread.start_new_thread(run_ytdlp_tasks, ())
    while True:
        time.sleep(1)

def run_ytdlp_webhook():
    logging.info("yt-dlp webhook is running...")
    webhook.ytdlp_server.run(host='0.0.0.0', port=3082)

def run_ytdlp_tasks():
    logging.info("yt-dlp tasks is running...")
    tasks.yt_dlp_tasks.run()

if __name__ == "__main__":
    ytdlp_main()
