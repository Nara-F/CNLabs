# 环境与运行

## 原生环境

使用 Linux、Python 3.11 或更新版本和 make；校准环境及容器固定 Python 3.14.6。课程使用标准库，无 pip 安装步骤。在仓库根目录执行：

```sh
python3 --version
make build
make grade LAB=lab01_packets MODE=student SUITE=public
make grade LAB=lab05_routing TEST=test_self REPORT_DIR=/tmp/cnlabs-one-test
```

`make build` 执行 `compileall` 语法检查。`make grade` 默认学生实现、公开测试、全部实验；`LAB` 选择实验，`TEST` 按完整测试 ID 或后缀筛选，筛选成绩仅用于调试。报告默认写入 `reports/grade.json` 和 `reports/junit.xml`，`REPORT_DIR` 指定其他目录。

以下完整评分示例需要教师提供的隐藏测试；公开仓库本身不含这些测试或教师参考实现。外部实现目录按 `<实验名>.py` 命名；完整测试的隐藏目录按 `test_<实验名>.py` 命名。例如：

```sh
make grade LAB=lab05_routing MODE=student SUITE=full \
  IMPL_ROOT=/absolute/path/implementations HIDDEN_ROOT=/absolute/path/hidden \
  REPORT_DIR=/tmp/cnlabs-external
python3 -m netlab.grade --lab lab05_routing --mode student --suite full \
  --impl-root /absolute/path/implementations --hidden-root /absolute/path/hidden \
  --timeout 12 --report-dir /tmp/cnlabs-direct
```

完整课程仓库中 `make grade LAB=lab05_routing MODE=reference SUITE=full` 使用教师参考实现与隐藏测试。各测试在独立工作进程中执行；环境变量可调整以下默认预算：

| 预算 | 默认值 | 配置 |
|---|---:|---|
| 单次收集或测试墙钟 | 8 秒 | `NETLAB_TIMEOUT` 或 `--timeout` |
| CPU 时间 | 软限制 5 秒、硬限制 6 秒 | `NETLAB_CPU`，硬限制为该值加 1 |
| 虚拟地址空间 | 512 MiB | `NETLAB_MEMORY_MB` |
| 单文件大小 | 64 MiB | `NETLAB_FILE_MB` |
| 输出读取 | stdout、stderr 各保留末尾 1 MiB | 评分器固定值 |

`NETLAB_IMPL_ROOT` 和 `HIDDEN_ROOT` 可分别指定实现和隐藏测试目录；命令行对应参数优先。超时终止工作进程组。测试使用本机 loopback，不需要外网。

## 容器

Docker daemon 可用时，在课程目录构建并运行：

```sh
docker build -t cnlabs:local .
docker run --rm --network none cnlabs:local make grade LAB=lab01_packets
```

`--network none` 禁止外网，容器内 loopback 仍可用于实验 06 的本地 socket。容器以 `python:3.14.6-slim-bookworm` 为基础，镜像构建时需要取得基础镜像和 make 软件包。

## 本地代理演示

完成实验 06 后，在仓库根目录的三个终端运行：

```sh
# 终端 1：本地 origin
python3 -m http.server 18080 --bind 127.0.0.1
```

```sh
# 终端 2：学生代理，指定本地端口
python3 -m labs.lab06_proxy 18081
```

```sh
# 终端 3：强制 localhost 请求通过代理
curl --noproxy '' -x http://127.0.0.1:18081 http://127.0.0.1:18080/
```

终端 1 和 2 使用 Ctrl-C 停止。若端口已占用，分别改成两个空闲端口并同步修改 curl；代理端口可省略，由系统分配并打印。更多轨迹见 [示例](demo.md)。
