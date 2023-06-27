#!/bin/bash

set -e

# 1.Load env and echo logo
source hack/env.sh

echo "[INFO] Start to deploy plex ..."

# 2. Check cliam code
claim=${PLEX_CLAIM}
if [[ $claim == "" ]];then
    echo "[ERROR] Please set your claim by env: PLEX_CLAIM"
    exit 1
fi

# 3. Creat directory
mkdir -p ${KUBESPIDER_HOME}/kubespider/plex/

# 4.Set registry
source hack/util.sh
util::set_registry_for_image

# 5. Install Plex
docker run -itd --name plex \
    -p 32400:32400 \
    -v ${KUBESPIDER_HOME}/kubespider/plex:/config \
    -v ${KUBESPIDER_HOME}/kubespider/nas:/nas \
    -e PUID=$UID \
    -e VERSION=docker \
    -e PLEX_CLAIM=${claim} \
    -e PGID=$GID \
    --restart unless-stopped \
    ${image_registry}/plex:latest

# 5. Notice
echo "[INFO] Deploy flex success, enjoy your time..."
echo "[INFO] Plex UI address is: http://<server_ip>:32400"