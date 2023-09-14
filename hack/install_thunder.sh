# Ref: https://github.com/cnk3x/xunlei
#!/usr/bin/env bash

set -e

# 1.Load env and echo logo
source hack/env.sh

echo "[INFO] Start to deploy thunder..."

# 2.Check env
ret=`docker version`
if [[ $? != 0 ]]; then
    echo "[ERROR] Please install docker"
    exit 1
fi

# 3.Create necessary directory
mkdir -p ${KUBESPIDER_HOME}/kubespider/nas/
mkdir -p ${KUBESPIDER_HOME}/kubespider/thunder/

# 4.Set registry
source hack/util.sh
util::set_registry_for_image

# 5.Install thunder 
docker run -d --name=thunder --hostname=thunder \
    --net=host \
    -v ${KUBESPIDER_HOME}/kubespider/thunder:/xunlei/data \
    -v ${KUBESPIDER_HOME}/kubespider/nas:/xunlei/downloads \
    --restart=unless-stopped --privileged \
    ${image_registry}/xunlei:latest

# 6.Notice
echo "[INFO] Deploy thunder success, enjoy your time..."
echo "[INFO] Thunder web address is: http://<server_ip>:2345"
