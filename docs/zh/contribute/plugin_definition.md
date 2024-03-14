# Plugin插件定义

kubespider使用不同的Plugin解析不同资源网站，调用不同下载软件触发资源下载，开发者可以根据自己的场景开发出合适的Plugin，如解析YoutuBe channel的Plugin，实现自动下载最新的channel内容，如下将对如何定义Plugin做详细描述。


## Plugin模板定义

kubespider使用yaml定义Plugin模板，前端将使用此模板在前端渲染对应的插件内容，首先我们看一个整体Demo：
```
name: majic-source
version: 1.0.0
author: opennaslab
type: parser
description: This is a magic source parser to parse different resource websites
language: python
logo: https://via.placeholder.com/200
binary: https://raw.githubusercontent.com/qingchoulove/ks_provider_example/main/example_provider
arguments:
  handle_host:
    type: text
    description: Configuration options
    required: true
    default: ""
  link_selector: 
    type: text
    description: Configuration options
    required: true
    default: ""
```

其中，除开arguments，都为非常简单的 `key: value` 的Plugin描述信息，描述此插件的作者和版本等信息，其中比较关键的是 `binary` 参数，kubespider会动态去此地址下载二进制并拉起进程，用于解析资源。

### arguments定义

kubespider会使用 `arguments` 定义渲染前端插件配置表格，这里对 `arguments` 的各种类型做详细格式描述。

#### text类型

```yaml
handle_host: 
  type: text
  description: Configuration options
  required: true
  default: ""
```

#### integer类型

```yaml
host_port: 
  type: integer
  description: Configuration options
  required: true
  default: ""
```

#### boolean类型

```yaml
enable_autodownload: 
  type: boolean
  description: Configuration options
  required: true
  default: true
```

#### array类型
##### 元素为object类型
```yaml
checking_websites: 
  type: array
  description: Configuration options
  required: false
  default: nil
  items:
    type: object
    properties:
      website: 
        type: text
        description: Configuration options
        required: true
        default: ""
      use_proxy:
        type: boolean
        description: Configuration options
        required: true
        default: false
```

##### 元素为简单类型
```yaml
checking_websites:
  type: array
  description: Configuration options
  required: false
  default: nil
  items:
    type: text
```

#### object类型

```yaml
checking_websites:
  type: object
  description: Configuration options
  required: true
  default: nil
  properties:
    website: 
      type: text
      description: Configuration options
      required: true
      default: ""
    use_proxy:
      type: boolean
      description: Configuration options
      required: true
      default: false
```

## Plugin二进制开发

TBD