# Kubespider铁威马NAS安装手册

<!-- 安装步骤 -->
## 安装步骤

### 1. 安装Docker套件
`Kubespider`使用Docker安装部署，需要安装Docker套件。铁威马的TOS系统原生支持Docker，并且安装十分方便。进入铁威马后台桌面，打开应用中心，寻找Docker Manager的应用套件，点击安装即可

<image src="./images/terramaster_install_docker.png" alt="安装Docker" height="300px">  

安装完成后，在后台桌面上会出现Docker的图标

### 2. 开启SSH服务
由于铁威马系统的开放性，可以直接使用SSH登录铁威马系统后台，通过命令行的方式进行安装

首先需要开启铁威马的SSH端口权限，进入铁威马后台桌面，打开控制面板，点击服务，找到SSH服务，右上角点击启动

<image src="./images/terramaster_enable_ssh.png" alt="开启SSH服务" height="300px">  

从选项中可以看到铁威马默认SSH端口为9222而不是Linux默认使用的22端口，请务必记住。随后选择一个自己喜欢的SSH工具如：Xshell、Putty，我这里使用Windows Terminal，直接输入以下命令进入铁威马控制台
```shell
ssh -p 9222 username@terramaster-ip
```
其中`username`为初始化铁威马系统时创建的账号，`terramaster-ip`为铁威马的IP地址，密码为创建账号的密码。如果遇到保存相关凭证信息时，输入yes即可。

<image src="./images/terramaster_connect_ssh.png" alt="SSH连接铁威马后台系统" height="300px">  

进入后台后，输入以下命令检查Docker是否正常运行
```shell
docker ps
```

### 3. 设置安装目录以及配置文件
`Kubespider`通过配置文件进行下载工作，由于铁威马的应用市场中还未上架有关编辑器的应用，因此我们需要在共享文件夹中创建`Kubespider`的安装目录以及配置文件，方便我们在其他系统对`Kubespider`进行配置

首先任意选择一个共享的文件夹，在文件夹中创建一个目录用于保存后续的配置文件。例如，创建一个名为`nas`的共享文件夹，设置好权限以及空间大小配额后，大小请自行控制，启动共享
<image src="./images/terramaster_create_smb.png" alt="创建共享文件夹" height="300px">  
<image src="./images/terramaster_smb_cap.png" alt="设置共享文件夹容量" height="300px">  

此时我们可以通过smb协议对该共享文件夹进行挂载，以Windows为例，打开文件资源管理器（我的电脑），在此电脑选项右键，选择映射网络驱动器
<image src="./images/terramaster_windows_drive.png" alt="Windows挂载共享文件夹1" height="300px">  

输入铁威马的IP地址以及共享文件夹的地址，例如`\\192.168.1.170\nas`，进行连接，如果是初次连接需要输入初始化铁威马系统时创建的账号信息
<image src="./images/terramaster_windows_mount_nas.png" alt="Windows挂载共享文件夹2" height="300px">  


挂载之后创建一个文件夹用于保存后续需要保存配置文件，例如`kubespider`
<image src="./images/terramaster_create_kubespider_directory.png" alt="创建配置文件保存文件夹" height="300px">  

创建完毕后，需要下载[默认配置](https://github.com/opennaslab/kubespider/tree/main/.config)文件到该文件夹中，你可以选择手动下载保存，也可以通过命令行直接下载

首先通过SSH连接铁威马系统，然后进入共享文件夹中，默认路径为`/Volume1/nas/kubespider`，其中`Volume1`是初始化磁盘时所创建的存储卷，`nas`则是上面创建的共享文件夹，`kubespider`则是上面创建用于保存配置文件的文件夹，请务必根据自己机器情况设定
```shell
cd /Volume1/nas/kubespider
```

进入文件夹后，输入以下命令下载默认配置文件

```shell
mkdir -p dependencies/xunlei_download_provider
ter_wget https://raw.githubusercontent.com/opennaslab/kubespider/main/.config/dependencies/xunlei_download_provider/get_token.js -O dependencies/xunlei_download_provider/get_token.js
ter_wget https://raw.githubusercontent.com/opennaslab/kubespider/main/.config/download_provider.yaml
ter_wget https://raw.githubusercontent.com/opennaslab/kubespider/main/.config/pt_provider.yaml
ter_wget https://raw.githubusercontent.com/opennaslab/kubespider/main/.config/source_provider.yaml
ter_wget https://raw.githubusercontent.com/opennaslab/kubespider/main/.config/kubespider.yaml
```
<image src="./images/terramaster_download_config_final.png" alt="下载保存默认配置文件" height="300px">  

### 4. 安装下载器

> 如果你已经安装了下载器，例如`aria2`或`qbittorrent`，可以跳过这一章节直接访问[文档](https://kubespider.netlify.app/user_guide/aria2_download_provider/)进行配置，随后进入后续的正式安装章节

`Kubesipder`需要搭配下载器使用，这里以`aria2`为例，首先还是需要创建一个文件夹用于保存`aria2`的配置文件以及下载的内容，例如我在`nas`的共享文件夹中创建了一个名为`aria2`的文件夹，用于保存配置文件以及下载的文件

<image src="./images/terramaster_create_aria2_dir.png" alt="创建aria2配置文件夹" height="300px">  

我们可以直接运行以下命令启动`aria2`容器，首先配置一下环境变量，方便后续脚本的运行
```shell
export KUBESPIDER_HOME=/Volume1/nas # 按照自己的配置更改！！！
docker run -d \
    --name aria2-pro \
    --restart unless-stopped \
    --log-opt max-size=1m \
    --network host \
    -e PUID=$UID \
    -e PGID=$GID \
    -e RPC_SECRET=kubespider \
    -e RPC_PORT=6800 \
    -e LISTEN_PORT=6888 \
    -v ${KUBESPIDER_HOME}/aria2/config:/config \ # 配置文件路径，可自行更改
    -v ${KUBESPIDER_HOME}/aria2/downloads:/downloads/ \ # 下载文件路径，可自行更改
    cesign/aria2-pro:latest
```

按照上面默认的配置文件，此时`kubespider`已经可以使用`aria2`作为下载器，如果你的`aria2`配置与上述配置文件不同，请按照[文档](https://kubespider.netlify.app/user_guide/aria2_download_provider/)修改`download_provider.yaml`文件进行配置

### 5. 安装Kubespider
在准备好上述文件并安装至少一个下载器后，就可以正式安装`Kubespider`了，在终端中运行以下命令即可运行`Kubespider`

```shell
export KUBESPIDER_HOME=/Volume1/nas # 按照自己的配置更改！！！
docker run -itd --name kubespider \
    -v ${KUBESPIDER_HOME}/kubespider:/root/.config \
    --network=host \
    --restart unless-stopped \
    cesign/kubespider:latest
```
如果本地没有发现镜像，会自动拉取最新镜像后启动，如需启动一个指定的版本，请在[Docker Hub](https://hub.docker.com/r/cesign/kubespider)中选择自己合适的版本号，并将`latest`更改为对应的版本号

`Kubespider`默认占用3080端口，该端口可以在`kubespider.yaml`配置文件中自行更改

此时使用以下命令查看容器运行情况
```shell
$ docker ps
CONTAINER ID   IMAGE                           COMMAND                  CREATED          STATUS          PORTS                                                                                                                             NAMESiner
38e6e092cd42   cesign/kubespider:latest        "python3 /root/kubes…"   53 seconds ago   Up 52 seconds                                                                                                                                     kubespider
b3fce940427d   cesign/aria2-pro:latest         "/init"                  6 minutes ago    Up 6 minutes                                                                                                                                      aria2-pro
```
通过以下命令可以检查`Kubespider`的日志信息
```shell
$ docker logs -f kubespider
2023-06-01 08:43:11,182-INFO: File handler start running...
2023-06-01 08:43:11,475-INFO: Source Provider:btbtt12_disposable_source_provider enabled...
2023-06-01 08:43:11,512-INFO: Source Provider:meijutt_source_provider enabled...
2023-06-01 08:43:11,548-INFO: Source Provider:bilibili_source_provider enabled...
2023-06-01 08:43:11,583-INFO: Source Provider:youtube_source_provider enabled...
2023-06-01 08:43:11,808-INFO: Download Provider:aria2 enabled...
2023-06-01 08:43:12,028-INFO: Period Server producer start running...
2023-06-01 08:43:12,029-INFO: Download trigger job start running...
2023-06-01 08:43:12,030-INFO: PT Server start running...
2023-06-01 08:43:12,030-INFO: Downloading size is:0.000000, threshold:100.000000
2023-06-01 08:43:12,031-INFO: Period Server Quene handler start running...
2023-06-01 08:43:12,045-INFO: Webhook Server start running...
2023-06-01 08:43:12,053-INFO: Serving on http://0.0.0.0:3080
```

### 5. 安装浏览器插件
为了方便下载浏览器中的资源，我们提供了一个浏览器插件，目前仅支持chromium内核的浏览器

- 安装Aria2插件，参考：[link](https://github.com/opennaslab/kubespider/blob/main/README-CN.md#2%E8%BF%9E%E6%8E%A5aria2)
- 安装Kubespider Chrome插件，参考：[link](https://github.com/opennaslab/kubespider/blob/main/README-CN.md#3%E5%AE%89%E8%A3%85chrome%E6%8F%92%E4%BB%B6)

### 6. 浏览器一键下载演示

如果您看到这一章节，这说明已经成功安装完`Kubespider`了，并且配置好了一个基本的下载器！此时可以通过浏览器插件与`Kubespider`进行交互下载文件了

首先配置浏览器设置，安装第五章节安装好浏览器插件后，点击插件，在第二个选项中输入`Kubespider`的地址也就是nas的IP地址以及端口号，默认为3080，点击确认，如果一切正常则会提示`OK`

以meijutt为例，打开[其中任意一个页面](https://www.meijutt.tv/content/meiju28502.html) ，右键选择 `Send to Kubespider`，如果一切正常则浏览器插件图标会提示`OK`字段，现在查看Aria2插件，即可看见触发下载的任务
<!-- ![演示动画](./images/terramaster_usage.gif) -->
<image src="./images/terramaster_usage.gif" alt="演示动画" height="300px">  

这里只给最简单下载演示，更多下载场景，请看项目 [README](https://github.com/opennaslab/kubespider/blob/main/README-CN.md#-%E7%89%B9%E6%80%A7%E5%88%97%E8%A1%A8)。

