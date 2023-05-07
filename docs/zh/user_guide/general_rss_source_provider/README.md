# general_rss_source_provider资源提供器配置
## 简介
本资源提供器旨在提供通用的rss订阅资源下载服务

## 配置
### 1.前提
你已经安装好了Kubespider

### 2.配置手册
你可以通过`${HOME}/kubespider/.config/source_provider.yaml`配置，普通配置如下（以RSSHUB的深影订阅为例）：
```yaml
general_rss_source_provider:
    enable: true
    type: general_rss_source_provider

    rss_name: 深影译站
    rss_link: http://192.168.124.10:1200/shinybbs
    file_type: movie
    link_type: magnet # [magnet, torrent]
    downloader: 
      - qbittorrent
    download_param:
      tags:
        - 电影
        - RSS
      category: 电影
```

* `enable`：是否开启此provider
* `type`：订阅源类型，需为`general_rss_source_provider`
* `rss_name`：rss资源名称
* `rss_link`：rss订阅链接
* `file_type`：下载资源类型标记，只支持Kubespider的六种内容，分别为general、tv、movie、video_mixed、music、picture
* `downloader`: 指定下载器
* `download_param`: 指定下载器对应的下载参数，具体参数请参考对应下载器的文档

所有资源将默认保存在`download_path/rss_name`中，其中`download_path`为所使用下载器中配置的下载路径，`rss_name`为配置选项。如果你想根据资源的标题自定义下载路径，可以添加一个字段为`title_pattern`的正则表达式配置。以如下标题为例：`【喵萌奶茶屋】★04月新番★[我内心的糟糕念头/Boku no Kokoro no Yabai Yatsu][05][1080p][简日双语][招募翻译]`，添加正则表达式:
```yaml
xxxxx_rss:
    ...
    title_pattern: \【(.*)\】.*?\[(.*?)\/
```
该表达式会根据标题提取出一个数组：`['喵萌奶茶屋', '我内心的糟糕念头']`，则新的保存路径为：`download_path/喵萌奶茶屋/我内心的糟糕念头`


### 3.测试
设置好后，直接重启Kubespider即可。
```sh
docker restart kubespider
```

## 友情提示
* 如若不知道如何获取rss订阅，可以参考https://docs.rsshub.app/
* 如果选择自部署rsshub，请注意是否拥有魔法环境，否则部分rss订阅无法获取