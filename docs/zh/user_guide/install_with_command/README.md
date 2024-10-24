# 使用docker进行部署

使用 docker 或者 docker-compose 进行配置可以灵活自定义本项目使用的配置目录。

## 参数配置

使用docker启动本项目需要的配置项目如下：

|参数|类型|含义|备注|
|:---:|:---:|:---:|:---:|
|`-v /app/.config`|VOLUMN|存放项目配置||
|`-p 3080`|port|[Web Api](../api_docs/README.md)以及浏览器插件的监听端口|可在全局配置中修改|

## 直接使用 docker 部署

直接在部署机器上执行

```bash
docker run -itd --name kubespider  -v {config_path}/.config:/app/.config -p 3080:3080 cesign/kubespider:latest
```

即可，注意替换命令中`{config_path}`为部署机器上真实存在的配置目录。

## 使用 docker compose 部署

构建如下 docker-compose.yaml 文件：

```yaml
services:
  kubespider:
    image: cesign/kubespider:latest
    depends_on:
      - qbittorrent
      - aria2
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Asia/Shanghai
    ports:
      - 3080:3080
    volumes:
      - {config_path}:/app/.config
    networks:
      - kb
  
  qbittorrent:
    image: lscr.io/linuxserver/qbittorrent:latest
    // and any other config needed by qbtorrent
    
  aria2:
    container_name: aria2-qb
    image: abcminiuser/docker-aria2-with-webui:latest-ng
    // and any other config needed by aria2

networks:
  kb:
    name: kb
```

在部署机器上执行 `docker-compose up` 即可，注意替换命令中`{config_path}`为部署机器上真实存在的配置目录。
