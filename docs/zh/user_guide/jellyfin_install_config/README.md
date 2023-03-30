# Jellyfin安装和配置

`Jellyfin`是一个自由软件媒体系统，可让您控制媒体的管理和流媒体。它是专有的Emby和Plex的替代品，可通过多个应用程序从专用服务器向终端用户设备提供媒体。Jellyfin是Emby 3.5.2版本的后代，移植到.NET Core框架以支持完整的跨平台支持。没有任何附加条件，只是一个团队想要更好地构建更好的东西并共同努力实现它，致力于让所有用户都能访问最好的媒体系统。

## 最终效果
PC端：  
<image src="./images/chrome_jellyfin.jpg" style="width: 50%">

手机APP端：  
<image src="./images/app_jellyfin.jpeg" style="width: 50%">

## 安装  
在安装Jellyfin之前，请确保你已经安装好Kubespider。

### 1.安装Jellyfin  
运行如下命令即可：
```sh
git clone https://github.com/jwcesign/kubespider.git
cd kubespider
bash hack/install_jellyfin.sh
```

### 2.配置Jellyfin  
到地址`http://<server_ip>:8096`配置对应目录即可，我配置的目录和类型对应如下：
```
Mixed 对应 挂载的目录/media/Common
Movie 对应 挂载的目录/media/Movie
Shows 对应 挂载的目录/media/TV
```

配置好后，即可享用。

