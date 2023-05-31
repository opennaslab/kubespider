# Kubespider群晖NAS安装手册

## 场景
对于NAS玩家，或多或少都有资源下载需求，包括但不限于： 
* 自动下载更新的TV/Movie/文件/其他，方便后续个人学习使用。
* 有一个大型文件或各式各样的文件下载，希望能方便的触发NAS机器下载。
* 自定义条件，自动触发下载相关资源，如自动下载豆瓣评分大于8的资源。
* 在某些资源网站上，有下载需求，如B站，YouTube，抖音等各种资源网站，供个人学习使用。
* 入门/资深PT玩家，需要对自己的账号维护，如自动刷上传下载量。

如果你有这些需求，那么Kubespider就是你要找的All-in-one的资源下载系统，打造属于自己的家庭NAS下载中心。

## 安装步骤

### 1.安装依赖软件  
去下载中心下载：Docker，git server，文本编辑器三个软件。  
<image src="./images/synology_docker.jpeg" alt="kubespider" height="300px">
<image src="./images/synology_git.jpeg" alt="kubespider" height="300px">
<image src="./images/synology_editor.jpeg" alt="kubespider" height="300px">  

### 2.开启SSH  
去 `控制面板/终端机和SNMP` 启用SSH功能，然后应用：  
<image src="./images/synology_ssh.jpeg" alt="kubespider" height="400px">

### 3.确定NAS局域网IP
在局域网内，查询到NAS主机IP如下（桌面右下脚），如这里的 `192.168.1.100`：  
<image src="./images/synology_ip.png" alt="kubespider" height="400px">

### 4.安装SSH工具
* 如果你是Windows，可以使用PuTTY，下载地址请点这里 [link](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html)。
* 如果你是Mac OS，无需安装任何工具。

### 5.连接NAS主机
* 如果你是Windows，安装好PuTTY后，通过PuTTY连接NAS的IP，用户名和密码是你登陆NAS网页页面的用户名和密码，如下：  
  <image src="./images/synology_windows_putty.png" alt="kubespider" height="400px">  
  点击Open后输入你的用户名密码(替换用户名，输入密码时不可见，直接输入就行):  
  <image src="./images/synology_windows_putty_login.png" alt="kubespider" height="200px">

* 如果你是Mac OS，打开终端，输入如下命令连接(替换用户名, 输入密码时不可见，直接输入就行)：  
  <image src="./images/synology_mac_login.png" alt="kubespider" height="200px">

如上步骤完成后，最后切换到 `root` 用，命令如下(输入密码时不可见，直接输入就行，密码和之前步骤一样)：
```sh
jwcesign@NICE:~$ sudo -i
Password:
root@NICE:~#
```

### 6.创建安装目录  
通过控制面板，创建安装目录：  
<image src="./images/synology_dir_create.png" alt="kubespider" height="600px">

### 6.下载Kubespider
通过如下命令切换到安装目录 `/volume1/kubespider` (可能随环境变化而变化)，下载Kubespider，拷贝运行如下命令:
```sh
cd /volume1/kubespider/
git clone https://github.com/opennaslab/kubespider.git
```

### 7.安装Kubespider
步骤6运行结束后，拷贝运行如下命令即可：
```sh
cd /volume1/kubespider/kubespider
export KUBESPIDER_HOME=/volume1
bash hack/install_kubespider.sh
```

### 8.安装Aria2插件和Kubespider Chrome插件
* 安装Aria2插件，参考：[link](https://github.com/opennaslab/kubespider/blob/main/README-CN.md#2%E8%BF%9E%E6%8E%A5aria2)
* 安装Kubespider Chrome插件，参考：[link](https://github.com/opennaslab/kubespider/blob/main/README-CN.md#3%E5%AE%89%E8%A3%85chrome%E6%8F%92%E4%BB%B6)

### 9.查看配置文件
通过右键编辑各配置文件(这里为默认配置文件，已开启基础下载功能)，`ctrl+s` 即可重载程序并运行：
<image src="./images/synology_edit_config.png" alt="kubespider" height="600px">

## 测试
现在，打开 [demo](https://www.meijutt.tv/content/meiju28502.html) ，右键选择 `Send to Kubespider`:  
<image src="./images/synology_demo.png" alt="kubespider" height="600px">

现在查看Aria2插件，即可看见触发下载的任务：  
<image src="./images/synology_demo_result.png" alt="kubespider" height="400px">  

这里只给最简单下载演示，更多下载场景，请看项目 [README](https://github.com/opennaslab/kubespider/blob/main/README-CN.md#-%E7%89%B9%E6%80%A7%E5%88%97%E8%A1%A8)。