#!/usr/bin/env bash

set -e

# 1.Load env and echo logo
source hack/env.sh

echo "[INFO] Start to deploy transmission for pt..."


function usage() {
    echo "This script is used to deploy transmission for pt..."
    echo "Usage:hack/install_transmission_pt.sh <PORT> <NAME>"
    echo "Example:hack/install_transmission_pt.sh 9092 mteam"
}

if [[ $# -ne 2 ]]; then
  usage
  exit 1
fi

# 2.Check env
ret=`docker version`
if [[ $? != 0 ]]; then
    echo "[ERROR] Please install docker"
    exit 1
fi

# 3.Create necessary directory
mkdir -p ${KUBESPIDER_HOME}/kubespider/transmission-${2}/
mkdir -p ${KUBESPIDER_HOME}/kubespider/nas/PT/${2}

# 4.Set registry
source hack/util.sh
util::set_registry_for_image

# Some PT website only supports older version
DEFAULT_VERSION=${DEFAULT_VERSION:-2.94-r1-ls24}

# 5.Install transmission
docker run -d \
  --name=transmission-${2} \
  -e PUID=$UID \
  -e PGID=$GID \
  -e TZ=Asia/Shanghai \
  -e USER=admin \
  -e PASS=admin \
  -p ${1}:9091 \
  -v ${KUBESPIDER_HOME}/kubespider/transmission-${2}/:/config \
  -v ${KUBESPIDER_HOME}/kubespider/nas/PT/${2}:/downloads \
  --restart unless-stopped \
  linuxserver/transmission:${DEFAULT_VERSION}

# 5.Notice
echo "[INFO] Deploy Transmission Enhanced Edition success, enjoy your time..."
echo "[INFO] Transmission web address is: http://<server_ip>:${1}"
