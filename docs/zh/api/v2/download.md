# download

## 简介

kubespider内置了一些下载器,通过配置这些下载器可以提供资源下载的能力

## api

headers: {"Authorization":"bearer {your token}"}

### 查询下载器定义 /api/v2/download [GET]

```json
{
  "code": 200,
  "data": [
    {
      "arguments": {
        "download_base_path": {
          "default": null,
          "description": "download base path",
          "required": false,
          "type": "text"
        },
        "name": {
          "default": null,
          "description": "unique instance name",
          "required": true,
          "type": "text"
        },
        "priority": {
          "default": null,
          "description": "download priority",
          "required": false,
          "type": "integer"
        },
        "rpc_endpoint_host": {
          "default": null,
          "description": "RPC endpoint host",
          "required": true,
          "type": "text"
        },
        "rpc_endpoint_port": {
          "default": null,
          "description": "RPC endpoint port",
          "required": true,
          "type": "integer"
        },
        "secret": {
          "default": null,
          "description": "RPC secret",
          "required": true,
          "type": "text"
        }
      },
      "author": "",
      "binary": "",
      "description": "aria2 is a lightweight, multi-protocol, and multi-source command-line download utility. It supports protocols\nsuch as HTTP, HTTPS, FTP, BitTorrent, and more. With features like resumable downloads and multiple connections,\naria2 maximizes the utilization of network resources to enhance download speeds.",
      "language": "",
      "logo": "",
      "name": "",
      "type": "Aria2DownloadProvider",
      "version": ""
    },
    {
      "arguments": {
        "download_base_path": {
          "default": null,
          "description": "download base path",
          "required": false,
          "type": "text"
        },
        "download_category": {
          "default": null,
          "description": "download category",
          "required": true,
          "type": "text"
        },
        "download_tags": {
          "default": null,
          "description": "download tags",
          "items": {
            "default": null,
            "description": "",
            "required": false,
            "type": "text"
          },
          "required": true,
          "type": "array"
        },
        "http_endpoint_host": {
          "default": null,
          "description": "http endpoint host",
          "required": true,
          "type": "text"
        },
        "http_endpoint_port": {
          "default": null,
          "description": "http endpoint port",
          "required": true,
          "type": "integer"
        },
        "name": {
          "default": null,
          "description": "unique instance name",
          "required": true,
          "type": "text"
        },
        "password": {
          "default": null,
          "description": "password",
          "required": true,
          "type": "text"
        },
        "priority": {
          "default": null,
          "description": "priority",
          "required": false,
          "type": "integer"
        },
        "use_auto_torrent_management": {
          "default": null,
          "description": "use auto torrent management",
          "required": false,
          "type": "boolean"
        },
        "username": {
          "default": null,
          "description": "username",
          "required": true,
          "type": "text"
        },
        "verify_webui_certificate": {
          "default": null,
          "description": "verify webui certificate",
          "required": true,
          "type": "boolean"
        }
      },
      "author": "",
      "binary": "",
      "description": "Qbittorrent downloader",
      "language": "",
      "logo": "",
      "name": "",
      "type": "QbittorrentDownloadProvider",
      "version": ""
    },
    {
      "arguments": {
        "cookie": {
          "default": null,
          "description": "cookie",
          "required": false,
          "type": "text"
        },
        "http_endpoint_host": {
          "default": null,
          "description": "http endpoint host",
          "required": false,
          "type": "text"
        },
        "http_endpoint_port": {
          "default": null,
          "description": "http endpoint port",
          "required": false,
          "type": "integer"
        },
        "name": {
          "default": null,
          "description": "unique instance name",
          "required": true,
          "type": "text"
        },
        "priority": {
          "default": null,
          "description": "priority",
          "required": false,
          "type": "integer"
        },
        "use_proxy": {
          "default": null,
          "description": "whether you use proxy",
          "required": false,
          "type": "boolean"
        }
      },
      "author": "",
      "binary": "",
      "description": "Tiktok downloader",
      "language": "",
      "logo": "",
      "name": "",
      "type": "TiktokDownloadProvider",
      "version": ""
    },
    {
      "arguments": {
        "download_base_path": {
          "default": null,
          "description": "download base path",
          "required": false,
          "type": "text"
        },
        "http_endpoint": {
          "default": null,
          "description": "http endpoint host",
          "required": true,
          "type": "text"
        },
        "name": {
          "default": null,
          "description": "unique instance name",
          "required": true,
          "type": "text"
        },
        "password": {
          "default": null,
          "description": "password",
          "required": false,
          "type": "text"
        },
        "priority": {
          "default": null,
          "description": "priority",
          "required": false,
          "type": "integer"
        },
        "username": {
          "default": null,
          "description": "username",
          "required": false,
          "type": "text"
        }
      },
      "author": "",
      "binary": "",
      "description": "Transmission is a fast, easy, and free BitTorrent client.",
      "language": "",
      "logo": "",
      "name": "",
      "type": "TransmissionProvider",
      "version": ""
    },
    {
      "arguments": {
        "device_id": {
          "default": null,
          "description": "device_id",
          "required": false,
          "type": "text"
        },
        "http_endpoint": {
          "default": null,
          "description": "http endpoint host",
          "required": false,
          "type": "text"
        },
        "name": {
          "default": null,
          "description": "unique instance name",
          "required": true,
          "type": "text"
        },
        "priority": {
          "default": null,
          "description": "priority",
          "required": false,
          "type": "integer"
        },
        "token_js_path": {
          "default": null,
          "description": "token js path",
          "required": false,
          "type": "text"
        },
        "use_proxy": {
          "default": null,
          "description": "whether you use proxy",
          "required": false,
          "type": "boolean"
        }
      },
      "author": "",
      "binary": "",
      "description": "Xunlei downloader",
      "language": "",
      "logo": "",
      "name": "",
      "type": "XunleiDownloadProvider",
      "version": ""
    },
    {
      "arguments": {
        "http_endpoint_host": {
          "default": null,
          "description": "http endpoint host",
          "required": true,
          "type": "text"
        },
        "http_endpoint_port": {
          "default": null,
          "description": "http endpoint port",
          "required": true,
          "type": "integer"
        },
        "name": {
          "default": null,
          "description": "unique instance name",
          "required": true,
          "type": "text"
        },
        "priority": {
          "default": null,
          "description": "priority",
          "required": false,
          "type": "integer"
        },
        "use_proxy": {
          "default": null,
          "description": "whether you use proxy",
          "required": false,
          "type": "boolean"
        }
      },
      "author": "",
      "binary": "",
      "description": "YouGet downloader",
      "language": "",
      "logo": "",
      "name": "",
      "type": "YougetDownloadProvider",
      "version": ""
    },
    {
      "arguments": {
        "auto_convert": {
          "default": null,
          "description": "auto convert",
          "required": false,
          "type": "boolean"
        },
        "download_proxy": {
          "default": null,
          "description": "download proxy",
          "required": false,
          "type": "text"
        },
        "handle_host": {
          "default": null,
          "description": "handle host",
          "items": {
            "default": null,
            "description": "",
            "required": false,
            "type": "text"
          },
          "required": false,
          "type": "array"
        },
        "http_endpoint_host": {
          "default": null,
          "description": "http endpoint host",
          "required": true,
          "type": "text"
        },
        "http_endpoint_port": {
          "default": null,
          "description": "http endpoint port",
          "required": true,
          "type": "integer"
        },
        "name": {
          "default": null,
          "description": "unique instance name",
          "required": true,
          "type": "text"
        },
        "priority": {
          "default": null,
          "description": "priority",
          "required": false,
          "type": "integer"
        },
        "target_format": {
          "default": null,
          "description": "target format",
          "required": false,
          "type": "text"
        },
        "use_proxy": {
          "default": null,
          "description": "whether you use proxy",
          "required": false,
          "type": "boolean"
        }
      },
      "author": "",
      "binary": "",
      "description": "YTDlp downloader",
      "language": "",
      "logo": "",
      "name": "",
      "type": "YTDlpDownloadProvider",
      "version": ""
    },
    {
      "arguments": {
        "http_endpoint_host": {
          "default": null,
          "description": "http endpoint host",
          "required": true,
          "type": "text"
        },
        "http_endpoint_port": {
          "default": null,
          "description": "http endpoint port",
          "required": true,
          "type": "integer"
        },
        "name": {
          "default": null,
          "description": "unique instance name",
          "required": true,
          "type": "text"
        },
        "priority": {
          "default": null,
          "description": "priority",
          "required": false,
          "type": "integer"
        },
        "use_proxy": {
          "default": null,
          "description": "whether you use proxy",
          "required": false,
          "type": "boolean"
        }
      },
      "author": "",
      "binary": "",
      "description": "Yutto downloader",
      "language": "",
      "logo": "",
      "name": "",
      "type": "YuttoDownloadProvider",
      "version": ""
    }
  ],
  "msg": "Ok"
}
```

### 查询下载器配置 /api/v2/download/configs [GET]

```json
{
  "code": 200,
  "data": {
    "aria2": {
      "download_base_path": "/downloads/",
      "enable": true,
      "id": 4,
      "is_alive": true,
      "name": "aria2",
      "priority": 2,
      "rpc_endpoint_host": "http://xxx.xxx.xxx",
      "rpc_endpoint_port": 6800,
      "secret": "xxx",
      "type": "Aria2DownloadProvider"
    },
    "qbittorrent": {
      "download_base_path": "/downloads/",
      "enable": false,
      "http_endpoint_host": "http://127.0.0.1",
      "http_endpoint_port": 8080,
      "id": 5,
      "is_alive": false,
      "name": "qbittorrent",
      "password": "adminadmin",
      "priority": 3,
      "tags": [
        "kubespider"
      ],
      "type": "QbittorrentDownloadProvider",
      "use_auto_torrent_management": false,
      "username": "admin",
      "verify_webui_certificate": false
    },
    "tiktok-dlp": {
      "cookie": null,
      "enable": false,
      "http_endpoint_host": "http://127.0.0.1",
      "http_endpoint_port": 3083,
      "id": 8,
      "is_alive": false,
      "name": "tiktok-dlp",
      "priority": 6,
      "type": "TiktokDownloadProvider"
    },
    "transmission": {
      "download_base_path": "/downloads/",
      "enable": false,
      "http_endpoint": "http://127.0.0.1:9091/transmission/rpc",
      "id": 7,
      "is_alive": false,
      "name": "transmission",
      "password": "admin",
      "priority": 5,
      "type": "TransmissionDownloadProvider",
      "username": "admin"
    },
    "xunlei": {
      "device_id": "xxx",
      "enable": false,
      "http_endpoint": "http://127.0.0.1:2345",
      "id": 6,
      "is_alive": false,
      "name": "xunlei",
      "priority": 4,
      "token_js_path": "/app/.config/dependencies/xunlei_download_provider/get_token.js",
      "type": "XunleiDownloadProvider"
    },
    "youget": {
      "enable": false,
      "http_endpoint_host": "http://127.0.0.1",
      "http_endpoint_port": 3081,
      "id": 2,
      "is_alive": false,
      "name": "youget",
      "priority": 1,
      "type": "YougetDownloadProvider"
    },
    "yt-dlp": {
      "auto_format_convet": false,
      "download_proxy": "http://192.168.1.8:1087",
      "enable": false,
      "handle_host": [
        "www.youtube.com",
        "youtube.com",
        "www.ted.com",
        "youtu.be",
        "m.youtube.com"
      ],
      "http_endpoint_host": "http://127.0.0.1",
      "http_endpoint_port": 3082,
      "id": 1,
      "is_alive": false,
      "name": "yt-dlp",
      "priority": 0,
      "target_format": "mp4",
      "type": "YtdlpDownloadProvider"
    },
    "yutto": {
      "enable": false,
      "http_endpoint_host": "http://127.0.0.1",
      "http_endpoint_port": 3084,
      "id": 3,
      "is_alive": false,
      "name": "yutto",
      "priority": 1,
      "type": "YuttoDownloadProvider"
    }
  },
  "msg": "Ok"
}
```

### 创建/修改下载器配置 /api/v2/download/configs [POST]

创建下载器配置

```json
{
  "download_base_path": "/downloads/",
  "enable": true,
  "is_alive": true,
  "name": "aria2",
  "priority": 2,
  "rpc_endpoint_host": "http://xxx.xxx.xxx",
  "rpc_endpoint_port": 6800,
  "secret": "xxx",
  "type": "Aria2DownloadProvider"
}
```

修改下载器配置

```json
{
  "download_base_path": "/downloads/",
  "enable": true,
  "id": 4,
  "is_alive": true,
  "name": "aria2",
  "priority": 2,
  "rpc_endpoint_host": "http://xxx.xxx.xxx",
  "rpc_endpoint_port": 6800,
  "secret": "xxx",
  "type": "Aria2DownloadProvider"
}
```

```json
{
  "code": 200,
  "data": null,
  "msg": "Ok"
}
```

### 删除下载器配置 /api/v2/download/<config_id> [DELETE]

```json
{
  "code": 200,
  "data": null,
  "msg": "Ok"
}
```

### 解析页面资源下载 /api/v2/download/from_url [POST]

```json
{
  "data_source": "http://www.baidu.com",
  "path": ""
}
```

```json
{
  "code": 200,
  "data": null,
  "msg": "Ok"
}
```

### 下载指定资源 /api/v2/download/from_resource [POST]

```json
{
  "url": "https://www.baidu.com",
  "path": "",
  "link_type": "",
  "file_type": "",
  "uid": "",
  "title": "",
  "subtitle": "",
  "desc": "",
  "poster": "",
  "size": "",
  "publish_time": "",
  "discover_time": "",
  "plugin": ""
}
```

```json
{
  "code": 200,
  "data": null,
  "msg": "Ok"
}
```