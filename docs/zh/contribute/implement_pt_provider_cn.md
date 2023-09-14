# 编写pt提供器

## 开始之前

pt provider 是用来适配不同框架类型的pt网站,并且实现相对应的种子发现,择优做种等功能

## 接口描述

对于一个某一个框架类型的pt提供器，需要实现如下接口：

```python
class PTProvider(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, config_reader: AbsConfigReader) -> None:
        pass

    @abc.abstractmethod
    def get_pt_user(self) -> PTUser:
        # name of source provider defined in config
        pass

    @abc.abstractmethod
    def get_provider_name(self) -> str:
        # name of source provider defined in config
        pass

    @abc.abstractmethod
    def provider_enabled(self) -> bool:
        pass

    @abc.abstractmethod
    def get_torrents(self) -> list:
        # links list, return in following format
        #  list of Torrent
        pass

    @abc.abstractmethod
    def filter_torrents_for_deletion(self, torrents) -> list:
        # Obtain the torrents to be deleted
        pass

    @abc.abstractmethod
    def filter_torrents_for_download(self, torrents) -> list:
        pass

    @abc.abstractmethod
    def go_attendance(self) -> None:
        # listen type of provider, disposable or periodly
        pass

    @abc.abstractmethod
    def get_download_provider(self) -> str:
        pass

    @abc.abstractmethod
    def get_cost_sum_size(self) -> float:
        pass

    @abc.abstractmethod
    def get_max_sum_size(self) -> float:
        pass

    @abc.abstractmethod
    def get_keeping_time(self) -> int:
        pass
```

* `__init__`: 资源提供器初始化函数，初始化一些必要状态。
* `get_provider_name`: 获取资源提供器名称。
* `get_download_provider`: 获取下载器。
* `get_file_type`: 获取资源提供器下载的文件类型，可为magnet, torrent获取其他通用类型。
* `provider_enabled`: 获取资源提供器是否启用，从配置文件中获取。
* `get_pt_user`: 获取pt用户。
* `go_attendance`: 签到。
* `get_torrents`: 从pt网站中获取种子。
* `filter_torrents_for_deletion`: 过滤出需要删除的种子。
* `filter_torrents_for_download`: 过滤出需要下载的种子。
* `get_cost_sum_size`: 获取已经占用的空间。
* `get_max_sum_size`: 获取最大可占用空间。

```python
class PTUser(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    @property
    def data(self) -> dict:
        # user info
        pass

    @abc.abstractmethod
    def __repr__(self) -> str:
        pass
```

* `__repr__`: 用户描述。
* `data`: 用户相关信息。

```python
class Torrent(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self):
        self.id = None  # Unique identification of torrent

    @property
    @abc.abstractmethod
    def data(self) -> dict:
        # torrent attributes
        pass

    @abc.abstractmethod
    def __add__(self, other):
        # This method is used to define how to merge the attributes of torrent
        pass

    @classmethod
    @abc.abstractmethod
    def merge_torrents(cls, torrents: list) -> list:
        # This method is used to merge torrent attributes with the same identifier from different sources
        pass
```

* `__init__`: 种子的初始化函数，初始化一些必要信息。
* `__add__`: 种子相加合并的方法实现,用来合并多个具有不同属性的同一个种子。
* `merge_torrents`: 多个种子合并去重。
* `data`: data相关信息。

在实现如上函数后，还需要在`kubespider/core/config_handler.py`中初始化对应provider，如下：

```python
pt_provider_init_func = {
    'nexusphp_pt_provider': nexusphp_pt_provider.NexuPHPPTProvider,
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