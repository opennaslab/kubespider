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
if [[ `whoami` != 'root' ]]; then
    echo "[ERROR] Please run as root"
    exit 1
fi

ret=`docker version`
if [[ $? != 0 ]]; then
    echo "[ERROR] Please install docker"
    exit 1
fi

# 3.Create necessary directory
mkdir -p /root/kubespider/nas/
mkdir -p /root/kubespider/baidunetdisk/

# 4.Install baidu net disk
docker create \
    --name=baidunetdisk \
    -p 5800:5800 \
    -p 5900:5900 \
    -v /root/kubespider/baidu:/config \
    -v /root/kubespider/nas:/config/baidunetdiskdownload \
    --restart unless-stopped \
    cesign/baidunetdisk:latest

# 5. Notice
echo "[INFO] Deploy baidu net disk success, enjoy your time..."
echo "[INFO] Biadu web address is: http://<server_ip>:5800"