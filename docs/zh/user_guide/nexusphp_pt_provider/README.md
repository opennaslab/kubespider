# NEXUSPHP PT提供器配置

## 简介

许多PT网站，都有上传流量、下载流量，魔力值的要求，这些如果靠人工手动管理，会非常的麻烦。此提供器旨在简化 NEXUSPHP
框架类PT网站的账号维护流程，将前面所述的流程全自动化。

## 最终效果

最终效果如下图所示，配置好后，会自动做账号维护，刷上传流量，下载流量和魔力值：
![final_show](./images/final_show.png)

## 配置

### 1.前提

你已经安装好了Kubespider。同时，每个PT站，都建议使用单独的下载提供器，这里以 [hdvideo](https://hdvideo.one/) 为例，为其单独启动一个
transmission 类型的下载提供器，运行如下命令即可（注意映射端口）：

```sh
DEFAULT_VERSION=${DEFAULT_VERSION:-2.94-r1-ls24}
KUBESPIDER_HOME=${KUBESPIDER_HOME:-${HOME}}

docker run -d \
  --name=transmission \
  -e PUID=$UID \
  -e PGID=$GID \
  -e TZ=Asia/Shanghai \
  -e USER=admin \
  -e PASS=admin \
  -p 9092:9091 \
  -v ${KUBESPIDER_HOME}/kubespider/transmission-hdvideo/:/config \
  -v ${KUBESPIDER_HOME}/kubespider/nas/:/downloads \
  --restart unless-stopped \
  linuxserver/transmission:${DEFAULT_VERSION}
```

### 2.配置手册

这里，需要配置2个配置文件，`${HOME}/kubespider/.config/pt_provider.yaml`
和`${HOME}/kubespider/.config/download_provider.yaml`。

#### pt_provider.yaml配置

整体配置如下：

```yaml
hdvideo:
  type: nexusphp_pt_provider
  enable: true
  attendance: true
  main_link: https://hdvideo.one
  language: traditional_chinese
  rss_subscribe_link: xxx
  html_links:
    - xxx
  cookie: xxx
  # I suggest you to use transmission type, and also,
  # do not use this downloader to download the resource you needed.,
  # only for PT provider
  downloader: transmission-hdvideo
  # time in hour for seeding and downloading
  keeping_time: 120
  # size in GB
  max_sum_size: 200
  # max seeding count
  max_seeding: 20
```

* type: 必须为 `nexusphp_pt_provider`。
* enable: 控制是否启用此提供器。
* attendance: 是否执行签到，此配置需要根据具体资源网站是否支持签到配置。
* main_link: 资源网站主页地址。
* language: nexusphp架构网站当前用户所选择的语言,目前支持三种语言,
  <简体中文:simplified_chinese> <繁体中文:traditional_chinese> <英文:english>
  此选项需要根据网站的情况正确配置,否则影响内容的解析。
* rss_subscribe_link: 资源订阅rss地址，这里尽量保证获取的内容中存在free类型的资源，如馒头，尽量订阅 music
  类型的资源（存在大范围free）。同时RSS链接中包含文件大小信息，如下：  
  ![rss_link](./images/rss_link.png)
* html_links: html页面过滤搜索的页面,注意过滤的时候勾选上免费,nexus搜索也支持排序,该链接可自定义,且支持多个配置
* cookie: 资源网站Cookie地址，获取方式为 F12查看cookie即可：
  ![get_cookie](./images/get_cookie.png)
  示例为：`c_secure_uid=xxx; c_secure_pass=xxx; c_secure_ssl=xxx; c_secure_tracker_ssl=xxx; c_secure_login=xxx`
* downloader: 知道下载使用的下载提供器，这里会使用前面创建的transmission。
* keeping_time: 做种保留的最长时间(无上传量)。
* max_sum_size: 每轮下载和做种的所有资源大小总和，根据你自己的磁盘大小决定。
* max_seed: 非免费资源的下载大小，根据各网站要求决定。

#### download_provider.yaml配置

前面配置了PT提供器，这里还需要配置对应的下载提供器：

```yaml
transmission-hdvideo:
  type: transmission_download_provider
  enable: true
  download_base_path: "/downloads/"
  http_endpoint: http://127.0.0.1:9092/transmission/rpc
  username: admin
  password: admin
  priority: 5
```

* type: 下载提供器类型，建议使用 `transmission_download_provider`。
* enable: 控制是否启用此提供器。
* download_base_path: 下载资源的根目录路径。
* http_endpoint: 下载资源的地址，这里前面启动了一个transmission，端口对应即可。
* username: 下载资源的用户名。
* password: 下载资源的密码。
* priority: 下载软件资源的优先级，随便设置即可。

### 3.种子下载的一些基本规则

这里，需要配置2个配置文件，`${HOME}/kubespider/.config/pt_provider.yaml`
和`${HOME}/kubespider/.config/download_provider.yaml`。

#### 种子来源:

* html页面搜索:根据用户配置的html_links搜索出来的种子
* rss订阅:根据用户配置的rss_subscribe_link搜索出来的种子
* rss下载筐: (待实现)
* 用户信息页,正在做种和正在下载的种子

#### 种子合并:

* 种子的来源方式不同,每种来源的种子能获取到的信息存在差异,所以需要按种子id对这些信息进行合并

#### 种子的促销规则:

* 普通:正常统计上传和下载
* 免费:不计下载,正常计算上传
* 2X:正常统计下载,计算两倍的上传
* 2X 免费:不计下载,计算两倍的上传
* 50%:统计50%下载,正常计算上传
* 2X 50%:统计50%下载,计算两倍的上传
* 30%:统计30%下载,正常计算上传

#### 下载的空间管理:

* 文件下载需要占用磁盘空间,所以需要空间管理
* 实例初始化需要配置最大占用空间
* 种子下载之后需要减去对应的磁盘空间
* 种子删除之后需要释放出对应的空间

#### 下载种子的影响因素计算(待实现):

* 种子的大小(占用磁盘的空间)
* 用户带宽(影响下载速度,可能出现种子免费过期了,还没下载完成的情况,这个要综合考虑)
* 做种人数(做种人数越多,下载越快,相应的抢到流量的可能性就小多了)
* 下载人数(越多的人下载,抢到上传流量的可能性更大)
* 已完成人数(完成的人数越多,潜在新增的下载用户就少了)
* 种子存活时间(种子存活时间越长,代表这个是老种子,下载的人可能不会多,但是也有可能是老种子免费了) 注:这个字段目前取不到
* 2X 免费的种子优于免费种子

#### 下载种子的选择:

* 不计下载流量的种子只有两种:免费和2X免费
* 为避免bug造成分享率过低,下载只会下载不计下载流量的种子

#### 删除种子:

* 做种数达到上限或者用户磁盘空间占用达到上限,触发种子删除
* 当种子Free时间过期,种子还没有下载完成时,删除当前种子的下载任务
* 当种子免费时间已过,并且没有上传时(TODO:计算一周内没有上传),移除该种子
* 若下载的种子在用户的收藏列表之中,该种子永远不会删除(待实现)

#### 种子魔力价值计算:

* 算法来自nexus,已实现

#### NexusPTProvider执行流程:

* 查询用户信息
* 签到
* 查询html种子,rss种子
* 合并用户做种的种子,下载的种子,html页面查询到的种子,rss种子
* 查询当前做种,下载情况,移除无效种子,释放对应磁盘空间
* 做种上限 - 已做种的种子 得到可以做种的坑位
* 从上述合并的种子种取出免费种子,按下载价值排序,按剩余坑位切片进行下载
* 下载前进行磁盘空间判断,满足条件下载,不满足条件丢弃
* 按 pt provider 的调度间隔,重复上述步骤

## TODO

* 新增用户收藏的种子来源,优先下载用户收藏的种子,种子移除逻辑修改,如果来源是收藏中的种子,不做移除
* 实现种子下载价值计算的算法
* 实现种子没有上传量的判断方法(种子信息需要入库,从库里查询)

## 使用场景

#### 做种

* 配置好做种数量:max_seed
* keeping_time设为-1
* 解释:当种子到达keeping_time设为-1时候,不会移除已下载好的种子,即会保留种子做种,一直下载下去,直到配置的磁盘空间满了或者达到做种上限

#### 刷上传量

* 配置好做种数量:max_seed
* keeping_time设为120
* 解释:当种子到达keeping_time所设定的时间没有上传量即会自动替换成其他免费种子刷上传量

## 注意事项

* 部分网站(比如馒头)会对ip进行限制,如果被判定为了盒子之后下载免费种子不享受不计流量的优惠,这种情况下不适合使用此provider

## 测试

设置好后，等一段时间，访问 `http://<server_ip>:9092` 即可看到触发下载的资源，用作账号维护：
![download_show](./images/download_show.png)


