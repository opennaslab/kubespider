# 常见问题

本文列举使用 Kubespider 可能遇到的问题，并提供解决方案供您参考。

## 如何查看日志信息？

当遇到下载任务未正常开启等问题，您可以通过日志查看详细的提示信息，您也可以[提交 Issue](https://github.com/opennaslab/kubespider/issues) 并附上日志，方便我们更快地定位问题原因，操作步骤如下：

通过 SSH 登录 Kubespider 所部署的设备上，执行下述命令获取日志信息：

```bash
# 获取 Kubespider 服务日志
docker logs kubespider

# 获取 aria2-pro 服务日志
docker logs aria2-pro
```

## 下载至 NFS 失败？

**故障现象**：

内网部署了一个 NFS 服务，挂载到 Kubespider 所属机器上，按照流程设置完毕，但是执行下载时提示错误，关键信息日志为：`Exception caught while allocating file space.`，查看挂载目录中没有生成任何文件。

**解决方案**：

此情况下，我们需要修改 `kubespider/aria2/aria2.conf` 文件，将 `file-allocation`（文件预分配方式） 的值修改为 `none`（无），即 `file-allocation=none`，随后执行命令 `docker restart aria2-pro` 重启相关服务即可。更多介绍，见[相关 Issue](https://github.com/aria2/aria2/issues/1032)。

## Unraid 使用 docker 连接 aria2 超过最大重试次数 

**故障现象**

Unraid 上使用 docker 尝试连接 aria2，提示

```
Please ensure your aria2 server is ok:HTTPConnectionPool(host='127.0.0.1', port=6800): Max retries exceeded with url: /jsonrp
```

**解决方案**

把 kubespider 的 网络权限修改为 'host'

参考 [请问有Unraid docker的配置教程么 · Issue #259 · opennaslab/kubespider](https://github.com/opennaslab/kubespider/issues/259)

## 更新使用 docker 安装的 kubespider 版本

**故障现象**：

当出新功能时候。在如群晖等机器中，使用教程中 `hack/install_kubespider.sh` 脚本安装的 kubespider 是无法通过

```bash
cd kubespider.git/
git pull
```

直接拉取最新源代码来更新版本的。而是要拉取最新镜像并重置该 docker container。

**解决方案**

1. 拉取最新版本镜像 `docker pull cesign/kubespider:latest` 或者 `docker pull docker pull cesign/kubespider:latest`
2. 重置 docker cotainer，如群晖中在网页端打开 docker->容器->kubespider->右键->操作->重置。或 设置->导出->删除容器->导入。
3. 启动容器并观察 log（后续版本中会增加版本日志）

## 更新 .config/xxx_provider.yaml 配置未生效

**故障现象**

通过一键安装脚本安装 kubespider 后，修改 xxx_provider.yaml 配置不生效。

**解决方案**

1. 确定修改的是否是正确文件：通过 docker 安装的 kubespider，配置目录在 `${KUBESPIDER_HOME}/kubespider/.config`。注意确认 docker 中的目录映射，修改安装前源代码目录中的配置，如 `${KUBESPIDER_HOME}/kubespider/kubespider/.config` 是无效的。
2. 确认配置文件读写权限是否正确：如果是按照 [教程](https://github.com/opennaslab/kubespider/blob/main/docs/zh/user_guide/synology_installation/README.md) 安装的 kubespider，其中第五步切到了 root 用户 `sudo -i`，此时默认创建的配置文件是无法在网页端使用群晖文本编辑器修改的（按 Ctrl+S会闪一下，但不会保存成功）。此时可以通过 ssh 切换到 root 用户重新修改，或者通过 File Station->右键.config 目录->权限->应用到这个文件夹、子文件夹及文件->确定，重新分配权限。
