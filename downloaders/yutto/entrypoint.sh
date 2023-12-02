#!/usr/bin/env bash

groupmod -o -g ${PGID} yutto
usermod -o -u ${PUID} yutto

chown -R yutto:yutto /app

umask ${UMASK}

exec su-exec yutto:yutto $@