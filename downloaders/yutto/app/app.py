import _thread
import logging
import time

from core import webhook
from core import tasks

logging.basicConfig(level=logging.INFO, format='%(asctime)s-%(levelname)s: %(message)s')

def yutto_main():
    _thread.start_new_thread(run_yutto_webhook, ())
    _thread.start_new_thread(run_yutto_tasks, ())
    while True:
        time.sleep(1)

def run_yutto_webhook():
    logging.info("yutto webhook is running...")
    webhook.yutto_server.run(host='0.0.0.0', port=3084)

def run_yutto_tasks():
    logging.info("yutto tasks is running...")
    tasks.yutto_tasks.run()

if __name__ == "__main__":
    yutto_main()
