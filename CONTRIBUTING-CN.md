# 贡献手册
如果你想向Kubespider贡献，请阅读如下内容。

## 安装Kubespider
在开发之前，你需要首先安装Kubespider。
```sh
git clone https://github.com/opennaslab/kubespider.git
cd kubespider
bash hack/install_kubespider.sh
```

## 更新依赖后部署
如果你有更新/添加python库依赖(requirements.txt需要被修改)，你需要按如下步骤部署Kubespider。

### 1.在Kubespider代码目录构建镜像
在中国大陆，如果没有HTTP_PROXY/HTTPS_PROXY可构建失败，所以有代理请设置；如果没有，请把--build-arg相关删除。
```sh
docker build -t cesign/kubespider:latest -f Dockerfile ./ --build-arg HTTP_PROXY=http://<server>:<port> --build-arg HTTPS_PROXY=http://<server>:<port>
```

### 2.删除已有Kubespider容器
```sh
docker rm kubespider --force
```

### 3.使用最新镜像启动Kubespider
```sh
export image_registry=cesign
export KUBESPIDER_VERSION=lates
docker run -itd --name kubespider \
    -v ${HOME}/kubespider/.config:/app/.config \
    --network=host \
    --restart unless-stopped \
    ${image_registry}/kubespider:${KUBESPIDER_VERSION}
```

## 无依赖更新部署
如果没有想关依赖添加/更新，你可以通过如下命令使用修改后的代码启动Kubespider:
```sh
# 在Kubespider代码文件夹运行
docker cp kubespider kubespider:/app/ && docker restart kubespider
```

## 提PR
如果你完成了开发，并且经过足够的测试，你可以在此代码库上创建PR。维护者会尽可能快地检查并合入代码。