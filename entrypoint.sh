#!/usr/bin/env bash

groupmod -o -g ${PGID} kubespider
usermod -o -u ${PUID} kubespider

chown -R kubespider:kubespider /app

umask ${UMASK}

exec su-exec kubespider:kubespider $@