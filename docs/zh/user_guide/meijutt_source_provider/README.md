# meijutt资源提供器配置
## 简介
meijutt有丰富的美剧内容，提供高质量下载资源。官方地址：[meijutt.tv](https://www.meijutt.tv/)  
本资源提供器旨在实现**全自动追剧**，当你订阅的美剧有更新时，自动下载，你能随时方便的观看。

## 前提
你已经安装好了Kubespider/Kubespider chrome插件

## 配置手册
你可以通过`/root/.kubespider/source_provider.cfg`配置，配置解释如下：
```cfg
{
    ...
    "meijutt_source_provider": {
        "enable": true,
        "download_path": "meijutt",
        "tv_links": []
    },
    ...
}
```

`enable`：是否开启此provider。  
`download_path`：下载路径，最终的下载路径为`/root/.kubespider/download_provide.cfg`中配置路径+此路径。    
`tv_links`：tv剧地址，直接通过Kubespider chrome插件发送美剧地址URL即可：  
![img](../../images/../../images/kubespider-chrome-ext-usage.png)  

其中Server地址为 http://<server_ip>:3080

## 启用配置
设置好后，直接重启Kubespider即可。
```sh
docker restart kubespider
```