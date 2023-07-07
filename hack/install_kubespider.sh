#!/usr/bin/env bash

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

# 5.Set os related args
kubespider_os_related_arg=""
if [[ "$(uname)" == "Darwin" ]]; then
    kubespider_os_related_arg="-p 3080:3080"
else
    kubespider_os_related_arg="--network=host"
fi

# 6.Deploy aria2
docker run -d \
    --name aria2-pro \
    --restart unless-stopped \
    --log-opt max-size=1m \
    -p 6800:6800 \
    -p 6888:6888 \
    -e PUID=$UID \
    -e PGID=$GID \
    -e RPC_SECRET=kubespider \
    -e RPC_PORT=6800 \
    -e LISTEN_PORT=6888 \
    -v ${KUBESPIDER_HOME}/kubespider/aria2/:/config \
    -v ${KUBESPIDER_HOME}/kubespider/nas/:/downloads/ \
    ${image_registry}/aria2-pro:latest

# 7.Deploy kubespider
export KUBESPIDER_DEFAULT_VERSION="latest"
if [[ ${KUBESPIDER_VERSION} == "" ]]; then
    export KUBESPIDER_VERSION=${KUBESPIDER_DEFAULT_VERSION}
fi
docker run -itd --name kubespider \
    -v ${KUBESPIDER_HOME}/kubespider/.config:/app/.config \
    -e PUID=$UID \
    -e PGID=$GID \
    $kubespider_os_related_arg \
    --restart unless-stopped \
    ${image_registry}/kubespider:${KUBESPIDER_VERSION}

# 8.Wait 5s for containers creating
sleep 5

# 9.Change download provider config IPAddress when OS is MacOS
if [[ "$(uname)" == "Darwin" ]]; then
    aria2_container_ip=$(docker inspect aria2-pro | grep IPAddress | sed -n '2p' | awk '{print substr($2, 2, length($2)-3)}')
    if [[ -z "$aria2_container_ip" ]]; then
        echo "[WARN] Can not find the aria2-pro container IPAddress. Please check your aria2 container IPAddress and modify your download_provider.yaml manually"
    else
        cd ${KUBESPIDER_HOME}/kubespider/.config
        line=$(awk '/aria2/{flag=1; next} flag && /rpc_endpoint_host/{print NR; exit}' download_provider.yaml)
        sed -i "" "${line}s#http.*#http://$aria2_container_ip#g" download_provider.yaml
    fi
fi

# 10.Give necessary info
echo "[INFO] Deploy successful, check the information:"
echo "*******************************************"
echo "Kubespider config path: ${KUBESPIDER_HOME}/kubespider/.config"
echo "Download file path: ${KUBESPIDER_HOME}/kubespider/nas/"
echo "Kubespider webhook address: http://<server_ip>:3080"
echo "Aria2 server address: http://<server_ip>:6800/jsonrpc, you can use any gui or webui to connect it"
echo "Aria2 default secret is:kubespider"
echo "*******************************************"
