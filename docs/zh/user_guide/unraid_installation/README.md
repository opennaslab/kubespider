# Unraid安装Kubespider指南

本文档将step by step介绍如何在Unraid NAS上安装Kubespider

## 准备工作

- 安装插件

    本次教程均在`docker compose`(方便设置Icon)的基础上搭建，假设你的Unraid上已经安装好Compose Manager插件，参考地址：[[Plugin] Docker Compose Manager - Plugin Support - Unraid](https://forums.unraid.net/topic/114415-plugin-docker-compose-manager/)

- 准备配置文件目录

    为了方便管理备份配置文件，这里我们以Unraid挂载的共享目录下新建一个`Config`目录存放各种app的配置文件，在里面依次新建`kubespider`,`aria2`等等目录

## 安装Kubespider

在Unraid-Docker菜单中往下拉，找到compose manager的`Add new stack`按钮新建一个stack

![](./images/01-newstack.png?msec=1710653272987)

之后再点击stack名称前面的齿轮图标，选择`Edit stack`-`Compose file`

![](./images/02-composefile.png?msec=1710653272987)

这里编写docker-compose.yml，酌情修改以下代码

```yaml
services:
  kubespider:
    container_name: kubespider
    image: cesign/kubespider:latest
    environment:
      - PUID=1000
      - PGID=100
      - TZ=Asia/Shanghai
    ports:
      - 3080:3080
    volumes:
      - /mnt/user/Files/Config/kubespider/config:/app/.config
    networks:
      - kb
networks:
  kb:
    name: kb
```

点击`Save changes`保存stack，会有个弹窗提示`Edit Stack UI Labels`，可以选择给`kubespider`配置一个icon图标

![](./images/03-savestack.png?msec=1710653272988)

粘贴图标链接到Icon那一栏，图标来源参考: [xushier/HD-Icons](https://github.com/xushier/HD-Icons)

> https://cdn.jsdelivr.net/gh/xushier/HD-Icons@master/border-radius/Kubespider_A.png

这时候点击右侧`Compose up`即可启动容器，等待片刻拉取镜像即可，容器列表里即可看到

![](./images/04-kubespider.png?msec=1710653272988)

## 安装配置下载器

Kubespider提供了诸如aria2、迅雷、qbit、yt-dlp、yutoo、tiktok-dlp等诸多下载器，对应不同种类的资源，可以根据自己需求选择性安装对应的下载器，这里以yutoo下载器为例

同上步骤，新建一个stack命名为yutoo，通过kubespider的安装文档可以看出，yutoo下载器的安装脚本在`hack/install_yutto.sh`

我们找到`install_yutto.sh`文件，里面实际上也是用docker容器的方式运行

![](./images/05-installyutto.png?msec=1710653272990)

这里由于是采用`docker run`的方式运行，我们需要用[Composerize](https://www.composerize.com/)网站转换成compose的方式，注意修改你对应的环境变量和路径映射

![](./images/06-composerize.png?msec=1710653272990)

将转换后的`docker-compose`内容复制粘贴到Unraid对应的stack文件

![](./images/07-yuttostack.png?msec=1710653272988)

同样保存之后，UI label弹窗配置一下Icon

> https://cdn.jsdelivr.net/gh/xushier/HD-Icons@master/border-radius/Bilibili_B.png

![](./images/08-yuttouilabel.png?msec=1710653272988)

等容器拉取启动完成之后，列表里即可看到yutoo下载器配置成功

![](./images/09-yutto.png?msec=1710653272988)

## 修改Kubespider配置文件

回到我们一开始新建的目录`Config/kubespider`中，找到`download_provider.yml`

修改对应的yutto下载器配置信息

```yaml
yutto:
  type: yutto_download_provider
  enable: true
  http_endpoint_host: http://192.168.2.167 #你的nas 
  http_endpoint_port: 3084
  priority: 1
```

修改source_provider.yml文件对应的信息

```yaml
bilibili_source_provider:
  type: bilibili_source_provider
  enable: true
  downloader: yutto
```

这样我们就启用了哔哩哔哩视频下载的source_provider并且指定yutto为对应的下载器，重启kubespider容器生效

## 后续

接下来的使用就和官方文档里操作一样，配置好浏览器插件，右键发送即可下载。如果有更多下载器安装，请参考上文yutto下载器，原理基本一样