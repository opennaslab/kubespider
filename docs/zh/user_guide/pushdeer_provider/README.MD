# [pushdeer](https://github.com/easychen/pushdeer)

> ⚠️ 目前，官方架设的Android版本因接口权限停止无法使用，[详情请点击](https://github.com/easychen/pushdeer/issues/150)

PushDeer是一个可以自行架设的无APP推送服务，同时也为因为某些原因无法使用无APP推送方案的同学提供有APP/自制设备方案。

项目详情可以参考以下链接
[🐙🐱 GitHub仓库](https://github.com/easychen/pushdeer) [🔮 中国大陆镜像仓库@Gitee](https://gitee.com/easychen/pushdeer)

该项目已经实现的方案/端包括：

- 无APP方案：
  - 轻APP（APP Clip）
  - 快应用
- 有APP方案：
  - iOS客户端
  - Mac客户端
  - Android客户端
- 自制设备方案：
  - DeerESP（ESP8266/ESP32）
  
---

|登入|设备|Key|消息|设置|
|-|-|-|-|-|
|![](images/登入.png)|![](images/设备.png)|![](images/key.png)|![](images/消息.png)|![](images/设置.png)|


# 试用

![](images/video.gif)

## 使用官方在线版本

官方在线版不用自行架设服务器端，只需启动客户端即可

### iOS14+

![](images/clipcode.png)

苹果手机（iOS 14+）用系统摄像头扫描上边的码即可拉起轻应用。亦可在苹果商店搜索「PushDeer」安装。

> 注意：这里不要安装PushDeer自架版

### MacOS 11+

PushDeer有Mac客户端，亦支持推送。可在Mac应用商店中搜索「PushDeer」安装。

### Android

快应用尚在开发，可下载并安装Android测试版APP([GitHub](https://github.com/easychen/pushdeer/releases/tag/android1.0alpha)|[Gitee](https://gitee.com/easychen/pushdeer/releases/android1.0alpha))。


### 发送消息

1. 通过apple账号（或微信账号·仅Android版支持）登录
1. 切换到「设备」标签页，点击右上角的加号，注册当前设备
1. 切换到「Key」标签页，点击右上角的加号，创建一个Key
1. 通过访问后边的URL即可推送内容：https://api2.pushdeer.com/message/push?pushkey=key&text=要发送的内容

> 注意注册设备用到了device token，应用一旦重装，device token会变，所以需要重新注册一次。

### 发送实例

发送文字：

```
https://api2.pushdeer.com/message/push?pushkey=key&text=要发送的内容
```

发送图片：

```
https://api2.pushdeer.com/message/push?pushkey=<key>&text=<图片URL>&type=image
```

发送Markdown：

```
https://api2.pushdeer.com/message/push?pushkey=<key>&text=标题&desp=<markdown>&type=markdown
```

### 将 PushDeer 接入 Kubespider 

将 PushDeer 作为消息推送 provider 接入 Kubespider：

```yaml
pushdeer:
  type: pushdeer_provider
  enable: true
  host: https://api2.pushdeer.com
  push_keys: [
    "your push keys",
  ]
```
这里包含4个配置属性：
* `type`: 消息通知提供器的类型。
* `enable`: 消息通知提供器是否启用，true表示启用，false表示禁用。
* `host`: 服务器地址。
* `push_keys`: 列表格式,key为需要接受通知的对象的密钥,支持多人发送。

## 使用自架服务器端和自架版客户端

### 自架服务器端
参考pushdeer官方文档

# Pushdeer 授权

Pushdeer项目禁止商用（包括但不限于搭建后挂广告或售卖会员、打包后上架商店销售等），在非商用的情况下遵循GPL v2，当两者冲突时，以非商用原则优先。
