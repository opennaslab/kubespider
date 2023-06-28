# Ref: https://github.com/v2fly/fhs-install-v2ray
#!/usr/bin/env bash

set -e

# 1.Load env and echo logo
source hack/env.sh

echo "[INFO] Start to install v2ray..."

# 1.Download necessary files
git clone https://github.com/v2fly/fhs-install-v2ray.git

wget https://github.com/v2fly/v2ray-core/releases/latest/download/v2ray-linux-64.zip
bash fhs-install-v2ray/install-dat-release.sh -l v2ray-linux-64.zip

# 2.Notice
echo "[INFO] Install v2ray successful..."
echo "[INFO] v2ray config path: /usr/local/etc/v2ray/config.json"
