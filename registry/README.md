## kubespider source provider hub

### provider

- [mikanani_source_provider](providers%2Fmikanani_source_provider)

### sdk

#### python sdk

##### python sdk 提供 Manager 类用来管理 source provider

Manager使用方式参考[alist_source_provider](providers%2Falist_source_provider)
通过 @manager 把当前source provider 注册到manager中
通过 @manager.registry 把当前被装饰的方法注册为api
支持注册的api类型定义在了HttpApi中
通过以下方法调用manager
```python
if __name__ == '__main__':
    manager.run()
```
manager.run() 通过识别provider.yaml来给当前程序运行添加命令行运行参数
当程序运行起来后会开始一个 http server
http server 会提供一些类型的api,api的运行逻辑为对应被装饰的方法
当前程序会把当前地址和支持的api上报给kubespider
kubespider 可以通过api调用来操作当前的source privider

# todo
执行api对应的逻辑异步执行