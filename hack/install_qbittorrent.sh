# Ref: https://github.com/SuperNG6/Docker-qBittorrent-Enhanced-Edition
#!/bin/sh

set -e

# 1.Echo logo
cat << "EOF"
 _          _                     _     _
| | ___   _| |__   ___  ___ _ __ (_) __| | ___ _ __
| |/ / | | | '_ \ / _ \/ __| '_ \| |/ _` |/ _ \ '__|
|   <| |_| | |_) |  __/\__ \ |_) | | (_| |  __/ |
|_|\_\\__,_|_.__/ \___||___/ .__/|_|\__,_|\___|_|
                           |_|  
EOF
echo "[INFO] Start to deploy qbittorrent..."

# 2.Check env
ret=`docker version`
if [[ $? != 0 ]]; then
    echo "[ERROR] Please install docker"
    exit 1
fi

# 3.Create necessary directory
mkdir -p ${HOME}/kubespider/qbittorrent/

# 4.Set registry
source hack/util.sh
util::set_registry_for_image

# 5.Install qbittorrent
docker run -itd  \
    --name=qbittorrentee  \
    -e WEBUIPORT=8080  \
    -e PUID=1026 \
    -e PGID=100 \
    -e TZ=Asia/Shanghai \
    -p 6881:6881  \
    -p 6881:6881/udp  \
    -p 8080:8080  \
    -v ${HOME}/kubespider/qbittorrent/config:/config  \
    -v ${HOME}/kubespider/qbittorrent/downloads:/downloads  \
    --restart unless-stopped  \
    superng6/qbittorrentee:latest

# 5.Notice
echo "[INFO] Deploy Qbittorrent Enhanced Edition success, enjoy your time..."
echo "[INFO] Qbittorrent web address is: http://<server_ip>:8080"