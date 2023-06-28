#!/usr/bin/env bash

groupmod -o -g ${PGID} ytdlp
usermod -o -u ${PUID} ytdlp

chown -R ytdlp:ytdlp /app

umask ${UMASK}

exec su-exec ytdlp:ytdlp $@