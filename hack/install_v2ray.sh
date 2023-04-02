# Ref: https://github.com/v2fly/fhs-install-v2ray
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
echo "[INFO] Start to install v2ray..."

# 1.Download necessary files
git clone https://github.com/v2fly/fhs-install-v2ray.git

wget https://github.com/v2fly/v2ray-core/releases/latest/download/v2ray-linux-64.zip
bash fhs-install-v2ray/install-dat-release.sh -l v2ray-linux-64.zip

# 2.Notice
echo "[INFO] Install v2ray successful..."
echo "[INFO] v2ray config path: /usr/local/etc/v2ray/config.json"
