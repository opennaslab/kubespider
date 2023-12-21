#!/usr/bin/env bash

set -e

# 1.Load env and echo logo
source hack/env.sh

echo "[INFO] Start to deploy yutto downloader..."

# 2.Check env
ret=`docker version`
if [[ $? != 0 ]]; then
    echo "[ERROR] Please install docker"
    exit 1
fi

if [[ ${BILIBILI_SESSDATA} == "" ]]; then
    echo "[ERROR] Please set BILIBILI_SESSDATA env"
    exit 1
fi

# 3.Create necessary directory
mkdir -p ${KUBESPIDER_HOME}/kubespider/nas/
mkdir -p ${KUBESPIDER_HOME}/kubespider/yutto/

# 4.Set registry
source hack/util.sh
util::set_registry_for_image

# 5.Install yutto
docker run -d \
    --name yutto \
    --network=host \
    -e PUID=$UID \
    -e PGID=$GID \
    -e BILIBILI_SESSDATA=${BILIBILI_SESSDATA} \
    -v ${KUBESPIDER_HOME}/kubespider/yutto:/app/config \
    -v ${KUBESPIDER_HOME}/kubespider/nas/:/app/downloads \
    --restart unless-stopped \
    cesign/yutto-downloader:latest

# 6.Notice
echo "[INFO] Deploy yutto success, enjoy your time..."
echo "[INFO] yutto downloader trigger address is: http://<server_ip>:3084"
