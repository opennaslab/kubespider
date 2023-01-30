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
echo "[INFO] Start to deploy baidu net disk..."

# 2.Check env
ret=`docker version`
if [[ $? != 0 ]]; then
    echo "[ERROR] Please install docker"
    exit 1
fi

# 3.Create necessary directory
mkdir -p ${HOME}/kubespider/nas/
mkdir -p ${HOME}/kubespider/baidunetdisk/

# 4.Set registry
source hack/util.sh
util::set_registry_for_image

# 5.Install baidu net disk
docker run -itd --name=baidunetdisk \
    -p 5800:5800 \
    -p 5900:5900 \
    -v ${HOME}/kubespider/baidu:/config \
    -v ${HOME}/kubespider/nas:/config/baidunetdiskdownload \
    --restart unless-stopped \
    ${image_registry}/baidunetdisk:latest

# 4. Notice
echo "[INFO] Deploy baidu net disk success, enjoy your time..."
echo "[INFO] Biadu web address is: http://<server_ip>:5800"