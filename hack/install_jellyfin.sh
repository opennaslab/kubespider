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
echo "[INFO] Start to deploy jellyfin ..."

# 2. Creat directory
mkdir -p ${HOME}/kubespider/jellyfin/

# 3. Install Jellyfin
docker run -d -p 8096:8096 \
    -v ${HOME}/kubespider/jellyfin/config:/config \
    -v ${HOME}/kubespider/nas/:/media \
    --name jellyfin \
    --restart unless-stopped jellyfin/jellyfin

# 4. Notice
echo "[INFO] Deploy Jellyfin success, enjoy your time..."
echo "[INFO] Jellyfin UI address is: http://<server_ip>:8096"
