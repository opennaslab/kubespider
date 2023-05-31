#!/bin/sh

set -e

# 1.Load env and echo logo
source hack/env.sh

echo "[INFO] Start to deploy yt-dlp downloader..."

# 2.Check env
ret=`docker version`
if [[ $? != 0 ]]; then
    echo "[ERROR] Please install docker"
    exit 1
fi

# 3.Create necessary directory
mkdir -p ${KUBESPIDER_HOME}/kubespider/nas/
mkdir -p ${KUBESPIDER_HOME}/kubespider/yt-dlp/

# 4.Set registry
source hack/util.sh
util::set_registry_for_image

# 5.Install yt-dlp 
docker run --name yt-dlp -d \
    --network=host \
    -v ${KUBESPIDER_HOME}/kubespider/yt-dlp:/root/config \
    -v ${KUBESPIDER_HOME}/kubespider/nas/:/root/downloads \
    --restart unless-stopped cesign/ytdlp-downloader:latest

# 6.Notice
echo "[INFO] Deploy yt-dlp success, enjoy your time..."
echo "[INFO] yt-dlp downloader trigger address is: http://<server_ip>:3082"
