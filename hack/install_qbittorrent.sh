# Ref: https://github.com/SuperNG6/Docker-qBittorrent-Enhanced-Edition
#!/usr/bin/env bash

set -e

# 1.Load env and echo logo
source hack/env.sh

echo "[INFO] Start to deploy qbittorrent..."

# 2.Check env
ret=`docker version`
if [[ $? != 0 ]]; then
    echo "[ERROR] Please install docker"
    exit 1
fi

# 3.Create necessary directory
mkdir -p ${KUBESPIDER_HOME}/kubespider/qbittorrent/

# 4.Set registry
source hack/util.sh
util::set_registry_for_image

# 5.Install qbittorrent
docker run -itd  \
    --name=qbittorrentee  \
    -e WEBUIPORT=8080  \
    -e PUID=$UID \
    -e PGID=$GID \
    -e TZ=Asia/Shanghai \
    --network=host \
    -v ${KUBESPIDER_HOME}/kubespider/qbittorrent/:/config  \
    -v ${KUBESPIDER_HOME}/kubespider/nas/:/downloads  \
    --restart unless-stopped  \
    superng6/qbittorrentee:latest

# 5.Notice
echo "[INFO] Deploy Qbittorrent Enhanced Edition success, enjoy your time..."
echo "[INFO] Qbittorrent web address is: http://<server_ip>:8080"