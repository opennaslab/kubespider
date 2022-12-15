# 编写资源提供器

## 开始之前
Kubespider为了适配各种资源网站，抽象了一套API接口，按照Kubespider定义的规则实现这些API接口，即可实现多种方式的特定资源下载。

## 接口描述
TBD
对于一个资源网站的资源提供器，需要实现如下接口：
```python
class SourceProvider(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self) -> None:
        pass
    
    @abc.abstractmethod
    def get_provider_name(self):
        pass 

    @abc.abstractmethod
    def get_provider_type(self):
        pass

    @abc.abstractmethod
    def get_file_type(self):
        pass

    @abc.abstractmethod
    def get_download_path(self):
        pass

    @abc.abstractmethod
    def provider_enabled(self):
        pass

    @abc.abstractmethod
    def is_webhook_enable(self):
        pass

    @abc.abstractmethod
    def should_handle(self, dataSourceUrl):
        pass
    
    @abc.abstractmethod
    def get_links(self, dataSourceUrl):
        pass

    @abc.abstractmethod
    def update_config(self, reqPara):
        pass

    @abc.abstractmethod
    def load_config(self):
        pass
```
`__init__`: 资源提供器初始化函数，初始化一些必要状态。

## 示例

## 测试
TBD