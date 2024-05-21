# notification

## 简介

kubespider内置了一些消息通知器,通过配置这些消息通知器,当事件发生时,可以进行消息通知

## api

headers: {"Authorization":"bearer {your token}"}

### 查询消息通知定义 /api/v2/notification [GET]

```json response
{
  "code": 200,
  "data": [
    {
      "arguments": {
        "device_token": {
          "default": null,
          "description": "bark`s device token",
          "required": true,
          "type": "text"
        },
        "host": {
          "default": null,
          "description": "bark`s host",
          "required": true,
          "type": "text"
        },
        "name": {
          "default": null,
          "description": "unique instance name",
          "required": true,
          "type": "text"
        }
      },
      "author": "",
      "binary": "",
      "description": "bark notification",
      "language": "",
      "logo": "",
      "name": "",
      "type": "BarkNotificationProvider",
      "version": ""
    },
    {
      "arguments": {
        "host": {
          "default": null,
          "description": "pushdeer`s host",
          "required": true,
          "type": "text"
        },
        "name": {
          "default": null,
          "description": "unique instance name",
          "required": true,
          "type": "text"
        },
        "push_keys": {
          "default": null,
          "description": "pushdeer`s push key",
          "items": {
            "default": null,
            "description": "",
            "required": false,
            "type": "text"
          },
          "required": true,
          "type": "array"
        }
      },
      "author": "",
      "binary": "",
      "description": "An open-source notification tool pushDeer",
      "language": "",
      "logo": "",
      "name": "",
      "type": "PushdeerNotificationProvider",
      "version": ""
    },
    {
      "arguments": {
        "access_token": {
          "default": null,
          "description": "access_token",
          "required": true,
          "type": "text"
        },
        "host": {
          "default": null,
          "description": "host",
          "required": true,
          "type": "text"
        },
        "name": {
          "default": null,
          "description": "unique instance name",
          "required": true,
          "type": "text"
        },
        "target_qq": {
          "default": null,
          "description": "target_qq",
          "required": true,
          "type": "text"
        }
      },
      "author": "",
      "binary": "",
      "description": "QQ notification",
      "language": "",
      "logo": "",
      "name": "",
      "type": "QQNotificationProvider",
      "version": ""
    },
    {
      "arguments": {
        "bot_token": {
          "default": null,
          "description": "bot token",
          "required": true,
          "type": "text"
        },
        "channel_chat_id": {
          "default": null,
          "description": "channel id",
          "required": false,
          "type": "text"
        },
        "channel_name": {
          "default": null,
          "description": "channel name",
          "required": true,
          "type": "text"
        },
        "name": {
          "default": null,
          "description": "unique instance name",
          "required": true,
          "type": "text"
        }
      },
      "author": "",
      "binary": "",
      "description": "Telegram channel notification tool",
      "language": "",
      "logo": "",
      "name": "",
      "type": "TelegramNotificationProvider",
      "version": ""
    },
    {
      "arguments": {
        "host": {
          "default": null,
          "description": "SynologyChat`s host",
          "required": true,
          "type": "text"
        },
        "name": {
          "default": null,
          "description": "unique instance name",
          "required": true,
          "type": "text"
        },
        "token": {
          "default": null,
          "description": "bot`s token",
          "required": true,
          "type": "text"
        }
      },
      "author": "",
      "binary": "",
      "description": "Synology Chat",
      "language": "",
      "logo": "",
      "name": "",
      "type": "SynologyNotificationProvider",
      "version": ""
    }
  ],
  "msg": "Ok"
}
```

### 查询消息通知配置 /api/v2/notification/configs [GET]

```json
{
  "code": 200,
  "data": {
    "bark": {
      "device_token": 12345678,
      "enable": false,
      "host": "https://api.day.app",
      "id": 4,
      "is_alive": false,
      "name": "bark",
      "type": "BarkNotificationProvider"
    },
    "pushdeer": {
      "enable": false,
      "host": "https://api2.pushdeer.com",
      "id": 1,
      "is_alive": false,
      "name": "pushdeer",
      "push_keys": [
        "dddd",
        "wdw"
      ],
      "type": "PushdeerNotificationProvider"
    },
    "qq": {
      "accessToken": null,
      "enable": false,
      "host": "http://127.0.0.1:5700",
      "id": 3,
      "is_alive": false,
      "name": "qq",
      "target_qq": 12345678,
      "type": "QqNotificationProvider"
    },
    "telegram": {
      "bot_token": "233",
      "channel_chat_id": -233,
      "channel_name": "push_test",
      "enable": true,
      "id": 2,
      "is_alive": false,
      "name": "telegram",
      "type": "TelegramNotificationProvider"
    }
  },
  "msg": "Ok"
}
```

### 创建/修改消息通知配置 /api/v2/notification/configs [POST]

新建配置

```json
{
  "bot_token": "your bot token",
  "channel_chat_id": null,
  "channel_name": "kubespider",
  "enable": false,
  "host": "https://api.telegram.org",
  "type": "TelegramNotificationProvider",
  "name": "telegram1"
}
```

修改配置

```json
{
  "bot_token": "xxx",
  "channel_chat_id": null,
  "channel_name": "kubespider",
  "enable": false,
  "host": "https://api.telegram.org",
  "type": "TelegramNotificationProvider",
  "name": "telegram1",
  "id": 7
}
```

```json
{
  "code": 200,
  "data": null,
  "msg": "Ok"
}
```

### 删除消息通知配置 /api/v2/notification/<config_id> [DELETE]

```json
{
  "code": 200,
  "data": null,
  "msg": "Ok"
}
```

### 发送消息 /api/v2/notification/send_message [POST]

消息体,title必传,其余字段作为消息发送

```json
{
  "title": "test",
  "msg": "this is a test message"
}
```

```json
{
  "code": 200,
  "data": null,
  "msg": "Ok"
}
```