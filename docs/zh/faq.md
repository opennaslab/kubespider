# 常见问题

本文列举使用 Kubespider 可能遇到的问题，并提供解决方案供您参考。



## 如何查看日志信息？

当遇到下载任务未正常开启等问题，您可以通过日志查看详细的提示信息，您也可以[提交 Issue](https://github.com/opennaslab/kubespider/issues) 并附上日志，方便我们更快地定位问题原因，操作步骤如下：

通过 SSH 登录 Kubespider 所部署的设备上，执行下述命令获取日志信息：

``` bash
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
