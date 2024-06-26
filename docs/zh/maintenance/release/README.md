# 版本发布流程

## Patch版本发布流程

如v1.1.x，其中x即为Patch版本编号，通常发布此版本是为了修复 v1.1.(x-1) 版本的bug。

1. 确保相关bugfix都已cherry-pick到 release-1.1 分支，如 [PR 491](https://github.com/opennaslab/kubespider/pull/491).
2. 在对应分支上创建release tag，如v1.1.x。
3. 编写对应的release notes，如：https://github.com/opennaslab/kubespider/releases/tag/v0.6.2
4. 运行流水线  [workflow](https://github.com/opennaslab/kubespider/actions/workflows/kubespider-release-notes.yaml) 获取对应的贡献者，并且写入release notes。

## Minor版本发布流程

如v1.x.y，其中x即为Minor版本编号，通常代表正式版本发布，包括相关的特性和bugfix。

1. 基于main分支创建对应的release分支，如这里的release-1.x.
2. 在对应分支上创建release tag，如v1.x.y。
3. 编写对应的release notes，如：https://github.com/opennaslab/kubespider/releases/tag/v0.6.0
4. 运行流水线  [workflow](https://github.com/opennaslab/kubespider/actions/workflows/kubespider-release-notes.yaml) 获取对应的贡献者，并且写入release notes。
