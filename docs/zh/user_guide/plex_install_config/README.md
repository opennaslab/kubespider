# Plex安装和配置

Plex是一套媒体播放器及媒体服务（英语：Media server）软件，让用户整理在装置上的有声书、音乐、播客、图片和影片档案，以供串流至流动装置、智能电视和电子媒体播放器（英语：Digital media player）上。Plex可用于Windows、Android、Linux、OS X。另外，Plex亦让用户透过该平台观看来自YouTube、Vimeo和TED等内容提供商的影片。

## 效果演示
![img](../../../images/plex-video-show.jpg)

## 安装
### 1.获取Plex口令
访问[Plex Claim](https://www.plex.tv/claim/)注册，获取Plex口令代码。  
![img](../../../images/plex-claim-code.jpg)

### 2.安装Plex docker
运行如下命令即可：
```sh
git clone https://github.com/jwcesign/kubespider.git
cd kubespider
export PLEX_CLAIM=<获取到的代码>
bash hack/install_plex.sh
```

## 配置
打开地址`http://<server_ip>:32400`，选择将`/nas`作为电影文件夹:
![img](../../../images/plex-add-dir.jpg)
