# binding

## 简介

plugin提供了资源解析的动作,但动作的调用需要一些必要的配置信息,binding提供配置信息,并绑定到plugin使用

## api

### 查询binding配置 /api/v2/binding [GET]

```json
{
  "code": 200,
  "data": [
    {
      "arguments": {
        "cookie": "",
        "host": "https://kp.xxx.cc",
        "parser": {},
        "scheduler": {
          "base_info": true,
          "mail_read": true
        },
        "search": {
          "mode": "normal"
        },
        "use_proxy": false
      },
      "id": 1,
      "name": "mt",
      "plugin_name": "M-Team",
      "type": "scheduler"
    }
  ],
  "msg": "Ok"
}
```

### 创建/更新binding配置 /api/v2/binding [POST]

创建

```json
{
  "cookie": "",
  "host": "https://kp.xx.cc",
  "use_proxy": false,
  "parser": {},
  "scheduler": {
    "base_info": true,
    "mail_read": true
  },
  "search": {
    "mode": "normal"
  },
  "name": "mt",
  "type": "scheduler",
  "plugin_name": "M-Team"
}
```

更新

```json
{
  "cookie": "",
  "host": "https://kp.xx.cc",
  "use_proxy": false,
  "parser": {},
  "scheduler": {
    "base_info": true,
    "mail_read": true
  },
  "search": {
    "mode": "normal"
  },
  "name": "mt",
  "type": "scheduler",
  "plugin_name": "M-Team",
  "id": 1
}
```

```json
{
  "code": 200,
  "data": null,
  "msg": "Ok"
}
```

### 删除binding配置 /api/v2/binding/<binding_id> [DELETE]

```json
{
  "code": 200,
  "data": null,
  "msg": "Ok"
}
```
