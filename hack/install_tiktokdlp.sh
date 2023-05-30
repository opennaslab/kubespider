# Ref: https://github.com/imgyh/tiktok
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
echo "[INFO] Start to deploy tiktok-dlp downloader..."

# 2.Check env
ret=`docker version`
if [[ $? != 0 ]]; then
    echo "[ERROR] Please install docker"
    exit 1
fi

# 3.Create necessary directory
mkdir -p ${HOME}/kubespider/nas/

# 4.Set registry
source hack/util.sh
util::set_registry_for_image

# 5.Install tiktok-dlp
docker run --name tiktok-dlp -d \
    --network=host \
    -v ${HOME}/kubespider/nas/:/root/downloads \
    --restart unless-stopped smilekung/tiktok-dlp:latest

# 6.Notice
echo "[INFO] Deploy tiktok-dlp success, enjoy your time..."
echo "[INFO] tiktok-dlp downloader trigger address is: http://<server_ip>:3083"
