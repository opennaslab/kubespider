#!/bin/sh

set -e

# 0.Set env
source hack/env.sh

# 1.Echo logo
cat << "EOF"
 _          _                     _     _
| | ___   _| |__   ___  ___ _ __ (_) __| | ___ _ __
| |/ / | | | '_ \ / _ \/ __| '_ \| |/ _` |/ _ \ '__|
|   <| |_| | |_) |  __/\__ \ |_) | | (_| |  __/ |
|_|\_\\__,_|_.__/ \___||___/ .__/|_|\__,_|\___|_|
                           |_|
EOF
echo "[INFO] Start to deploy transmission..."

# 2.Check env
ret=`docker version`
if [[ $? != 0 ]]; then
    echo "[ERROR] Please install docker"
    exit 1
fi

# 3.Create necessary directory
mkdir -p ${HOME}/kubespider/transmission/

# 4.Set registry
source hack/util.sh
util::set_registry_for_image

# Some PT website only supports older version
DEFAULT_VERSION=${DEFAULT_VERSION:-2.94-r1-ls24}

# 5.Install transmission
docker run -d \
  --name=transmission \
  -e PUID=1000 \
  -e PGID=1000 \
  -e TZ=Asia/Shanghai \
  -e USER=admin \
  -e PASS=admin \
  -p 9091:9091 \
  -p 51413:51413 \
  -p 51413:51413/udp \
  -v ${HOME}/kubespider/transmission/:/config \
  -v ${HOME}/kubespider/nas/:/downloads \
  --restart unless-stopped \
  linuxserver/transmission:${DEFAULT_VERSION}

# 5.Notice
echo "[INFO] Deploy Transmission Enhanced Edition success, enjoy your time..."
echo "[INFO] Transmission web address is: http://<server_ip>:9091"