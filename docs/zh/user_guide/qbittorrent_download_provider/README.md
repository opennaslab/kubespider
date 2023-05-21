# qBittorrent下载提供器安装和配置
## 简介
qbittorrent是一个开源的bt种子下载工具，界面简洁功能强大并且支持多平台安装使用。在Linux版本上已支持基于WebUI的Docker版本，方便Nas用户使用。qbittorrent-enhanced-edition则在原始版本的基础上添加额外功能，感谢 [SuperNG6](https://github.com/SuperNG6/Docker-qBittorrent-Enhanced-Edition) 的Docker移植。

## 最终效果
![使用界面](./images/final_show.gif)

## 安装
### 1. 安装qBittorrent
运行如下命令即可
```sh
git clone https://github.com/opennaslab/kubespider.git
cd kubespider
bash hack/install_qbittorrent.sh
```

### 2. 确认安装
运行如下命令，确认迅雷已经安装成功：
```sh
docker ps | grep qbittorrent
```
输出类似：
```sh
CONTAINER ID   IMAGE                           COMMAND   CREATED         STATUS        PORTS     NAMES
05d180956975   superng6/qbittorrentee:latest   "/init"   2 seconds ago   Up 1 second             qbittorrentee
```

打开浏览器进入如下网址检查是否成功启动
```sh
http://<your-nas-ip>:8080
```
如果正常启动，则可以看到输入账号密码的界面，初始账号密码为
```
username = admin
password = adminadmin
```
![登录界面](images/login_page.png)

登录之后则可以进入上述最终效果中的使用界面

## 配置
### 1.WebAPI配置
默认配置足以运行，但是如果有特殊需求如更改用户名或密码，则可以进入WebAPI配置项中进行配置
![WebUI配置](images/webui_config.png)
**需要注意，如果更改了WebAPI相关配置，在Kubespider对接配置中进行对应的修改**

### 2.添加Tracker列表
由于BT下载的特性，需要Tracker服务器进行连接。对于不自带Tracker服务器的种子文件或磁力连接，我们可以在Qbittorrent中人工添加Tracker服务器以提高连接p2p网络的速度

打开设置中的`BitTorrent`选项，往下寻找到`Automatically update public trackers list`选项，勾选后在输入框内输入以下网址，最后保存即可

```
https://jsd.cdn.zzko.cn/gh/XIU2/TrackersListCollection/best.txt
```

![添加Tracker](images/add_tracker.png)

> 感谢[XIU2](https://github.com/XIU2/TrackersListCollection)的收集和更新

当然你也可以手动在上面的输入框中自行将上述连接中的Trackers列表地址添加进去

### 3.Kubespider对接配置

如果你对WebAPI进行了修改配置，请务必修改Kubespider的对接配置，如果没有修改则可以直接使用默认配置使用

qBittorrent对应的配置文件如下

```yaml
qbittorrent:
  type: qbittorrent_download_provider
  enable: false
  download_base_path: "/downloads/"
  http_endpoint_host: http://127.0.0.1
  http_endpoint_port: 8080
  username: admin
  password: adminadmin
  verify_webui_certificate: false
  priority: 2
  tags:
    - kubespider
  category: kubespider
```

其中:

* 名称，可自定义（不可重复），可以在 `source_provider.yaml` 中按名称指定下载器。
* `type`: 表示此下载器的类型，需为 `qbittorrent_download_provider`。
* `enable`: 设置是否使用此provider，只能使用一个，后续开发优先级后可以多个一起使用。
* `download_base_path`: 设置下载基础路径，后续文件都将保存在该目录中，务必设置在你所挂载的nas目录或其他目录。
* `http_endpoint_host`: qbittorrent服务所在服务器地址。
* `http_endpoint_port`: qbittorrent的API服务端口，默认8080。
* `username`: 登录WebAPI的用户名，与WebAPI设置中保持一致。
* `password`: 登录WebAPI的密码，与WebAPI设置中保持一致。
* `verify_webui_certificate`: 是否启用WebAPI的证书认证，目前务必设置为false。
* `priority`: 下载提供器优先级，数字越小，优先级越高，下载资源时按优先级尝试，无法下载或下载失败时切换下载器。
* `tags`: 触发下载时使用的tag，可用于资源分类，不需要时可留空或不设置。
* `category`: 触发下载时使用的category，可用于资源分类，不需要时可留空或不设置。

#### 3.1 来自订阅源的配置

qBittorrent支持订阅源传递过来的下载参数：

source_provider.yaml:

```yaml
---
mikan_oshi:
  enable: true
  rss_link: https://mikanani.me/RSS/Bangumi?bangumiId=2995&subgroupid=534
  type: mikanani_source_provider
  downloader:
    # 指定使用 qBittorrent进行下载
    - qb
  download_param:
    tags:
      - oshinoko
      - mikan_tv
    category: mikananime
```

在触发下载时，订阅源会将 `download_param` 内的参数传递过来，其值的含义参考上面的格式定义。

### 4.测试下载
配置好后，运行如下命令：
```
docker restart kubespider
```
按最终效果图测试一下即可。
