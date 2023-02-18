# 编写资源提供器

## 开始之前
Kubespider为了适配各种资源网站，抽象了一套API接口，按照Kubespider定义的规则实现这些API接口，即可实现多种方式的特定资源下载。

## 接口描述
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
* `__init__`: 资源提供器初始化函数，初始化一些必要状态。
* `get_provider_name`: 获取资源提供器名称。
* `get_provider_type`: 获取资源提供器类型，只能为`SOURCE_PROVIDER_PERIOD_TYPE`或者`SOURCE_PROVIDER_DISPOSABLE_TYPE`, 分别表示周期性资源提供器和一次性资源提供器，周期提供器可用于追剧等下载操作，一次性提供器用于webhook触发等下载操作。
* `get_file_type`: 获取资源提供器下载的文件类型，可为magnet, torrent获取其他通用类型。
* `get_download_path`: 获取资源提供器下载的文件存放路径，一般是每个提供一一个目录。
* `provider_enabled`: 获取资源提供器是否启用，从配置文件中获取。
* `is_webhook_enable`: webhook是否启用，在provider type为`SOURCE_PROVIDER_DISPOSABLE_TYPE`时，此接口必需返回true。
* `should_handle`: 判断是否需要处理当前url，如果需要处理，返回true，否则返回false，在provider type为* `SOURCE_PROVIDER_DISPOSABLE_TYPE`时，此接口必需检查资源是否由此provider处理。
* `get_links`: 获取此链接下的所有资源下载链接，如给一个博主地址，获取所有适配下载地址。
* `update_config`: 更新资源提供器配置信息，在webhook ebable时，此接口可用于更新配置文件，如接受美剧地址，刷写地址到配置文件，然后周期下载更新剧集。
* `load_config`: 获取资源提供器配置信息。

在实现如上函数后，还需要在`kubespider/core/kubespider_global.py`中初始化对应provider，如下：
```python
source_providers = [
    mikanani_source_provider.MikananiSourceProvider(),
    btbtt12_disposable_source_provider.Btbtt12DisposableSourceProvider(),
    meijutt_source_provider.MeijuttSourceProvider(),
]
```

## 示例
这里以meijutt作为示例，实现一个资源提供器。meijutt资源提供器旨在接收webhook触发（接收喜欢的美剧地址URL），实现自动追剧。
### 1.配置定义
```cfg
[meijutt_source_provider]
ENABLE=true
DOWNLOAD_PATH=meijutt
TV_LINKS=
```
这里包含3个配置属性：
* `ENABLE`: 资源提供器是否启用，true表示启用，false表示禁用。
* `DOWNLOAD_PATH`: 资源提供器下载的文件存放路径，一般是每个提供一一个目录。
* `TV_LINKS`: 美剧地址，多个地址用逗号分隔，在收到美剧地址URL时，会通过函数`update_config`追加URL。


### 2.函数解释
```python
class MeijuttSourceProvider(provider.SourceProvider):
    def __init__(self) -> None:
        self.provider_type = types.SOURCE_PROVIDER_PERIOD_TYPE
        self.file_type = 'magnet'
        self.webhook_enable = True
        self.provider_name = 'meijutt_source_provider'
        self.download_path = ''
        self.tv_links = []

    def get_provider_name(self):
        return self.provider_name

    def get_provider_type(self):
        return self.provider_type

    def get_file_type(self):
        return self.file_type

    def get_download_path(self):
        return self.download_path

    def provider_enabled(self):
        cfg = provider.load_source_provide_config(self.provider_name)
        return cfg['ENABLE'] == 'true'

    def is_webhook_enable(self):
        return True

    def should_handle(self, data_source_url: str):
        parse_url = urlparse(data_source_url)
        if parse_url.hostname == 'www.meijutt.tv' and 'content' in parse_url.path:
            logging.info('%s belongs to MeijuttSourceProvider', data_source_url)
            return True
        return False

    def get_links(self, data_source_url: str):
        ret = []
        for tv_link in self.tv_links:
            if len(tv_link) == 0:
                continue
            try:
                req = requests.get(tv_link, timeout=30)
            except Exception as err:
                logging.info('meijutt_source_provider get links error:%s', err)
                continue
            dom = BeautifulSoup(req.content, 'html.parser')
            div = dom.find_all("div", ['class', 'tabs-list current-tab'])
            if len(div) == 0:
                continue
            links = div[0].find_all('input', ['class', 'down_url'])
            for link in links:
                url = link.get('value')
                logging.info('meijutt find %s', url)
                ret.append(url)
        return ret

    def update_config(self, req_para: str):
        cfg = provider.load_source_provide_config(self.provider_name)
        links = cfg['TV_LINKS']
        links = str.split(links, ',')
        if req_para not in links:
            links.append(req_para)
        links = ','.join(links)
        cfg['TV_LINKS'] = links
        provider.save_source_provider_config(self.provider_name, cfg)

    def load_config(self):
        cfg = provider.load_source_provide_config(self.provider_name)
        logging.info('meijutt tv link is:%s', cfg['TV_LINKS'])
        self.tv_links = str.split(cfg['TV_LINKS'], ',')
        self.download_path = cfg['DOWNLOAD_PATH']
```

* `__init__`: 初始化函数，包含provider类型，文件类型，是否支持webhook，资源提供器名称，下载路径，美剧地址。注意：
  * 文件类型目前只支持magnet，torrent，general。
  * meijutt资源提供器接受webhook触发，所以`webhook_enable`设置为true。
  * meijutt资源提供器会周期检查美剧是否更新，所以provider类型为`SOURCE_PROVIDER_PERIOD_TYPE`。
  * 其中provider name必需合配置文件中的provider name一致。
* `get_provider_name`: 直接返回此provider的name即可。
* `get_provider_type`: 此provider为周期下载类型，所以返回`SOURCE_PROVIDER_PERIOD_TYPE`。
* `get_file_type`: 返回此provider的下载文件类型。
* `get_download_path`: 返回下载文件夹地址。
* `provider_enabled`: 读取配置文件，返回此provider是否开启。
* `is_webhook_enable`: 此provider需要接收webhook触发，所以返回true。
* `should_handle`: 判断请求的url是否为www.meijutt.tv，如果是则调用此provider处理。
* `get_links`: 获取所有文件的下载链接。
* `update_config`: 在webhook开启情况下，如果请求的url通过`should_handle`检查，则会调用此函数把美剧地址存如provider config文件。
* `load_config`: 读取配置文件函数。

最后，在`kubespider/core/kubespider_global.py`中初始化meijutt provider，如下：
```python
source_providers = [
    mikanani_source_provider.MikananiSourceProvider(),
    btbtt12_disposable_source_provider.Btbtt12DisposableSourceProvider(),
    meijutt_source_provider.MeijuttSourceProvider(),
]
```

## 测试
在代码写好后，直接运行如下命令打包镜像并运行即可(在此repo的根目录运行)：
```sh
docker build -t cesign/kubespider:latest -f Dockerfile ./

docker rm kubespider --force

docker run -itd --name kubespider \
    -v ${HOME}/kubespider/.config:/root/.config \
    --network=host \
    --restart unless-stopped \
    cesign/kubespider:latest
```
然后执行你期待的操作，检查是否如期运行。