# 课程与实验调研

调研日期：2026-10-28。下列为对官方材料的独立概括；本课代码和评分设计独立制定，不复制官方实现。版本限定直接影响可比较的事实。

## 1. 课程目标和覆盖范围

[Stanford CS144 2026 Fall](https://cs144.github.io/) 将协议栈实现与课堂知识结合；当日主页已发布 check0–4。本课覆盖字节编码、重组、传输、转发、路由及代理，形成从抽象到真实 socket 的路径。

## 2. 前置知识与起点

[CS144 check0](https://cs144.github.io/assignments/check0.pdf) 使用 C++23 与提供的环境；[Imp starter](https://github.com/CS144/imp) 在调研时检查的提交为 `837d45af2ce837c4ff9cb29bfd2cfaff2578a6a5`（2026-09-29）。本课选择 Python 3.11 标准库，降低构建和工具链门槛，保留字节、状态、并发和协议分析的难度。

## 3. 实验序列与依赖

[check1](https://cs144.github.io/assignments/check1.pdf) 涉及有容量限制的重组、重复数据和性能；[check3](https://cs144.github.io/assignments/check3.pdf) 包括确定性 tick、最早未确认段、RTO 倍增及零窗口。我们借鉴其状态驱动思路，但每个 starter 自包含，传输协议采用固定初始 RTO 和显式窗口更新。

## 4. 系统与资源限制

[MIT 6.1810 2025 网络实验](https://pdos.csail.mit.edu/6.1810/2025/labs/net.html) 在 xv6/QEMU 中实现 E1000 驱动与 UDP 接收，使用 `make grade`、pcap/tcpdump，并限制每端口队列最多 16 包。本课借鉴受限资源与可观察性，不要求实现内核驱动。

## 5. 分布式故障和调试

[MIT 6.5840 指南](https://pdos.csail.mit.edu/6.5840/labs/guidance.html) 指出少量代码也可能有较高概念难度，给出约每周六小时的中等投入参考，并讨论不可靠网络、并发、崩溃、测试及竞态检测。本课将确定性时间、固定种子和可重复复现纳入设计；本课使用独立规划的工时估计。

## 6. 应用、并发和缓存

[CMU 15-213 当前实验列表](https://www.cs.cmu.edu/~213/labs.html) 规定实验占课程 50%，其中 Proxy 占 4%，采用 Autolab、代码审查和 Parsons 问题等方式。[CS:APP Proxy Lab](https://csapp.cs.cmu.edu/3e/proxylab.pdf) 以 C、Linux socket 和线程依次实现顺序、并发、缓存，70 分按 40/15/15 划分，使用 driver.sh。它是系统课的一部分，而非纯网络课程。本课的 Python 代理采用独立接口和评分。

## 7. 路由仿真

[Berkeley CS168 Fall 2026 Project 2](https://fa26.cs168.io/proj2/) 以 Python 3.8 仿真器分十阶段实现距离向量，涵盖静态路由、转发、通告、超时、水平分割、毒性逆转、无穷计数、毒化过期与触发更新；该项目明确无隐藏测试。本课按要求设置独立隐藏测试，算法背景参见 [CS168 距离向量教材](https://textbook.cs168.io/routing/distance-vector.html)。

## 8. 设计、沟通与评价

[MIT 6.033 general](https://www.mit.edu/~6.033/general.shtml) 所示版本为 Spring 2022，包含 lecture、recitation、tutorial；设计项目 40%、技术 35%、参与 25%。其 [hands-on](https://www.mit.edu/~6.033/handsons.shtml) 为 DNS、UNIX、Networking、Logging、MapReduce、Databases 六项中取五项，计 5%；具体作业通过 Canvas 提供。另据 [MIT OCW 2018 设计项目](https://ocw.mit.edu/courses/6-033-computer-system-engineering-spring-2018/pages/design-project/)，三人组经历初稿、口头报告、终稿与同伴评审。本课借鉴设计沟通，但采用独立实现和个人报告。

## 9. 构建、测试和风格

调研时的 CS144 Imp 使用 CMake 最低 3.24.2、C++23、`-Werror`、ASan/UBSan；`etc/tests.cmake` 配置按组件的 CTest、15 秒超时、check0/1/2/3/5/6 累积目标与速度测试。仓库当时 tests 目录包含七个 byte_stream 测试文件。[CS144 FAQ](https://cs144.github.io/lab_faq.html) 强调正确性与风格、format/tidy 及调试。本课以标准库 unittest、独立测试和可复现数据代替其构建链，性能阈值依据本课数据，不直接移植其吞吐量目标。

## 10. 评分、工作量与课程取舍

CS144 主页列实验正确性 20%、主观评价 18%，主观评价要求完成最后 checkpoint。本课建议自动评分 80%、设计报告人工评审 20%，自动评分总分按六项各 100 分换算。14 周建议约 80–110 小时，属于本课估计。采用独立 starter；跨实验演示作为可选拓展。原课程采用的 C++、C、Go 或驱动环境提供不同的系统层次，本课以 Python 聚焦核心机制和可复现验证。


## 来源版本与访问记录

| 来源 | 版本或时间 | 访问日期 |
|---|---|---|
| CS144 网站和 Imp | 2026 Fall；Imp 固定提交 `837d45af2ce837c4ff9cb29bfd2cfaff2578a6a5` | 2026-10-28 |
| MIT 6.033 general / OCW | Spring 2022 / Spring 2018 | 2026-10-28 |
| MIT 6.1810 / 6.5840 | 2025 网络实验 / 在线指南 | 2026-10-28 |
| CMU 15-213 / CS:APP | 当前列表 / 第三版 Proxy Lab | 2026-10-28 |
| Berkeley CS168 | Fall 2026 | 2026-10-28 |

## 十维比较与本课决策

| 维度 | 官方课程观察 | 本课决策及依据 |
|---|---|---|
| 目标 | CS144 侧重协议实现；6.033 强调系统设计；15-213 覆盖系统编程 | 六项实验贯通网络机制，并以个人报告检查设计表达 |
| 结构 | CS144 按 checkpoint，CS168 按路由阶段，Proxy Lab 递进三部分 | 按六个独立主题组织，知识递进、实现自包含 |
| 实验价值 | 6.1810 将驱动、UDP 与可观测数据结合 | 每项要求可观察输入输出和边界分析 |
| 理论与实践 | 6.033 以 lecture、recitation、tutorial 配合项目 | 每周阅读标准并完成实现、测试和设计说明 |
| 依赖 | CS144 checkpoint 持续构建，CS168 基于统一模拟器 | 避免前一实现错误阻断后续实验，保留可选跨层演示 |
| Starter | Imp 提供 C++ starter，CS168 提供仿真环境 | Python 标准库 starter 暴露类型、接口和待实现算法 |
| 文档 | CS144 提供 assignment 与调试 FAQ，6.033 提供设计项目说明 | 每项提供契约、运行、排错、测试和参考资料 |
| 自动评测 | Imp 的 CTest 分组件和设时限；Proxy Lab 用 driver | unittest 权重化评分、公开与独立隐藏测试，另有人工报告 |
| 前置与工作量 | 6.5840 指南指出实现短小仍可能概念困难 | 按主题规划 72–98 小时实验，含阅读评审共约 80–110 小时 |
| 工程规模 | Imp 包含构建、检查、测试与程序模块；当前公开测试目录有七个 byte_stream 测试文件 | 六实验覆盖有界状态到真实并发代理；实际代码和测试数量由验收记录统计 |

## 固定版本的工程证据

本次查看 [Imp 固定提交](https://github.com/CS144/imp/tree/837d45af2ce837c4ff9cb29bfd2cfaff2578a6a5) 的 [顶层 CMakeLists.txt](https://github.com/CS144/imp/blob/837d45af2ce837c4ff9cb29bfd2cfaff2578a6a5/CMakeLists.txt)、[编译选项](https://github.com/CS144/imp/blob/837d45af2ce837c4ff9cb29bfd2cfaff2578a6a5/etc/cflags.cmake)、[CTest 配置](https://github.com/CS144/imp/blob/837d45af2ce837c4ff9cb29bfd2cfaff2578a6a5/etc/tests.cmake) 及 [tests 目录](https://github.com/CS144/imp/tree/837d45af2ce837c4ff9cb29bfd2cfaff2578a6a5/tests)。工程以构建配置、编译检查、库、应用和测试共同支撑 checkpoint；测试目录规模与累计 CTest 目标是不同统计口径。本课独立设计实现，验收时的代码行数和测试数见 [验收记录](acceptance.md)。
