# YouTube资源提供器配置
## 简介
YouTube是一个美国网络视频共享网站，总部设在加利福尼亚州的圣布鲁诺。 该服务由史蒂夫-陈和贾维德-卡里姆于2005年2月推出，于2006年10月被谷歌以16.5亿美元收购。 自发布以来，YouTube已经成为互联网上最大的搜索引擎之一，每天接收数十亿的观众。  
官方地址：[youtube.com](https://youtube.com/)  
本资源提供器旨在实现**链接触发下载**，简化下载流程。

## 最终效果
最终效果如下图，在Chrome中右键，选择`Send to Kubespider`，Kubespider会自动下载YouTube视频资源。
![img](../../images/youtube_final_show.gif)

## 配置
### 1.前提
你已经安装并配置好yt-dlp下载器，并对接Kubespider；如果未安装，请先参照 [link](../ytdlp_download_provider/README.md) 安装。

### 2.配置手册
你可以通过`${HOME}/kubespider/.config/source_provider.yaml`配置，配置解释如下：
```yaml
youtube_source_provider:
  type: youtube_source_provider
  enable: true
  downloader: yt-dlp
```

其中：  
* `youtube_source_provider`: 名称，可自定义（不可重复），可以在 `source_provider.yaml` 中按名称指定下载器，此处示例为 youtube_source_provider。
* `type`: 表示此下载器的类型，需为 `youtube_source_provider`。
* `downloader`: 指定使用的download软件，如果不需要高级下载策略，这里无需修改。
* `enable`: 设置是否使用此provider，只能使用一个，后续开发优先级后可以多个一起使用。

## 测试
设置好后，直接重启Kubespider即可。
```sh
docker restart kubespider
```

安装最终效果测试即可。