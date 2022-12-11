# meijutt资源提供器配置
## 简介
meijutt有丰富的美剧内容，提供高质量下载资源。官方地址：[meijutt.tv](https://www.meijutt.tv/)  
本资源提供器旨在实现**全自动追剧**，当你订阅的美剧有更新时，自动下载，你能随时方便的观看。

## 前提
你已经安装好了Kubespider/Kubespider chrome插件

## 配置手册
你可以通过`/root/.kubespider/source_provider.cfg`配置，配置解释如下：
```cfg
ENABLE=true
DOWNLOAD_PATH=meijutt
TV_LINKS=
```

`ENABLE`：是否开启此provider。  
`DOWNLOAD_PATH`：下载路径，最终的下载路径为`/root/.kubespider/download_provide.cfg`中配置路径+此路径。    
`TV_LINKS`：tv剧地址，获取方法如下：  
TDB

## 启用配置
设置好后，直接重启Kubespider即可。
```sh
docker restart kubespider
```
TDB