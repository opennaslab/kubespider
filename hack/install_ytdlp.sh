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
echo "[INFO] Start to deploy yt-dlp downloader..."

# 2.Check env
ret=`docker version`
if [[ $? != 0 ]]; then
    echo "[ERROR] Please install docker"
    exit 1
fi

# 3.Create necessary directory
mkdir -p ${HOME}/kubespider/nas/
mkdir -p ${HOME}/kubespider/yt-dlp/

# 4.Set registry
source hack/util.sh
util::set_registry_for_image

# 5.Install yt-dlp 
docker run --name yt-dlp -d \
    --network=host \
    -e YOUTUBE_PROXY=${http_proxy} \
    -v ${HOME}/kubespider/yt-dlp:/root/config \
    -v ${HOME}/kubespider/nas/:/root/downloads \
    --restart unless-stopped cesign/ytdlp-downloader:latest

# 6.Notice
echo "[INFO] Deploy yt-dlp success, enjoy your time..."
echo "[INFO] yt-dlp downloader trigger address is: http://<server_ip>:3082"
