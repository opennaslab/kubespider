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
echo "[INFO] Start to deploy plex ..."

# 2. Check cliam code
claim=${PLEX_CLAIM}
if [[ $claim == "" ]];then
    echo "[ERROR] Please set your claim by env: PLEX_CLAIM"
    exit 1
fi

# 3. Creat directory
mkdir -p /root/netdisk/plex

# 4. Install Plex
docker run -itd --name plex \
    -p 32400:32400 \
    -v /root/netdisk/plex:/config \
    -v /root/nas:/nas \
    -e PUID=1000 \
    -e VERSION=docker \
    -e PLEX_CLAIM=${claim} \
    -e PGID=1000 \
    --restart unless-stopped \
    linuxserver/plex:latest

# 5. Notice
echo "[INFO] Deploy flex success, enjoy your time..."
echo "[INFO] Plex UI address is: http://<your_server_ip>:32400"