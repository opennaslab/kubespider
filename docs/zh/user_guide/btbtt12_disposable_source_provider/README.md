# btbtt12单任务资源提供器配置
## 简介
BT之家单版社区平台，最快提供最新最全高清电影、动漫、韩剧、日剧、美剧、无损音乐、体育、小说等BT迅雷下载以及资讯！官方地址：[btbtt12.com](https://www.btbtt12.com/)  
本资源提供器旨在实现**链接触发下载**，简化下载流程。

## 前提
你已经安装好了Kubespider/Kubespider chrome插件。

## 配置手册
你可以通过`${HOME}/kubespider/.config/source_provider.cfg`配置，配置解释如下：
```cfg
{
    ...
    "btbtt12_disposable_source_provider": {
        "enable":true
    },
    ...
}
```

`enable`：是否开启此provider，因为此provider无需口令等用户信息，所以默认开启。

## 启用配置
设置好后，直接重启Kubespider即可。
```sh
docker restart kubespider
```

TBD：增加如何使用插件触发下载教程。