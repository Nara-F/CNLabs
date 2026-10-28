# 第三方工具与参考资料

本项目运行和测试仅使用 Python 标准库，没有第三方 Python 包依赖。工具链由使用者安装，仓库不附带这些工具或基础镜像。

| 工具或材料 | 用途及本次验证版本 | 来源与许可证 |
| --- | --- | --- |
| CPython | 运行时；本机 CPython 3.14.6，支持 Python ≥ 3.11 | [Python 官网及许可证](https://docs.python.org/3/license.html)：Python Software Foundation License Version 2（PSF-2.0）；Python 发行版可能包含另行授权的组件，见其许可证说明。 |
| GNU Make | 开发与评分入口；本机 4.3 | [GNU Make](https://www.gnu.org/software/make/)：GPL-3.0-or-later。 |
| Git | 版本管理开发工具；本机 2.43.0 | [Git 源码许可证](https://github.com/git/git/blob/master/COPYING)：GPL-2.0；个别文件的许可参见其源码声明。 |
| Docker CLI | 可选容器工具；本机发现 29.9.2，daemon 未运行 | [Docker CLI 源码](https://github.com/docker/cli)：Apache-2.0。 |
| Python 官方容器镜像 | CI/容器目标 `python:3.14.6-slim-bookworm`；未验证镜像摘要 | [Python Official Image](https://hub.docker.com/_/python) 及 [Debian 官方镜像](https://hub.docker.com/_/debian)：Python 和 Debian 软件包分别适用其各自许可证；基础镜像不随本仓库分发。 |

课程中的 RFC 和大学公开资料链接用于协议和教学设计参考；未复制大学课程源码。项目自身代码按仓库的 MIT 许可证授权；协议文档与外部资料仍由各自权利人授权。

本次本机验证环境为 Ubuntu 24.04、Linux x86_64、内核 `7.0.0-38-generic`，CPython 构建编译器为 GCC 13.3.0。容器 registry 查询遇到 TLS EOF，且 Docker daemon 未运行，因此镜像 digest 和容器执行均未验证。
