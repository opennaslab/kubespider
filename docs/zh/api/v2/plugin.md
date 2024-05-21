# plugin

## 简介

为了支持多种语言的资源解析动作,我们把SourceProvider做了拆分,设计出了plugin.
了解plugin的概念以及如何开发[点击这里]

## api

headers: {"Authorization":"bearer {your token}"}

### 查询plugin插件 /api/v2/plugin [GET]

```json response
{
  "code": 200,
  "data": [
    {
      "arguments": {
        "cookie": {
          "default": null,
          "description": "M-Team`s cookie",
          "required": true,
          "type": "text"
        },
        "host": {
          "default": null,
          "description": "M-Team`s host",
          "required": true,
          "type": "text"
        },
        "parser": {
          "default": null,
          "description": "M-Team parser configration",
          "required": false,
          "type": "object"
        },
        "scheduler": {
          "default": null,
          "description": "M-Team scheduler configration",
          "properties": {
            "base_info": {
              "default": true,
              "description": "推送用户基础信息",
              "required": false,
              "type": "boolean"
            },
            "mail_read": {
              "default": true,
              "description": "读取邮件信息推送",
              "required": false,
              "type": "boolean"
            }
          },
          "required": false,
          "type": "object"
        },
        "search": {
          "default": null,
          "description": "M-Team search configration",
          "properties": {
            "mode": {
              "default": "",
              "description": "搜索类型",
              "required": true,
              "type": "text"
            }
          },
          "required": false,
          "type": "object"
        },
        "use_proxy": {
          "default": false,
          "description": "weather use proxy, if proxy configration",
          "required": false,
          "type": "boolean"
        }
      },
      "author": "evell",
      "binary": "https://raw.githubusercontent.com/evell1992/kubespider_plugin/main/mt/bin/provider",
      "description": "M-Team Private Tracker Provider",
      "language": "python",
      "logo": "https://raw.githubusercontent.com/evell1992/kubespider_plugin/main/mt/logo.png",
      "name": "M-Team",
      "type": "scheduler",
      "up": true,
      "version": "1.0.0"
    }
  ],
  "msg": "Ok"
}
```

### 启用/禁用plugin插件 /api/v2/plugin/<plugin_name> [PUT]

```json request
{
    "enable":true,
    "name":"M-Team"
}
```

```json response
{
  "code": 200,
  "data": null,
  "msg": "Ok"
}
```

### 注册远端插件 /api/v2/plugin/register/remote [POST]

```json request
{
  "definition": "https://raw.githubusercontent.com/evell1992/kubespider_plugin/main/mt/provider.yaml"
}
```

```json response
{
  "code": 200,
  "data": null,
  "msg": "Ok"
}
```

### 注册本地插件 /api/v2/plugin/register/local [POST]

```formdata request
definition: <yarm file>
binary: <binary file>
```

```json response
{
  "code": 200,
  "data": null,
  "msg": "Ok"
}
```

### 删除plugin插件 /api/v2/plugin/<plugin_name> [DELETE]

```json response
{
  "code": 200,
  "data": null,
  "msg": "Ok"
}
```
