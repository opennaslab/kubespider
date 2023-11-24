import logging
import sys

from core import runner


def check_python_version():
    min_version = '3.10'
    version_info = str(sys.version_info[0]) + '.' + str(sys.version_info[1])
    if version_info < min_version:
        msg = f'Python version should be higher or equal to {min_version}.'
        raise Exception(msg)


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s-%(levelname)s: %(message)s')
    runner.run_with_config_handler()


if __name__ == "__main__":
    check_python_version()
    main()
