# Ref: https://github.com/imgyh/tiktok
#!/bin/bash

set -e

# 1.Load env and echo logo
source hack/env.sh

echo "[INFO] Start to deploy tiktok-dlp downloader..."

# 2.Check env
ret=`docker version`
if [[ $? != 0 ]]; then
    echo "[ERROR] Please install docker"
    exit 1
fi

# 3.Create necessary directory
mkdir -p ${KUBESPIDER_HOME}/kubespider/nas/

# 4.Set registry
source hack/util.sh
util::set_registry_for_image

# 5.Install tiktok-dlp
docker run --name tiktok-dlp -d \
    --network=host \
    -e PUID=$UID \
    -e PGID=$GID \
    -v ${KUBESPIDER_HOME}/kubespider/nas/:/app/downloads \
    --restart unless-stopped \
    cesign/tiktok-dlp:latest

# 6.Notice
echo "[INFO] Deploy tiktok-dlp success, enjoy your time..."
echo "[INFO] tiktok-dlp downloader trigger address is: http://<server_ip>:3083"
