#!/usr/bin/env bash

set -e

# 1.Load env and echo logo
source hack/env.sh

echo "[INFO] Start to install rsshub..."

ret=`docker version`
if [[ $? != 0 ]]; then
    echo "[ERROR] Please install docker"
    exit 1
fi

source hack/util.sh
util::set_registry_for_image

docker run -itd --name rsshub \
    -p 1200:1200 \
    --restart unless-stopped \
    diygod/rsshub:latest

# 5. Notice
echo "[INFO] Deploy rsshub success, enjoy your time..."
echo "[INFO] RSSHUB UI address is: http://<server_ip>:1200"