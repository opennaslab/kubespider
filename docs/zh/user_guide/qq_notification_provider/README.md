# [QQ(go-cqhttp)](https://github.com/Mrs4s/go-cqhttp)

> 目前仅支持go-cqhttp的HTTP接口

go-cqhttp是一个自建的QQ机器人服务，其工作方式如Telegram类似，提供了消息推送接口

### 创建CQHTTP机器人

- 创建一个QQ账号
- 根据[官方文档](https://docs.go-cqhttp.org/guide/quick_start.html#%E5%9F%BA%E7%A1%80%E6%95%99%E7%A8%8B)，下载并配置QQ机器人
- v1.1.0版本需要自建SignServer，请参考[该issue](https://github.com/Mrs4s/go-cqhttp/issues/2242)
    - 使用该SignServer需要使用安卓协议，建议使用aPad协议登陆
- 在启动前，务必开启GOCQHTTP的HTTP服务

### 将CQHTTP接入Kubespider

修改配置文件目录中的`notifiaction_provider.yaml`，修改以下内容

```yaml
qq:
  type: qq_notification_provider
  target_qq: your qq account
  accessToken: cqhttp config
  host: cqhttp address
  enable: True
```
* `target_qq`: 需要收到推送信息的账号
* `accessToken`: 在配置CQHTTP的HTTP服务时的设置项
* `host`: CQHTTP的HTTP服务所在地址，如http://127.0.0.1:5700
