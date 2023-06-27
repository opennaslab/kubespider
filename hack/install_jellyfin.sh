#!/bin/bash

set -e

# 1.Load env and echo logo
source hack/env.sh

echo "[INFO] Start to deploy jellyfin ..."

# 2. Creat directory
mkdir -p ${KUBESPIDER_HOME}/kubespider/jellyfin/

# 3. Install Jellyfin
docker run -d -p 8096:8096 \
    -v ${KUBESPIDER_HOME}/kubespider/jellyfin/config:/config \
    -v ${KUBESPIDER_HOME}/kubespider/nas/:/media \
    --name jellyfin \
    --restart unless-stopped jellyfin/jellyfin

# 4. Notice
echo "[INFO] Deploy Jellyfin success, enjoy your time..."
echo "[INFO] Jellyfin UI address is: http://<server_ip>:8096"
