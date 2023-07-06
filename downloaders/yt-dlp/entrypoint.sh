#!/usr/bin/env bash

groupmod -o -g ${PGID} ytdlp
usermod -o -u ${PUID} ytdlp

chown -R ytdlp:ytdlp /app

umask ${UMASK}

case "$1" in
  server)
    exec python3 /app/app/app.py
    ;;
  dev_server)
    exec watchmedo auto-restart --directory=./app/ --pattern=*.py --recursive -- python3 /app/app/app.py
    ;;
  *)
    exec "$@"
    ;;
esac

su-exec ytdlp:ytdlp $@