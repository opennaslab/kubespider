# Bilibili资源提供器配置
## 简介
哔哩哔哩（Bilibili）是一家中国的在线视频分享和弹幕评论平台，于2009年创建。它最初定位为ACG（动画、漫画、游戏）文化社区，但现在已扩展到包括音乐、舞蹈、科技、生活等各种领域。用户可以在B站上观看和上传视频，并与其他用户互动交流。B站以其丰富的内容、独特的弹幕系统和活跃的用户群体而闻名。
官方地址：[bilibili.com](https://bilibili.com/)  
本资源提供器旨在实现**链接触发下载**，简化下载流程。

## 最终效果
最终效果如下图，在Chrome中右键，选择`Send to Kubespider`，Kubespider会自动下载B站视频资源。
![img](./images/bilibili_final_show.gif)

## 配置
### 1.前提
你已经安装并配置好You-Get下载器，并对接Kubespider；如果未安装，请先参照 [link](../youget_download_provider/README.md) 安装。

### 2.配置手册
你可以通过`${HOME}/kubespider/.config/source_provider.cfg`配置，配置解释如下：

```yaml
bilibili_source_provider:
  type: bilibili_source_provider
  enable: true
```

* `type`：订阅源类型，需为`bilibili_source_provider`。
* `enable`：是否开启此provider，因为此provider无需口令等用户信息，所以默认开启。
* `downloader`：指定使用的下载器，格式为数组，内容需要精确地跟 `downloader_provider.yaml` 中声明的名称一样；下载优先级将由数组顺序决定。
* `download_param`：下载时传给下载器的额外参数，具体参数需要参考下载器定义。

## 测试
设置好后，直接重启Kubespider即可。
```sh
docker restart kubespider
```

安装最终效果测试即可。