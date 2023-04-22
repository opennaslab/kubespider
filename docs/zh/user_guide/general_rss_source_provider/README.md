# general_rss_source_provider资源提供器配置
## 简介
本资源提供器旨在提供通用的影视rss资源下载服务

## 配置
### 1.前提
你已经安装好了Kubespider

### 2.配置手册
你可以通过`${HOME}/kubespider/.config/source_provider.yaml`配置，配置解释如下：
```yaml
general_rss_source_provider:
    enable: false
    type: general_rss_source_provider
    rss_name: 深影译站
    rss_link: http://192.168.124.10:1200/shinybbs
    rss_type: 电影
    flag: movie
    decs: decs
    exec_time: 8
    check_time: 0
```

* `type`：订阅源类型，需为`general_rss_source_provider`。
* `enable`：是否开启此provider。  
* `rss_name`：rss资源名称，随意设置。
* `rss_link`：rss订阅链接。
* `rss_type`：rss资源类型，随意设置。
* `flag`：下载资源类型标记，只支持Kubespider的六种内容，分别为general、tv、movie、video_mixed、music、picture。
* `decs`：rss资源描述，随意设置。
* `exec_time`：保持默认。
* `check_time`：保持默认。



### 3.测试
设置好后，直接重启Kubespider即可。
```sh
docker restart kubespider
```

## 友情提示
* 如若不知道如何获取rss订阅，可以参考https://docs.rsshub.app/
* 如果选择自部署rsshub，请注意是否拥有魔法环境，否则部分rss订阅无法获取。