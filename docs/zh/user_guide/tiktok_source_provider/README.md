# 抖音资源提供器配置

## 简介

抖音是国内最大的短视频平台，官方地址：[douyin.com](https://douyin.com/)
本资源提供器旨在实现**分享链接触发下载无水印视频**，简化下载流程。

## 最终效果

最终效果如下图，通过短视频分享按钮获取分享链接，填入Chrome扩展，Kubespider会自动下载抖音视频资源。
![img](images/tiktok_final_show.gif)

## 配置

### 1.前提

你已经安装并配置好tiktok-dlp下载器，并对接Kubespider；如果未安装，请先参照 [link](../tiktok_download_provider/README.md)安装。

### 2.配置手册

你可以通过`${HOME}/kubespider/.config/source_provider.yaml`配置，配置解释如下：

```yaml
douyin_source_provider:
  enable: false
  type: tiktok_source_provider
  downloader: tiktok-dlp
```

* `type`：订阅源类型，需为`tiktok_source_provider`。
* `enable`：是否开启此provider，因为此provider需要对应downloader支持，所以默认关闭。
* `downloader`: 下载器名称，需为`tiktok-dlp`。

## 测试

设置好后，直接重启Kubespider即可。

```sh
docker restart kubespider
```

按照最终效果测试即可。