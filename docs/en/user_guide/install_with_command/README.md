# Deploy with docker

You can have more flexable control of path configuration while installing with docker or docker-compose.

## Parameters

Parameters needed to start this project in docker shows as follow:

|Parameter|Type|Function|Note|
|:---:|:---:|:---:|:---:|
|`-v /app/.config`|VOLUMN|Path to store all configurations||
|`-p 3080`|port|Listen port of [Web Api](../../../zh/user_guide/api_docs/README.md) and Chrome plugin|Can be changed by Global configuration|

## Run with docker cli

Run the following command in machine to be deployed to:

```bash
docker run -itd --name kubespider  -v {config_path}/.config:/app/.config -p 3080:3080 cesign/kubespider:latest
```

`{config_path}` should be replaced to the real path in docker host.

## Deploy with docker-compose

Build your docker-compose.yaml file like list:

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

And run `docker-compose up` in your docker host machine.

`{config_path}` should be replaced to the real path in docker host.
