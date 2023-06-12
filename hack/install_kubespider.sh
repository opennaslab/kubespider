#!/bin/sh

set -e

# 1.Load env and echo logo
source hack/env.sh

echo "[INFO] Start to deploy with default configuration..."

# 2.Check env
ret=`docker version`
if [[ $? != 0 ]]; then
    echo "[ERROR] Please install docker"
    exit 1
fi

# 3.Create necessary directory
mkdir -p ${KUBESPIDER_HOME}/kubespider/nas/
mkdir -p ${KUBESPIDER_HOME}/kubespider/aria2/

# 4.Set registry
source hack/util.sh
util::set_registry_for_image

# 5.Deploy aria2
docker run -d \
    --name aria2-pro \
    --restart unless-stopped \
    --log-opt max-size=1m \
    --network host \
    -e PUID=$UID \
    -e PGID=$GID \
    -e RPC_SECRET=kubespider \
    -e RPC_PORT=6800 \
    -e LISTEN_PORT=6888 \
    -v ${KUBESPIDER_HOME}/kubespider/aria2/:/config \
    -v ${KUBESPIDER_HOME}/kubespider/nas/:/downloads/ \
    ${image_registry}/aria2-pro:latest

# 6.Deploy kubespider
export KUBESPIDER_DEFAULT_VERSION="latest"
if [[ ${KUBESPIDER_VERSION} == "" ]]; then
    export KUBESPIDER_VERSION=${KUBESPIDER_DEFAULT_VERSION}
fi
docker run -itd --name kubespider \
    -v ${KUBESPIDER_HOME}/kubespider/.config:/app/.config \
    -e PUID=$UID \
    -e PGID=$GID \
    --network=host \
    --restart unless-stopped \
    ${image_registry}/kubespider:${KUBESPIDER_VERSION}

# 7.Give necessary info
echo "[INFO] Deploy successful, check the information:"
echo "*******************************************"
echo "Kubespider config path: ${KUBESPIDER_HOME}/kubespider/.config"
echo "Download file path: ${KUBESPIDER_HOME}/kubespider/nas/"
echo "Kubespider webhook address: http://<server_ip>:3080"
echo "Aria2 server address: http://<server_ip>:6800/jsonrpc, you can use any gui or webui to connect it"
echo "Aria2 default secret is:kubespider"
echo "*******************************************"