# Ref: https://github.com/cnk3x/xunlei
#!/bin/sh

set -e

# 0.Set env
source hack/env.sh

# 1.Echo logo
cat << "EOF"
 _          _                     _     _
| | ___   _| |__   ___  ___ _ __ (_) __| | ___ _ __
| |/ / | | | '_ \ / _ \/ __| '_ \| |/ _` |/ _ \ '__|
|   <| |_| | |_) |  __/\__ \ |_) | | (_| |  __/ |
|_|\_\\__,_|_.__/ \___||___/ .__/|_|\__,_|\___|_|
                           |_|  
EOF
echo "[INFO] Start to deploy you-get downloader..."

# 2.Check env
ret=`docker version`
if [[ $? != 0 ]]; then
    echo "[ERROR] Please install docker"
    exit 1
fi

# 3.Create necessary directory
mkdir -p ${HOME}/kubespider/nas/
mkdir -p ${HOME}/kubespider/youget/

# 4.Set registry
source hack/util.sh
util::set_registry_for_image

# 5.Install youget 
docker run --name youget -d \
    --network=host \
    -e BILIBILI_COOKIE_PATH=/root/config/bilibili_cookie.txt \
    -v ${HOME}/kubespider/youget:/root/config \
    -v ${HOME}/kubespider/nas/:/root/downloads \
    --restart unless-stopped cesign/youget-downloader:latest

# 6.Notice
echo "[INFO] Deploy you-get success, now prepare you cookie, enjoy your time..."
echo "[INFO] you-get downloader trigger address is: http://<server_ip>:3081"
