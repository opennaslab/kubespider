import logging
import sys

from core import runner
from utils.global_config import cfg


def check_python_version():
    min_version = '3.10'
    version_info = str(sys.version_info[0]) + '.' + str(sys.version_info[1])
    if version_info < min_version:
        msg = f'Python version should be higher or equal to {min_version}.'
        raise Exception(msg)


def main():
    if cfg.log.level == 'DEBUG':
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s-%(levelname)s %(filename)s[line%(lineno)d]: %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s-%(levelname)s: %(message)s')
    runner.run()


if __name__ == "__main__":
    check_python_version()
    main()
