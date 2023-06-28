#!/usr/bin/env bash

groupmod -o -g ${PGID} tiktokdlp
usermod -o -u ${PUID} tiktokdlp

chown -R tiktokdlp:tiktokdlp /app

umask ${UMASK}

exec su-exec tiktokdlp:tiktokdlp $@