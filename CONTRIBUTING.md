# Contribution guidelines
If you want to contribute to Kubespider, please read the following content.

## Install Kubespider
Before developing, you need to install Kubespider first.
```sh
git clone https://github.com/opennaslab/kubespider.git
cd kubespider
bash hack/install_kubespider.sh
```

## Deploy with updated dependencies
If you add/update python lib dependencies( requirements.txt needs to be modified), you need to deploy Kubespider with the following steps:

### 1.Build an image in Kubespider code directory
In china mainland, it may build failed if without HTTP_PROXY/HTTPS_PROXY, so please set if you have proxy. But if you don't have it, please delete `--build-arg` related.
```sh
docker build -t cesign/kubespider:latest -f Dockerfile ./ --build-arg HTTP_PROXY=http://<server>:<port> --build-arg HTTPS_PROXY=http://<server>:<port>
```
### 2.Delete exist Kubespider container
```sh
docker rm kubespider --force
```

### 3.Launch Kubespider with the newest image
```sh
export image_registry=cesign
export KUBESPIDER_VERSION=lates
docker run -itd --name kubespider \
    -v ${HOME}/kubespider/.config:/app/.config \
    --network=host \
    --restart unless-stopped \
    ${image_registry}/kubespider:${KUBESPIDER_VERSION}
```

## Deploy with no dependencies update
If no new dependencies are added/updated, you can run the following command to run Kubespider with the modified code:
```sh
# Run it in Kubespider code directory
docker cp kubespider kubespider:/app/ && docker restart kubespider
```

## Give a PR
Once you finish developing and do enough testing, you can create a PR in this repository. The maintainer will check and merge it as soon as possible.