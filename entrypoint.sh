#!/usr/bin/env bash

groupmod -o -g ${PGID} kubespider
usermod -o -u ${PUID} kubespider

chown -R kubespider:kubespider /app

umask ${UMASK}


case "$1" in
    server)
        exec python3 /app/kubespider/app.py
    ;;
    dev_server)
        exec watchmedo auto-restart --directory=./kubespider --pattern=*.py --recursive -- python3 /app/kubespider/app.py
    ;;
    *)
        exec "$@"
    ;;
esac

su-exec kubespider:kubespider $@