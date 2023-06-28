#!/usr/bin/env bash

groupmod -o -g ${PGID} youget
usermod -o -u ${PUID} youget

chown -R youget:youget /app

umask ${UMASK}

exec su-exec youget:youget $@