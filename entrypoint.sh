#!/bin/bash

groupmod -o -g ${PGID} kubespider
usermod -o -u ${PUID} kubespider

chown -R kubespider:kubespider /kubespider

umask ${UMASK}

exec su-exec kubespider:kubespider $@