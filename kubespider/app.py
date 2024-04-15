import sys
import os

from core import runner


def check_python_version():
    min_version = '3.10'
    version_info = str(sys.version_info[0]) + '.' + str(sys.version_info[1])
    if version_info < min_version:
        msg = f'Python version should be higher or equal to {min_version}.'
        raise Exception(msg)


def migrate():
    pass


def print_logo():
    print(r'''
 _          _                     _     _
| | ___   _| |__   ___  ___ _ __ (_) __| | ___ _ __
| |/ / | | | '_ \ / _ \/ __| '_ \| |/ _` |/ _ \ '__|
|   <| |_| | |_) |  __/\__ \ |_) | | (_| |  __/ |
|_|\_\\__,_|_.__/ \___||___/ .__/|_|\__,_|\___|_|
                           |_|                    
    ''')
    print('KubeSpider - A global resource download orchestration system')
    if os.getenv('GIT_COMMIT'):
        print('Build Tag: ' + os.getenv('GIT_COMMIT'))


def main():
    runner.run()


if __name__ == "__main__":
    check_python_version()
    print_logo()
    main()
