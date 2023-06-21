#!/usr/bin/env bash
#
#  _          _                     _     _
# | | ___   _| |__   ___  ___ _ __ (_) __| | ___ _ __
# | |/ / | | | '_ \ / _ \/ __| '_ \| |/ _` |/ _ \ '__|
# |   <| |_| | |_) |  __/\__ \ |_) | | (_| |  __/ |
# |_|\_\\__,_|_.__/ \___||___/ .__/|_|\__,_|\___|_|
#                            |_|  
#
# Copyright (c) 2023 opennaslab/kubespider
#
# This is free software, licensed under the Apache License 2.0 License.
#
#
# The functions that the script can call are 'INFO' 'WARN' 'ERROR' 'if_port' 'get_uid_gid' 
#                                            'get_umask' 'get_tz' 'get_port' 'get_volume' 
#                                            'get_env' 'docker_source_choose'.
# INFO function use(log output): INFO "xxxx"
# WARN function use(log output): WARN "xxxx"
# ERROR function use(log output): ERROR "xxxx"
# if_port function use: if_port 80
#                       80 can customize any port.
#                       Changes the value of the 'TEST_IF_PORT' environment variable after calling.
#                       'TEST_IF_PORT=1' port not occupied.
#                       'TEST_IF_PORT=0' port occupied.


Green="\033[32m"
Red="\033[31m"
Yellow='\033[33m'
Font="\033[0m"
INFO="[${Green}INFO${Font}]"
ERROR="[${Red}ERROR${Font}]"
WARN="[${Yellow}WARN${Font}]"
function INFO {
echo -e "${INFO} ${1}"
}
function ERROR {
echo -e "${ERROR} ${1}"
}
function WARN {
echo -e "${WARN} ${1}"
}

function if_docker_install {
    if command -v docker >/dev/null 2>&1; then
        INFO "Docker is installed."
        INFO "Docker version: $(docker -v)"
    else
        ERROR "Docker is not installed."
        exit 1
    fi
}

function if_port {
    if nc -z localhost "$1" >/dev/null; then
        TEST_IF_PORT=0
    else
        TEST_IF_PORT=1
    fi
}

function get_uid_gid {

    DEFAULT_UID=${UID:-1000}
    DEFAULT_GID=${GID:-1000}

    INFO "Please enter a user ID (default ${DEFAULT_UID})"
    read -ep "PUID:" SET_UID
    [[ -z "${SET_UID}" ]] && SET_UID=${DEFAULT_UID}

    INFO "Please enter a group ID (default ${DEFAULT_GID})"
    read -ep "PUID:" SET_GID
    [[ -z "${SET_GID}" ]] && SET_GID=${DEFAULT_GID}

}

function get_umask {

    DEFAULT_UMASK=$(umask)

    INFO "Please enter a umask (default ${DEFAULT_UMASK})"
    read -ep "Umask:" SET_UMASK
    [[ -z "${SET_UMASK}" ]] && SET_UMASK=${DEFAULT_UMASK}

}

function get_tz {

    INFO "Please enter your time zone (default UTC)"
    read -ep "TZ:" SET_TZ
    [[ -z "${SET_TZ}" ]] && SET_TZ=UTC

}

function get_port {

    DEFAULT_PORT=$1
    OUTPUT=$2
    INFO "${OUTPUT} (default ${DEFAULT_PORT})"
    read -ep "PORT:" SET_PORT
    [[ -z "${SET_PORT}" ]] && SET_PORT=${DEFAULT_PORT}
    if_port "${SET_PORT}"
    if [[ ${TEST_IF_PORT} = '0' ]]; then
        WARN "${SET_PORT} port is occupied, please re-enter an unoccupied port"
        get_port "$1" "$2"
    fi

}

function get_volume {

    DEFAULT_VOLUME=$1
    OUTPUT=$2
    INFO "${OUTPUT} (default ${DEFAULT_VOLUME})"
    read -ep "DIR:" SET_VOLUME
    [[ -z "${SET_VOLUME}" ]] && SET_VOLUME=${DEFAULT_VOLUME}

}

function get_env {

    DEFAULT_ENV_VALUE=$1
    ENV_NAME=$2
    OUTPUT=$3
    INFO "${OUTPUT} (default ${DEFAULT_ENV_VALUE})"
    read -ep "${ENV_NAME}:" SET_ENV
    [[ -z "${SET_ENV}" ]] && SET_ENV=${DEFAULT_ENV_VALUE}

}

function docker_source_choose {

    INFO "Whether to use Alibaba Cloud source to pull the image (default n) [y/N]"
    read -ep "Enter your choice:" YN
    [[ -z "${YN}" ]] && YN="n"
    if [[ ${YN} == [Nn] ]]; then
        IMAGE_SOURCE=index.docker.io/cesign
    elif [[ ${YN} == [Yy] ]]; then
        IMAGE_SOURCE=registry.cn-hangzhou.aliyuncs.com/jwcesign
    fi

}

function echo_logo {
cat << "EOF"
———————————————————————————————————————————————————————————————————————
 _          _                     _     _
| | ___   _| |__   ___  ___ _ __ (_) __| | ___ _ __
| |/ / | | | '_ \ / _ \/ __| '_ \| |/ _` |/ _ \ '__|
|   <| |_| | |_) |  __/\__ \ |_) | | (_| |  __/ |
|_|\_\\__,_|_.__/ \___||___/ .__/|_|\__,_|\___|_|
                           |_|  

Copyright (c) 2023 opennaslab/kubespider

This is free software, licensed under the Apache License 2.0 License.

———————————————————————————————————————————————————————————————————————
EOF
}

function kubespider_install {

    get_volume "${HOME}/kubespider/.config" "Please enter your kubespider config file save path"
    kubespider_dir=${SET_VOLUME}

    get_port "3080" "Please enter your kubespider port"
    kubespider_port=${SET_PORT}

    get_uid_gid
    get_umask
    get_tz

    docker_source_choose

    clear
    INFO "Start deploying kubespider"
    docker run -itd --name kubespider \
        -v ${kubespider_dir}:/app/.config \
        -e PUID=${SET_UID} \
        -e PGID=${SET_GID} \
        -e UMASK=${SET_UMASK} \
        -e TZ=${SET_TZ} \
        -p ${kubespider_port}:3080 \
        --restart unless-stopped \
        ${IMAGE_SOURCE}/kubespider:latest
    if [ $? -eq 0 ]; then
        INFO "Kubespider installed successfully"
    else
        ERROR "Kubespider installation failed"
        exit 1
    fi

}

function aria2_install {

    get_volume "${HOME}/kubespider/aria2" "Please enter your aria2 config file save path"
    aria2_config_dir=${SET_VOLUME}
    get_volume "${HOME}/kubespider/nas" "Please enter your download path"
    download_dir=${SET_VOLUME}

    get_port "6800" "Please enter your aria2 rpc port"
    aria2_rpc_port=${SET_PORT}
    get_port "6888" "Please enter your aria2 listen port"
    aria2_listen_port=${SET_PORT}

    get_env "password" "RPC_SECRET" "Please enter your aria2 rpc secret"
    aria2_rpc_secret=${SET_ENV}

    get_uid_gid
    get_umask
    get_tz

    docker_source_choose

    clear
    INFO "Start deploying aria2"
    docker run -d \
        --name aria2-pro \
        --restart unless-stopped \
        --log-opt max-size=1m \
        --network host \
        -e PUID=${SET_UID} \
        -e PGID=${SET_GID} \
        -e SET_UMASK=${SET_UMASK} \
        -e TZ=${SET_TZ} \
        -e RPC_SECRET=${aria2_rpc_secret} \
        -e RPC_PORT=${aria2_rpc_port} \
        -e LISTEN_PORT=${aria2_listen_port} \
        -v ${aria2_config_dir}:/config \
        -v ${download_dir}:/downloads \
        ${IMAGE_SOURCE}/aria2-pro:latest
    if [ $? -eq 0 ]; then
        INFO "Aria2 installed successfully"
    else
        ERROR "Aria2 installation failed"
        exit 1
    fi

}

function transmission_install {

TODO

}

function qbittorrent_install {

TODO

}

function youget_install {

    get_volume "${HOME}/kubespider/youget" "Please enter your youget config file save path"
    youget_config_dir=${SET_VOLUME}
    get_volume "${HOME}/kubespider/nas" "Please enter your download path"
    download_dir=${SET_VOLUME}

    get_port "3081" "Please enter your youget port"
    youget_port=${SET_PORT}

    get_uid_gid
    get_umask
    get_tz

    docker_source_choose

    clear

    docker run -d \
        --name youget \
        -p ${youget_port}:3081 \
        -e PUID=${SET_UID} \
        -e PGID=${SET_GID} \
        -e UMASK=${SET_UMASK} \
        -e BILIBILI_COOKIE_PATH=/app/config/bilibili_cookie.txt \
        -v ${youget_config_dir}:/app/config \
        -v ${download_dir}:/app/downloads \
        --restart unless-stopped \
        cesign/youget-downloader:latest
    if [ $? -eq 0 ]; then
        INFO "youget installed successfully"
    else
        ERROR "youget installation failed"
        exit 1
    fi

}

function ytdlp_install {

    get_volume "${HOME}/kubespider/yt-dlp" "Please enter your yt-dlp config file save path"
    ytdlp_config_dir=${SET_VOLUME}
    get_volume "${HOME}/kubespider/nas" "Please enter your download path"
    download_dir=${SET_VOLUME}

    get_port "3082" "Please enter your yt-dlp port"
    ytdlp_port=${SET_PORT}

    get_uid_gid
    get_umask
    get_tz

    docker_source_choose

    clear

    docker run -d \
        --name yt-dlp \
        -p ${ytdlp_port}:3082 \
        -e PUID=${SET_UID} \
        -e PGID=${SET_GID} \
        -e UMASK=${SET_UMASK} \
        -e TZ=${SET_TZ} \
        -v ${ytdlp_config_dir}:/app/config \
        -v ${download_dir}:/app/downloads \
        --restart unless-stopped \
        cesign/ytdlp-downloader:latest
    if [ $? -eq 0 ]; then
        INFO "yt-dlp installed successfully"
    else
        ERROR "yt-dlp installation failed"
        exit 1
    fi

}

function tiktokdlp_install {

    get_volume "${HOME}/kubespider/tiktokdlp" "Please enter your tiktokdlp config file save path"
    tiktokdlp_config_dir=${SET_VOLUME}
    get_volume "${HOME}/kubespider/nas" "Please enter your download path"
    download_dir=${SET_VOLUME}

    get_port "3083" "Please enter your tiktokdlp port"
    tiktokdlp_port=${SET_PORT}

    get_uid_gid
    get_umask
    get_tz

    docker_source_choose

    clear

    docker run -d \
        --name tiktok-dlp \
        -p ${tiktokdlp_port}:3083 \
        -e PUID=${SET_UID} \
        -e PGID=${SET_GID} \
        -e UMASK=${SET_UMASK} \
        -e TZ=${SET_TZ} \
        -v ${tiktokdlp_config_dir}:/app/config \
        -v ${download_dir}:/app/downloads \
        --restart unless-stopped \
        cesign/tiktok-dlp:latest
    if [ $? -eq 0 ]; then
        INFO "tiktok-dlp installed successfully"
    else
        ERROR "tiktok-dlp installation failed"
        exit 1
    fi

}

function baidunetdisk_install {

TODO

}

function xunlei_install {

TODO

}

function jellyfin_install {

TODO

}

function emby_install {

TODO

}

function plex_install {

TODO

}

function downloader_main {

    echo -e "———————————————————————————————————————————————————————————————————————"
    echo -e "1. Aria2 installation"
    echo -e "2. Transmission installation"
    echo -e "3. qBittorrent installation"
    echo -e "4. you-get installation"
    echo -e "5. ytdlp installation"
    echo -e "6. baidunetdisk installation"
    echo -e "7. xunlei installation"
    echo -e "8. tiktok-dlp installation"
    echo -e "9. Back to previous menu"
    echo -e "———————————————————————————————————————————————————————————————————————"
    read -ep "Please enter the number [1-9]:" num
    case "$num" in
        1)
        clear
        aria2_install
        ;;
        2)
        clear
        transmission_install
        ;;
        3)
        clear
        qbittorrent_install
        ;;
        4)
        clear
        youget_install
        ;;
        5)
        clear
        ytdlp_install
        ;;
        6)
        clear
        baidunetdisk_install
        ;;
        7)
        clear
        xunlei_install
        ;;
        8)
        clear
        tiktokdlp_install
        ;;
        9)
        clear
        main_menu
        ;;
        *)
        clear
        WARN 'Please enter the correct number [1-9]'
        downloader_main
        ;;
        esac

}

function mediaserver_main {

    echo -e "———————————————————————————————————————————————————————————————————————"
    echo -e "1. Jellyfin installation"
    echo -e "2. Emby installation"
    echo -e "3. Plex installation"
    echo -e "4. Back to previous menu"
    echo -e "———————————————————————————————————————————————————————————————————————"
    read -ep "Please enter the number [1-4]:" num
    case "$num" in
        1)
        clear
        jellyfin_install
        ;;
        2)
        clear
        emby_install
        ;;
        3)
        clear
        plex_install
        ;;
        4)
        clear
        main_menu
        ;;
        *)
        clear
        WARN 'Please enter the correct number [1-4]'
        mediaserver_main
        ;;
        esac

}

function main_menu {

    echo_logo
    echo -e "\n1. Kubespider installation"
    echo -e "2. Downloader installation"
    echo -e "3. Media server installation"
    echo -e "4. Exit the script"
    echo -e "\n———————————————————————————————————————————————————————————————————————"
    read -ep "Please enter the number [1-4]:" num
    case "$num" in
        1)
        clear
        kubespider_install
        ;;
        2)
        clear
        downloader_main
        ;;
        3)
        clear
        mediaserver_main
        ;;
        4)
        clear
        exit 0
        ;;
        *)
        clear
        WARN 'Please enter the correct number [1-4]'
        main_menu
        ;;
        esac

}

function main {

    if_docker_install
    for i in `seq -w 2 -1 0`
    do
        echo -en "${INFO} Going to the main menu${Green} $i ${Font}\r"  
    sleep 1;
    done
    clear
    main_menu

}

main
