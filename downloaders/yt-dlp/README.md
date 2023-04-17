# yt-dlp downloader

## Summary
[yt-dlp](https://github.com/yt-dlp/yt-dlp): A youtube-dl fork with additional features and fixes

In order to implement trigger downloading, this repository build a docker image with yt-dlp to accept http download trigger.

## Installation
Run with following command to install:
```sh
docker run --name yt-dlp -d \
    --network=host \
    -e YOUTUBE_PROXY=${http_proxy} \
    -v ${HOME}/kubespider/yt-dlp:/root/config \
    -v ${HOME}/kubespider/nas/:/root/downloads \
    --restart unless-stopped cesign/ytdlp-downloader:latest
```
`/root/config`: cookie config path.  
`/root/downloads`: download file store path.  
`YOUTUBE_PROXY`: proxy used to download videos from YouTube, it could be empty.

## Build
Build with following command(If you have no proxy, please delete --build-arg HTTP_PROXY=http://xxx --build-arg HTTPS_PROXY=http://xxx):
```sh
# Go to the directory where this README.md exists
docker build -t cesign/ytdlp-downloader . --build-arg HTTP_PROXY=http://xxx --build-arg HTTPS_PROXY=http://xxx
```