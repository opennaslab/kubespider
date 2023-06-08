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
# The functions that the script can call are 'INFO' 'WARN' 'ERROR' 'if_port' 'get_uid_gid' 'get_umask' 'get_tz'.
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

    INFO "Please enter a user ID (default ${DEFAULT_GID})"
    read -ep "PUID:" SET_GID
    [[ -z "${SET_GID}" ]] && SET_GID=${DEFAULT_GID}

    clear
    INFO "You set the user id to ${SET_UID}"
    INFO "You set the group id to ${SET_GID}"

    INFO "Please confirm your settings (enter [n] to reset) [Y/n]"
    read -ep "Enter your choice:" YN
    [[ -z "${YN}" ]] && YN="y"
    if [[ ${YN} == [Nn] ]]; then
        clear
        get_uid_gid
    fi

}

function get_umask {

    DEFAULT_UMASK=$(umask)

    INFO "Please enter a user ID (default ${DEFAULT_UMASK})"
    read -ep "Umask:" SET_UMASK
    [[ -z "${SET_UMASK}" ]] && SET_UMASK=${DEFAULT_UMASK}

    clear
    INFO "You set the umask to ${SET_UMASK}"

    INFO "Please confirm your settings (enter [n] to reset) [Y/n]"
    read -ep "Enter your choice:" YN
    [[ -z "${YN}" ]] && YN="y"
    if [[ ${YN} == [Nn] ]]; then
        clear
        get_umask
    fi

}

function get_tz {

    INFO "Please enter your time zone (default UTC)"
    read -ep "TZ:" SET_TZ
    [[ -z "${SET_TZ}" ]] && SET_TZ=UTC

    clear
    INFO "You set the umask to ${SET_TZ}"

    INFO "Please confirm your settings (enter [n] to reset) [Y/n]"
    read -ep "Enter your choice:" YN
    [[ -z "${YN}" ]] && YN="y"
    if [[ ${YN} == [Nn] ]]; then
        clear
        get_tz
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

TODO

}

function aria2_install {

TODO

}

function transmission_install {

TODO

}

function qbittorrent_install {

TODO

}

function youget_install {

TODO

}

function ytdlp_install {

TODO

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
    echo -e "8. Back to previous menu"
    echo -e "———————————————————————————————————————————————————————————————————————"
    read -ep "Please enter the number [1-8]:" num
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
        main_menu
        ;;
        *)
        clear
        WARN 'Please enter the correct number [1-8]'
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