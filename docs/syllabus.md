# 14 周教学计划

## 可测量的学习目标

完成课程后，学生能够：

1. 编解码 IPv4/UDP 字节串，用独立向量验证长度、字节序和校验和。
2. 构造乱序与重叠输入，证明重组缓存容量不变量并解释 EOF。
3. 绘制发送窗口、累计 ACK、FIN 和重传计时器的状态轨迹，复现链路故障。
4. 计算最长前缀匹配、ARP 队列及距离向量更新，解释故障后的状态变化。
5. 用 socket 实现代理的指定 HTTP 子集，分析并发资源、缓存和关闭路径。
6. 设计可复现测试、测量复杂度并以证据评审设计取舍。

## 预备知识与自测

需要 Python 3.11、函数和类、bytes、字典、异常、unittest、基础数据结构、二进制和位运算。先尝试解释 `int.from_bytes(b'\x01\x02', 'big')` 的结果、画出 4 字节缓冲窗口、用 `socket` 建立本地连接，并运行 `python3 --version`、`make build` 和 `make grade LAB=lab01_packets`。无法解释的部分先阅读实验前置知识；starter 的未完成测试是正常开发起点。

六实验的本课估计分别为 8–12、12–16、14–18、10–14、12–16、16–22 小时，合计 72–98 小时；加阅读与评审共约 80–110 小时。

## 每周安排与必读

| 周 | 理论与实验里程碑 | 必读标准或官方课程材料 |
|---|---|---|
| 1 | 分层、字节序；01 checksum | [RFC 1071 §1–2](https://www.rfc-editor.org/rfc/rfc1071.html#section-1) |
| 2 | IPv4、UDP；完成 01 | [RFC 791 §3.1](https://www.rfc-editor.org/rfc/rfc791.html#section-3.1)、[RFC 768](https://www.rfc-editor.org/rfc/rfc768.html) |
| 3 | 流、缓冲和背压；02 窗口设计 | [CS144 check1](https://cs144.github.io/assignments/check1.pdf) |
| 4 | 重叠、缺口、EOF；完成 02 | [RFC 9293 §3.3](https://www.rfc-editor.org/rfc/rfc9293.html#section-3.3) |
| 5 | 序号和累计 ACK；03 接收与发送 | [RFC 9293 §3.4](https://www.rfc-editor.org/rfc/rfc9293.html#section-3.4) |
| 6 | 流量控制和重传；完成 03 链路模拟 | [RFC 6298 §2、§5](https://www.rfc-editor.org/rfc/rfc6298.html#section-2)、[CS144 check3](https://cs144.github.io/assignments/check3.pdf) |
| 7 | CIDR、转发；04 前缀与 TTL | [RFC 1812 §5.2](https://www.rfc-editor.org/rfc/rfc1812.html#section-5.2)、[RFC 791 §3.1](https://www.rfc-editor.org/rfc/rfc791.html#section-3.1) |
| 8 | ARP 缓存、队列；完成 04 | [RFC 826 报文格式与处理](https://www.rfc-editor.org/rfc/rfc826.html) |
| 9 | 距离向量；05 单节点与收敛 | [CS168 距离向量教材](https://textbook.cs168.io/routing/distance-vector.html) |
| 10 | 路由环路、失效、毒性逆转；完成 05 | [RFC 1058 §2.2](https://www.rfc-editor.org/rfc/rfc1058.html#section-2.2) |
| 11 | HTTP 与 socket；06 基本代理 | [RFC 9112 §2–3](https://www.rfc-editor.org/rfc/rfc9112.html#section-2) |
| 12 | 并发和资源；06 并发与关闭 | [CS:APP Proxy Lab](https://csapp.cs.cmu.edu/3e/proxylab.pdf) |
| 13 | 缓存与性能；完成 06 | [RFC 9111 §2–4](https://www.rfc-editor.org/rfc/rfc9111.html#section-2) |
| 14 | 系统设计与评审；六份报告和展示 | [MIT 6.033 设计项目](https://ocw.mit.edu/courses/6-033-computer-system-engineering-spring-2018/pages/design-project/) |

每两周里程碑包含可运行代码、自主测试、状态不变量及报告草稿。拥塞控制、DNS 和 TLS 通过研讨与延伸阅读覆盖：阅读 [RFC 5681 §3](https://www.rfc-editor.org/rfc/rfc5681.html#section-3)、[RFC 1035 §2](https://www.rfc-editor.org/rfc/rfc1035.html#section-2)、[RFC 8446 §2](https://www.rfc-editor.org/rfc/rfc8446.html#section-2)，分别比较拥塞与流量控制、名称解析以及 TLS 握手。跨实验端到端演示为可选拓展。
