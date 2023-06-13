#!/bin/sh

set -e

# 1.Load env and echo logo
source hack/env.sh

echo "[INFO] Start to deploy transmission..."

# 2.Check env
ret=`docker version`
if [[ $? != 0 ]]; then
    echo "[ERROR] Please install docker"
    exit 1
fi

# 3.Create necessary directory
mkdir -p ${KUBESPIDER_HOME}/kubespider/transmission/

# 4.Set registry
source hack/util.sh
util::set_registry_for_image

# Some PT website only supports older version
DEFAULT_VERSION=${DEFAULT_VERSION:-2.94-r1-ls24}

# 5.Install transmission
docker run -d \
  --name=transmission \
  -e PUID=$UID \
  -e PGID=$GID \
  -e TZ=Asia/Shanghai \
  -e USER=admin \
  -e PASS=admin \
  -p 9091:9091 \
  -p 51413:51413 \
  -p 51413:51413/udp \
  -v ${KUBESPIDER_HOME}/kubespider/transmission/:/config \
  -v ${KUBESPIDER_HOME}/kubespider/nas/:/downloads \
  --restart unless-stopped \
  linuxserver/transmission:${DEFAULT_VERSION}

# 5.Notice
echo "[INFO] Deploy Transmission Enhanced Edition success, enjoy your time..."
echo "[INFO] Transmission web address is: http://<server_ip>:9091"