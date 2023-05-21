# FAQ

In this article, we list problems that you may encounter using Kubespider and provide solutions for your reference.



## How do I view the container's log?

When you encounter problems such as download tasks not usually starting, you can check the detailed prompt through the log, you can also [submit an issue](https://github.com/opennaslab/kubespider/issues) and attach the log, so that we can quickly locate the cause of the problem:

Log into the device that deployed the Kubespider via SSH, execute the following command to obtain log:

```bash
# obtain Kubespider log
docker logs kubespider

# obtain aria2-pro log
docker logs aria2-pro
```



## Failed download files to the NFS folder?

**Problem**:

When your intranet deploys an NFS service, which is mounted on Kubespider's machine. However, the error appears when you attempt to download files throuth Kubespider. The key information in the log is: `Exception caught while allocating file space.`, and no files are generated in the mounted directory.



**Solutions**:

In this case, we need to modify the `kubespider/aria2/aria2.conf` file, change the value of `file-allocation` to `none`, that is, `file-allocation = none`, and then execute the command: `docker restart aria2-pro` to restart the related service. For more information, see [related Issues](https://github.com/aria2/aria2/issues/1032).



