# 如何设计开发kubespider插件

## 简介

为了拓展资源发现的功能,我们对原[SourceProvider]的功能进行了拆解,设计出了plugin
plugin支持三种基础的动作: 资源解析,资源搜索,周期调度
plugin支持多种语言的开发

## 插件基础功能介绍

#### 解析

提供解析功能,对用户触发的链接进行解析,获取页面中的资源

#### 搜索

根据用户提供的关键词进行搜索,获取资源内容

#### 周期调度

提供周期调度的功能,由kubespider进行调度

## 插件类型

根据插件提供的功能,插件可以分为三种类型

- 解析: parser
- 搜索: search
- 调度: scheduler

## 插件组成

插件由四个部分组成:

- sdk: kubespider提供的不同语言sdk,内部包含了一些基础功能以及工具
- provider.yaml: provider.yaml用来对插件进行定义描述
- provider: provider用来实现插件的基础功能
- bin/provider: 编译过后的二进制provider,提供给kubespider执行

## 插件如何与kubespider交互

插件开发完成之后通过kubespider提供的api接口导入kubespider[导入api]
启用导入之后的插件[启用api]
kubespider通过命令行拉起插件,插件开始启动
插件sdk内提供了httpserver,当插件启动之后,kubespider可通过api接口和插件进行通信
kubespider 通过 _heath api来检查插件是否正常启动
资源解析:
- kubespider 通过 should_handle api来检查当前链接是否可以交给插件解析
- kubespider 通过 get_links api来调用插件解析链接获取资源
搜索:
- kubespider 通过 search api来调用插件搜索资源
调度:
- kubespider 通过 scheduler api来周期调用插件进行资源发现

## 插件开发

这里以Python语言为例,介绍provider如何开发
针对插件的三种基础功能,Python sdk 提供了三个对应的类:

```python 解析类
class ParserProvider:
    TYPE = "parser"
    API_LIST = ["get_links", "should_handle"]

    @staticmethod
    def get_links(source: str, **kwargs):
        """Parse links to extract resources inside the links."""
        return []

    @staticmethod
    def should_handle(source: str, **kwargs):
        """Determine whether the current link can be parsed."""
        return False
```

```python 搜索类
class SearchProvider(ParserProvider):
    TYPE = "search"
    API_LIST = ["get_links", "should_handle", "search"]

    @staticmethod
    def search(keyword: str, page=1, **kwargs):
        """
        Search resource by keyword and page
        per page defined by developer
        """
        return []
```

```python 调度类
class SchedulerProvider(SearchProvider):
    TYPE = "scheduler"
    API_LIST = ["get_links", "should_handle", "search", "scheduler"]

    @staticmethod
    def scheduler(auto_download_resource: bool, **kwargs):
        """
        Task scheduling, you can discover resources here, return resources,
        and also do other things you want to do at the moment.
        return: resource list
        """
        return []
```

三种类是逐步继承的一个关系
ParserProvider提供了 should_handle,get_links 两个api, 这个类对应了插件的解析功能
SearchProvider继承了ParserProvider,提供了should_handle,get_links,search 三个api, SearchProvider对应了插件的搜索以及解析两个功能
SchedulerProvider继承了SearchProvider,提供了should_handle,get_links,search,scheduler 四个api, 这个搜索类对应了插件的搜索,解析以及调度三个功能

所以:
当你需要开发一个解析插件的话,就继承ParserProvider,重写should_handle,get_links两个方法
当你需要开发一个搜索插件的话,就继承SearchProvider,重写should_handle,get_links,search三个方法
(补充:大部分搜索功能,搜索的列表页不包含资源的具体信息,得到的只是详情页地址,所以通过搜索功能获得资源之后还需要二次调用解析功能进行解析,
如果搜索页可以直接获取资源的话,则继承SearchProvider,重写search方法即可)
当你需要开发一个调度插件的话,就继承SchedulerProvider,重写should_handle,get_links,search,scheduler这四个方法即可
(补充:四个方法对应插件的三个功能,需要重写的方案根据实际情况来选择,如果只有调度功能且能直接获取资源,则重写scheduler即可,
如果只有调度功能,不能直接获取资源,则需要重写should_handle,get_links,scheduler,
如果包含了搜索,调度功能,则除了重写scheduler方法之外,还需要实现搜索对应的方法)

参考 [demo]

## 插件编译


免责申明:
由于最终代码是通过编译之后交给kubespider运行,所以kubespider无法控制编译之后的插件执行内容,开发者尽量提供源码供用户自行编译,如直接提供编译的二进制,
kubespider不对任何可能产生的后果负责
用户在使用插件时,尽量自行阅读源码,编译插件.如没有相关能力,在使用编译好的二进制插件时,选择可信的插件来源,不要使用未知来源的插件