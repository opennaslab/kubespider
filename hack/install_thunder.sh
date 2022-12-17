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
mkdir -p /root/kubespider/thunder/

# 4.Install thunder 
docker run -d --name=thunder --hostname=thunder \
    --net=host \
    -v /root/kubespider/thunder:/xunlei/data \
    -v /root/kubespider/nas:/xunlei/downloads \
    --restart=unless-stopped --privileged \
    cesign/xunlei:latest

# 5. Notice
echo "[INFO] Deploy baidu thunder success, enjoy your time..."
echo "[INFO] Thunder web address is: http://<server_ip>:2345"