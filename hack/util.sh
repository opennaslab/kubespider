#!/usr/bin/env bash

export image_registry=""

function util::set_registry_for_image() {
    if [[ $CHINA_MAINLAND == "TRUE" ]];then
        export image_registry=registry.cn-hangzhou.aliyuncs.com/jwcesign
    else
        export image_registry=index.docker.io/cesign
    fi
}

function util::get_latest_release_version() {
    curl --silent https://api.github.com/repos/opennaslab/kubespider/tags | grep -o '"name": "[^"]*' | cut -d'"' -f4 | head -n1
}
