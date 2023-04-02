import _thread
import logging
import time

from core import tasks
from core import webhook

logging.basicConfig(level=logging.INFO, format='%(asctime)s-%(levelname)s: %(message)s')

def you_get_main():
    _thread.start_new_thread(run_you_get_webhook, ())
    _thread.start_new_thread(run_you_get_tasks, ())
    while True:
        time.sleep(1)

def run_you_get_webhook():
    logging.info("you-get webhook is running...")
    webhook.you_get_server.run(host='0.0.0.0', port=3081)

def run_you_get_tasks():
    logging.info("you-get tasks is running...")
    tasks.you_get_tasks.run()

if __name__ == "__main__":
    you_get_main()
