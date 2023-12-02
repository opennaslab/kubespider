# yutto downloader

## Summary
[Yutto](https://github.com/yutto-dev/yutto)，A cute and willful Bilibili downloader (CLI).

In order to implement trigger downloading, this repository build a docker image with yutto to accept http download trigger.

## Installation
Run with following command to install:
```sh
docker run -d \
    --name yutto \
    --network=host \
    -e BILIBILI_SESSDATA='d8bc7493%2C2843925707%2C08c3e*81' \
    -v ${HOME}/kubespider/yutto:/app/config \
    -v ${HOME}/kubespider/nas/:/app/downloads \
    --restart unless-stopped \
    cesign/yutto-downloader:latest
```
`/app/config`: config path.  
`/app/downloads`: download file store path.  
`BILIBILI_SESSDATA`: bilibili cookie SESSDATA.

## Build
Build with following command(If you have no proxy, please delete --build-arg HTTP_PROXY=http://xxx --build-arg HTTPS_PROXY=http://xxx):
```sh
# Go to the directory where this README.md exists
docker build -t cesign/yutto-downloader . --build-arg HTTP_PROXY=http://xxx --build-arg HTTPS_PROXY=http://xxx
```