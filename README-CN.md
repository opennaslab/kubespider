# Kubespider

![image](./docs/images/logo.png)

## 一款全自动下载/追剧工具
[![GitHub release](https://img.shields.io/github/v/release/agalwood/Motrix.svg)](https://github.com/agalwood/Motrix/releases) ![Build/release](https://github.com/agalwood/Motrix/workflows/Build/release/badge.svg) ![Total Downloads](https://img.shields.io/github/downloads/agalwood/Motrix/total.svg) ![Support Platforms](https://camo.githubusercontent.com/a50c47295f350646d08f2e1ccd797ceca3840e52/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f706c6174666f726d2d6d61634f5325323025374325323057696e646f77732532302537432532304c696e75782d6c69676874677265792e737667)

[English](./README.md) | 简体中文  
我是一个云计算工程师🤓，专注Serverles/FinOps/Runtime，利用空闲之余开发了 Kubespider。
开发Kubespider的出发点是：我有一台空闲的服务器（局域网），想把它作为NAS，实现自动追剧下载，本地笔记本电脑触发下载，同时适配各种网站资源（Youtube、Bilibili等)。

之前接触到Terraform，惊讶于其通用性。Kubespiders受到Terraform启发，旨在构建一个通用的下载编排系统，兼容各种资源平台和下载软件（如Motrix），同时兼容多种触发下载方式（只要符合Kubespider API即可）。

## 系统架构
为了实现一个通用的下载编排系统，需要适配各种资源网站和下载软件，所以将这两部分从核心功能中抽象出来：
![image](./docs/images/kubespider-architecture.png)
* `kubespider-core`：Kubespider核心模块，接受触发下载请求，调用资源提供器provider解析（最终会解析为标准模式，如用户输入bilibili博主地址，对应资源提供器输出mp4文件地址下载列表），最后调用下载提供器provider实现下载；此模块同时也会周期调用providers(如追剧provider)，下载增加的资源。
* `source-provider`：各资源网站的提供器，接受通用资源地址输入，输出为标准资源地址url，如输入为某个bilibili博主的个人主页，输出为博主视频的所有mp4下载地址。配置文件在`./kubespider/source_provider.cfg`。
* `download-provider`：各下载软件的提供器，接收`kubespider-core`的请求Task，调用对应的服务实现下载。配置文件在`./kubespider/download_provider.cfg`。

## 💽 安装
### 前提
1. 操作电脑和你的NAS服务器在同一局域网。（暂时还没有试过不在同一局域网的安装）
2. NAS服务器为linux系统。
3. NAS服务器已安装Docker。

### 默认安装
Kubespider为了适配多种资源平台，提供了许多适配器，按你的需要开启或关闭这些适配器。配置文件在`.kubespider`文件夹：

#### 1.下载代码库并且安装
```sh
git clone https://github.com/jwcesign/kubespider.git
cd kubespider
bash hack/install.sh
```
输出类似：
```sh
root@cesign [02:18:54 PM] [+33.0°C] [~/git/kubespider] [main *]
-> # bash hack/install.sh
_          _                     _     _
| | ___   _| |__   ___  ___ _ __ (_) __| | ___ _ __
| |/ / | | | '_ \ / _ \/ __| '_ \| |/ _` |/ _ \ '__|
|   <| |_| | |_) |  __/\__ \ |_) | | (_| |  __/ |
|_|\_\\__,_|_.__/ \___||___/ .__/|_|\__,_|\___|_|
                        |_|
[INFO] Start to deploy with default configuration...
f4b5c6647dbbced11e1f511167edfc0f269ef697dfe05dcba082262ba4b4234f
WARNING: Published ports are discarded when using host network mode
de37a5203a3340177e7b3d796b81245941d5f7535047b567675554c659ea7af0
[INFO] Deploy successful, check the information:
*******************************************
[INFO] It's better idea to try chrome extenstions, check here:
[INFO] It's better idea to try plex, check here:
*******************************************
Kubespider config path: /root/.kubespider/
Download file path: /root/nas/
Kubespider webhook address: http://<server_ip>:3800
Waring: Motrix server UI address: http://<server_ip>:8081, go and open motrix
```

#### 2.开启Motrix下载器  
启动的Motrix服务端口为8081，所以打开游览器，输入`http://<nas_server_ip>:8081`，打开Motrix软件即可：
![img](./docs/images/motrix-server-start.jpg)


#### 3.检查是否安装成功  
查看kubespider容器日志即可，无报错即可：
```sh
root@cesign [04:20:36 PM] [+31.0°C] [~]
-> # docker logs kubespider
2022-12-04 06:19:14,302-INFO: Source Provider:mikanani_source_provider enabled...
2022-12-04 06:19:14,302-INFO: Source Provider:btbtt12_disposable_source_provider enabled...
2022-12-04 06:19:14,302-INFO: Download Provider:motrix_download_provider enabled...
2022-12-04 06:19:14,302-INFO: Period Server start running...
2022-12-04 06:19:14,303-INFO: https://mikanani.me/RSS/MyBangumi?token=egIVi24Uxfg68bFDW5ehVgpHCadfZ1AULNYot%2b95mDo%3d
2022-12-04 06:19:14,304-INFO: Webhook Server start running...
```

#### 4.安装Chrome插件  
TBD（还未发布）

#### 5.安装Plex（非必需，可选安装）  
Plex是一个视频观看平台，能非常方便的观看下载的视频资源。最后效果如下：
![img](./docs/images/plex-video-show.jpg)
   
首先，获取Plex口令代码：访问[Plex Claim](https://www.plex.tv/claim/)注册获取口令。  
![img](./docs/img/../images/plex-claim-code.jpg)

然后，安装Plex:
```sh
git clone https://github.com/jwcesign/kubespider.git
cd kubespider
export PLEX_CLAIM=<获取到的代码>
bash hack/install_plex.sh
```

最后，配置Plex：
打开地址`http://<nas_server_ip>:32400`，将`/nas`作为电影文件夹:
![img](./docs/images/plex-add-dir.jpg)

## 🤝 参与共建 [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat)](http://makeapullrequest.com)

如果你有兴趣参与共同开发，欢迎 STAR/FORK/PR。