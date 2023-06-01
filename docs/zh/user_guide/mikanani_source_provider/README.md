# mikanani资源提供器配置
## 简介
蜜柑计划是新一代的动漫下载站，专业提供动漫、动漫下載、新番下载、动画下载等服务。官方地址：[mikanani.me](https://mikanani.me/)  
本资源提供器旨在实现**全自动追番**，当你订阅的动漫有更新时，自动下载，你能随时方便的观看。

## 前提
你已经安装好了Kubespider。

## 配置手册
你可以通过`${HOME}/kubespider/.config/source_provider.yaml`配置，配置解释如下：
```yaml
mikanani_source_provider:
  type: mikanani_source_provider
  enable: false
  # 将以下rss链接更换为自己的mikan订阅链接
  # 格式为 https://mikanani.me/RSS/MyBangumi?token=***mytoken***
  rss_link: https://mikanani.me/Home/Classic
  downloader:
    - qbittorrent
  download_param:
    tags:
      - mikanani
  filter: ^((?!先行).)*$
```

* `type`：订阅源类型，需为`meijutt_source_provider`。
* `enable`：是否开启此provider。  
* `rss_link`：mikanani账号的rss链接，获取方法如下：  
  1. 去[mikanani](https://mikanani.me/)注册账号，开启高级订阅 
   ![img](../../../images/mikanani_source_provider_cfg_1.jpg)
  2. 关注你喜欢的动漫
   ![img](../../../images/mikanani_source_provider_cfg_2.jpg)
  3. 查看RSS链接，选择复制链接地址并设置为`rss_link`即可
   ![img](../../../images/mikanani_source_provider_cfg_3.jpg)
* `downloader`：指定使用的下载器，格式为数组，内容需要精确地跟 `downloader_provider.yaml` 中声明的名称一样；下载优先级将由数组顺序决定。
* `download_param`：下载时传给下载器的额外参数，具体参数需要参考下载器定义。
* `filter`：用于过滤标题名的正则表达式。

## 启用配置
设置好后，直接重启Kubespider即可。
```sh
docker restart kubespider
```
