#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

function handle_trap() {
  docker ps -a
  docker logs kubespider
  docker logs baidunetdisk
  docker logs aria2-pro
  docker logs plex
  docker logs thunder
  docker logs youget
  docker logs tiktok-dlp
}

trap handle_trap ERR EXIT

#1. Test deploy Kubespider
./hack/install_kubespider.sh
sleep 10
docker ps | grep -e kubespider -e aria2-pro
if [[ $? != 0 ]]; then
  exit 1
fi

log=`docker logs kubespider`
if [[ $log =~ 'Traceback' ]]
then
  exit 1
fi

#2. Test deploy baidu net disk
./hack/install_baidunetdisk.sh
sleep 10
docker ps | grep -e baidunetdisk
if [[ $? != 0 ]]; then
  exit 1
fi

#3. Test deploy plex
export PLEX_CLAIM=fake_claim
./hack/install_plex.sh
sleep 10
docker ps | grep -e plex
if [[ $? != 0 ]]; then
  exit 1
fi

#4. Test deploy thunder
./hack/install_thunder.sh
sleep 10
docker ps | grep -e thunder
if [[ $? != 0 ]]; then
  exit 1
fi

#5. Test deploy tiktok-dlp
./hack/install_tiktokdlp.sh
sleep 10
docker ps | grep -e tiktok-dlp
if [[ $? != 0 ]]; then
  exit 1
fi

#6. Test deploy youget
./hack/install_youget.sh
sleep 10
docker ps | grep -e youget
if [[ $? != 0 ]]; then
  exit 1
fi
# ffmpeg needs to be installed to merge video and audio
docker exec youget ffmpeg -version
if [[ $? != 0 ]]; then
  exit 1
fi

#7. Test deploy yt-dlp
./hack/install_ytdlp.sh
sleep 10
docker ps | grep -e yt-dlp
if [[ $? != 0 ]]; then
  exit 1
fi
# ffmpeg needs to be installed to merge video and audio
docker exec yt-dlp ffmpeg -version
if [[ $? != 0 ]]; then
  exit 1
fi
