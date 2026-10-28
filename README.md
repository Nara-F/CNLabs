# 计算机网络实验课程（学生公开版）

本公开仓库提供学生起始代码与公开测试；教师参考实现和隐藏测试保存在独立的教师维护仓库。`make validate` 检查原始 starter 基线，完成实验后使用 `make grade` 评测自己的实现。公开仓库的 GitHub Actions 在 Python 3.12.3 和 3.14.6 上检查原始 starter。

本课程以六个独立实验贯通报文、可靠传输、转发、路由和应用代理。使用 Python 3.11 及以上版本和标准库；具体接口和边界以各实验说明为准。建议先阅读 [学生指南](docs/student-guide.md) 和 [教学计划](docs/syllabus.md)。

| 实验 | 核心问题 | 本课预计投入 |
|---|---|---:|
| [01 报文](labs/lab01_packets/README.md) | IPv4/UDP 编解码与校验 | 8–12 小时 |
| [02 重组](labs/lab02_reassembly/README.md) | 有界缓冲、乱序和 EOF | 12–16 小时 |
| [03 传输](labs/lab03_transport/README.md) | 窗口、ACK、重传与 FIN | 14–18 小时 |
| [04 转发](labs/lab04_router/README.md) | 最长前缀、ARP 与 TTL | 10–14 小时 |
| [05 路由](labs/lab05_routing/README.md) | 距离向量与毒性逆转 | 12–16 小时 |
| [06 代理](labs/lab06_proxy/README.md) | HTTP、socket、并发和缓存 | 16–22 小时 |

以上是本课规划估计，含测试与报告，合计约 72–98 小时；加上课程阅读、设计评审和缓冲，建议预留约 80–110 小时。每个实验提供独立的公共类型与 starter，避免先前实现的错误阻断后续学习。协议模型的具体范围见各实验说明。

```sh
make build
make grade LAB=lab01_packets
```

从 `lab01_packets` 至 `lab06_proxy` 替换 `LAB` 值可运行相应公开测试；不指定 LAB 运行全部实验。完成后按 [评分说明](docs/grading.md) 和 [报告模板](writeups/template.md) 提交。课程安排见 [教学计划](docs/syllabus.md)，设计与参考依据分别见 [设计说明](docs/design.md) 和 [调研](docs/research.md)。

运行示例见 [可执行轨迹](docs/demo.md)。

本地验收结果与环境见 [验收记录](docs/acceptance.md)。
