# ANi资源提供器配置
## 简介
ANi Project是一个全自动下载流媒体网站（[动画疯](https://ani.gamer.com.tw/)、[Bilibili](https://www.bilibili.com/anime/)等）番剧资源的项目。官方频道：[Telegram Channel](https://t.me/channel_ani)

由于ANi项目与上游的流媒体平台放送时间完全同步，所以该源能够**最及时**地跟踪正在放送的番剧更新。

本项目将会同步ANi更新的所有番剧到你的私有库中。由于是内嵌字幕，该项目的视频源不适合用作收藏，我们推荐定期清除旧的下载。

因为ANi的API提供的是直链下载，所以本源要求必须正确配置好aria2或其他类似下载软件。

## 前提
你已经安装好了Kubespider。

## 配置手册
你可以通过`${HOME}/kubespider/.config/source_provider.yaml`配置，配置解释如下：
```yaml
ani_source_provider:
  type: ani_source_provider
  enable: true
  rss_link: https://api.ani.rip/ani-download.xml
  classification_on_directory: true
  blacklist:
    - 孤獨搖滾！
    - 機動戰士鋼彈 水星的魔女
```

* `type`：订阅源类型，需为`ani_source_provider`。
* `enable`：是否开启此provider。
* `rss_link`：ANi的API地址，默认已经填好。
* `classification_on_directory`：是否按照番剧名分文件夹保存。启用该项有助于Emby/Jellyfin等插件显示“Shows”页面。
* `blacklist`：黑名单，可以是`list`或者`str`，在黑名单中的番剧将不会被下载。黑名单使用纯字符串匹配，**不支持正则表达式**，为空时默认下载所有番剧。

下载好的文件默认保存在`$download_base_path/TV/ANi`中，可根据该路径合理映射docker volume。

## 启用配置
默认配置已经能够运行，将`enable`改为`true`后直接重启Kubespider即可。

```sh
docker restart kubespider
```

因为KubeSpider默认的更新机制是每3600秒（1小时），我们推荐在整点后若干分钟启动Kubespider，每次更新时能够恰好抓到最新的番剧信息，或者手动将docker容器中`/kubespider/core/period_server.py`中line 17：

```python
class PeriodServer:
    def __init__(self, source_providers) -> None:
        self.state_config = YamlFileConfigReader(Config.STATE.config_path())
        self.period_seconds = 3600
        self.source_providers = source_providers
        self.queue = queue.Queue()
```

`self.period_seconds`调整为1800或更低。但是请注意，过短的刷新间隔可能导致资源占用的增加。