#!/usr/bin/env bash

groupmod -o -g ${PGID} ytdlp
usermod -o -u ${PUID} ytdlp

chown -R ytdlp:ytdlp /app

umask ${UMASK}

case "$1" in
  server)
    exec su-exec ytdlp:ytdlp python3 /app/app/app.py
    ;;
  dev_server)
    exec su-exec ytdlp:ytdlp watchmedo auto-restart --directory=./app/ --pattern=*.py --recursive -- python3 /app/app/app.py
    ;;
  *)
    exec su-exec ytdlp:ytdlp "$@"
    ;;
esac