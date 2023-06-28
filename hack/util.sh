#!/usr/bin/env bash

export image_registry=""

function util::set_registry_for_image() {
    if [[ $CHINA_MAINLAND == "TRUE" ]];then
        export image_registry=registry.cn-hangzhou.aliyuncs.com/jwcesign
    else
        export image_registry=index.docker.io/cesign
    fi
}
