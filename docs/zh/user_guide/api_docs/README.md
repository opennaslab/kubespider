# API手册
基于Kubespider的架构，为了便于开发者开发更多的下载触发方式，在此详细描述Kubespider webhook的API。

## 获取所有下载提供器
API接口 GET /api/v1/downloadproviders  

响应内容:
```json
{
    "aria2_download_provider":false,
    "qbittorrent_download_provider":false,
    "xunlei_download_provider":true
}
```
true代表此download provider开启，反之则关闭。

## 获取所有资源提供器
API接口 GET /api/v1/surceproviders

响应内容:
```json
{
    "btbtt12_disposable_source_provider":true,
    "meijutt_source_provider":true,
    "mikanani_source_provider":true
}
```
true代表此download provider开启，反之则关闭。

## 触发下载
API接口 POST /api/v1/download

请求内容：
```json
{
    "dataSource": <url>,
    "path": ""
}
```
* `<url>`表示资源相关地址，如magnet链接，torrent地,http地址等。
* path表示下载路径，如`钢铁侠1`。

## 健康检查
API接口 GET /healthz

响应内容:
```
OK
```
