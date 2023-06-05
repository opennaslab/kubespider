# you-get downloader

## Summary
[You-Get](https://github.com/soimort/you-get) is a tiny command-line utility to download media contents (videos, audios, images) from the Web, in case there is no other handy way to do it.

In order to implement trigger downloading, this repository build a docker image with you-get to accept http download trigger.

## Installation
Run with following command to install:
```sh
docker run --name youget -d \
    --network=host \
    -e BILIBILI_COOKIE_PATH=/app/config/bilibili_cookie.txt \
    -v ${HOME}/kubespider/youget:/app/config \
    -v ${HOME}/kubespider/nas/:/app/downloads \
    --restart unless-stopped cesign/youget-downloader:latest
```
`/app/config`: cookie config path.  
`/app/downloads`: download file store path.  
`BILIBILI_COOKIE_PATH`: bilibili cookie path.

## Build
Build with following command(If you have no proxy, please delete --build-arg HTTP_PROXY=http://xxx --build-arg HTTPS_PROXY=http://xxx):
```sh
# Go to the directory where this README.md exists
docker build -t cesign/youget-downloader . --build-arg HTTP_PROXY=http://xxx --build-arg HTTPS_PROXY=http://xxx
```