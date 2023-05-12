#!/bin/sh

kill 9 'ps -ef | grep "python" | grep -v grep | awk '{print $2}''
python3 ./kubespider/app.py