# 编写消息通知提供器

## 开始之前

Kubespider为了适配多种类型的消息通知，抽象了一套API接口，按照Kubespider定义的规则实现这些API接口，即可实现多种方式的消息推送。

## 接口描述

对于一个消息通知提供器，需要实现如下接口：

```python
class NotificationProvider(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __init__(self, name: str, config_reader: AbsConfigReader) -> None:
        self.name = name
        self.config_reader = config_reader

    @abc.abstractmethod
    def push(self, *args, **kwargs) -> bool:
        # push message
        pass

    @abc.abstractmethod
    def get_provider_name(self) -> str:
        # name of notifications provider
        pass

    @abc.abstractmethod
    def provider_enabled(self) -> bool:
        pass

    @abc.abstractmethod
    def format_message(self, title, **kwargs) -> str:
        pass

```

* `__init__`: 资源提供器初始化函数，初始化一些必要状态。
* `get_provider_name`: 获取消息通知提供器名称。
* `provider_enabled`: 获取消息通知提供器是否启用，从配置文件中获取。
* `push`: 消息推送的方法。
* `format_message`: 对需要发送的消息进行格式化。

在实现如上函数后，还需要在`kubespider/core/config_handler.py`中初始化对应provider，如下：

```python
notification_provider_init_func = {
    'pushdeer_notification_provider': pushdeer_notification_provider.PushDeerNotificationProvider,
}
```

## 测试

在代码写好后，直接运行如下命令打包镜像并运行即可(在此repo的根目录运行)：

```sh
docker build -t cesign/kubespider:latest -f Dockerfile ./

docker rm kubespider --force

docker run -itd --name kubespider \
    -v ${HOME}/kubespider/.config:/app/.config \
    --network=host \
    --restart unless-stopped \
    cesign/kubespider:latest
```

然后执行你期待的操作，检查是否如期运行。