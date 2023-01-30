# Ref: https://github.com/cnk3x/xunlei
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
echo "[INFO] Start to deploy thunder..."

# 2.Check env
ret=`docker version`
if [[ $? != 0 ]]; then
    echo "[ERROR] Please install docker"
    exit 1
fi

# 3.Create necessary directory
mkdir -p ${HOME}/kubespider/nas/
mkdir -p ${HOME}/kubespider/thunder/

# 4.Set registry
source hack/util.sh
util::set_registry_for_image

# 5.Install thunder 
docker run -d --name=thunder --hostname=thunder \
    --net=host \
    -v ${HOME}/kubespider/thunder:/xunlei/data \
    -v ${HOME}/kubespider/nas:/xunlei/downloads \
    --restart=unless-stopped --privileged \
    ${image_registry}/xunlei:latest

# 5.Notice
echo "[INFO] Deploy baidu thunder success, enjoy your time..."
echo "[INFO] Thunder web address is: http://<server_ip>:2345"