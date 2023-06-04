#!/bin/sh

set -e

# 1.Load env and echo logo
source hack/env.sh

echo "[INFO] Start to deploy you-get downloader..."

# 2.Check env
ret=`docker version`
if [[ $? != 0 ]]; then
    echo "[ERROR] Please install docker"
    exit 1
fi

# 3.Create necessary directory
mkdir -p ${KUBESPIDER_HOME}/kubespider/nas/
mkdir -p ${KUBESPIDER_HOME}/kubespider/youget/

# 4.Set registry
source hack/util.sh
util::set_registry_for_image

# 5.Install youget 
docker run --name youget -d \
    --network=host \
    -e PUID=$UID \
    -e PGID=$GID \
    -e BILIBILI_COOKIE_PATH=/app/config/bilibili_cookie.txt \
    -v ${KUBESPIDER_HOME}/kubespider/youget:/app/config \
    -v ${KUBESPIDER_HOME}/kubespider/nas/:/app/downloads \
    --restart unless-stopped cesign/youget-downloader:latest

# 6.Notice
echo "[INFO] Deploy you-get success, now prepare you cookie, enjoy your time..."
echo "[INFO] you-get downloader trigger address is: http://<server_ip>:3081"
