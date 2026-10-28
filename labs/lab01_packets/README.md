# 实验 01：IPv4、UDP 与 Internet checksum

## 概览（Overview）

本实验属于 CNLabs，独立完成学生接口后通过公开和隐藏测试验证。

**目标**

理解分层、网络字节序、长度字段和端到端校验。实现真实 bytes 编解码，明确区分传输层和网络层。

## 学习目标（Learning Objectives）

从字节级向量推导校验和，独立检查 IPv4 与 UDP 的长度和伪首部。

**预备知识**

需了解二进制、位运算、Python dataclass、IPv4 地址；阅读 RFC 791、768 和 1071。建议 8–12 小时（含测试报告）。

## 先修要求（Prerequisites）

使用 Python 3.11 或更新版本，具备基本网络、字节序和标准库知识。

## 背景（Background）

协议头中的长度、状态和边界都由接收者验证；本课程为可复现实验定义明确子集。

**场景**

应用数据进入 UDP，UDP 段成为 IPv4 负载；接收方逆向解析。任何未经验证的长度均不可信。

## 必读资料（Required Readings）

请先阅读第 18 节所列 RFC 和课程原始资料中与本实验相关的章节。

## 架构总览（Architecture Overview）

数据模型位于 api.py，学生实现位于 student.py；测试通过公开接口调用。

## 起始代码指南（Starter Code Guide）

只在 student.py 中实现约定接口，允许使用 Python 标准库，不得导入 instructor。

## 分阶段任务（Tasks）

先完成基础功能，再实现边界与异常，最后通过独立向量、状态轨迹和压力测试检查。

**开发步骤**

先完成 checksum，再用固定字节向量检查 IPv4，最后实现 UDP 伪首部。分别测试编码与解码，避免仅靠双向往返掩盖相同错误。

阶段 1：反码校验和；阶段 2：IPv4 编解码；阶段 3：UDP 伪首部；阶段 4：独立向量和随机边界。

## 接口规范（Interface Specifications）

**数据模型**

`IPv4Packet(src, dst, protocol, payload, ttl=64, identification=0, flags_offset=0, tos=0)`；`UDPSegment(src_port, dst_port, payload)`。地址为点分十进制字符串，负载为 bytes。值比较由 dataclass 提供。

**checksum**

`checksum(data: bytes) -> int` 对大端 16 位字做反码和，重复回卷进位后按位取反；奇数字节尾部补零，仅用于计算。空数据结果 65535；非 bytes 抛 TypeError。

**IPv4 编码**

`encode_ipv4(packet) -> bytes` 编码无选项 20 字节首部与负载，version=4、IHL=5，计算首部校验和。`tos`、`ttl`、`protocol` 为 0..255 的整数，`identification`、`flags_offset` 为 0..65535 的整数（均不接受 bool），负载最多 65515 字节。地址或范围无效抛 ValueError；模型或负载类型错误抛 TypeError。flags_offset 按原始 16 位保留，不执行分片。

**IPv4 解码**

`decode_ipv4(data) -> IPv4Packet` 验证 bytes、长度至少 20、版本/IHL 恰为 0x45、总长度严格等于输入长度且首部校验和正确；违反条件抛 ValueError，非 bytes 抛 TypeError。不接受尾随填充或 options。返回规范化点分十进制地址，原样保留各字段及负载。

**UDP 编码**

`encode_udp(segment, src, dst) -> bytes` 编码 8 字节首部和最多 65527 字节负载。端口为 0..65535 的整数，不接受 bool。以源和目标 IPv4、零字节、协议号 17、UDP 长度构造伪首部，计算校验和；计算结果为零时在线上写 0xffff。地址、范围、长度无效为 ValueError，模型或负载类型错误为 TypeError。

**UDP 解码**

`decode_udp(data, src, dst) -> UDPSegment` 检查 bytes、至少 8 字节、长度严格等于输入；非零校验和必须连同伪首部验证为零；零校验和表示 IPv4 中省略校验。格式、地址或校验错误抛 ValueError，输入非 bytes 抛 TypeError。

## 行为要求（Behavioral Requirements）

相同输入和状态应得到确定结果；所有未声明支持的协议扩展不属于实现范围。

**示例**

`checksum(b'\x01') == 0xfeff`。将 `UDPSegment(1000, 53, b'hello')` 编码后可作为 IPv4Packet 的 payload；解码时必须使用相同的源和目标地址。

## 边界情况（Edge Cases）

覆盖空输入、精确上限、超过上限、非法类型、截断及重复调用。

**边界**

检查奇数长度、零、最大长度、端口上下界、长度不匹配、损坏首部和伪首部；长度不匹配即使存在有效前缀也必须拒绝。

## 构建与运行（Build & Run）

在仓库根目录运行 `make grade LAB=lab01_packets MODE=student SUITE=public`；教师可运行 `make grade LAB=lab01_packets MODE=reference SUITE=full`。`make build` 编译检查。

**环境**

Linux，Python 3.11+，仅标准库。仓库根目录执行 `make grade`；参考课程根目录的评分说明。

## 调试指南（Debugging Guide）

缩小输入、逐字段打印并与独立向量比较；检查资源释放和错误分支。

**排错与思考**

校验失败时检查端序、补零的位置、是否将首部 checksum 字段先清零，以及 UDP 伪首部的地址顺序。思考 checksum 为什么不能检测所有错误、为什么必须检查总长度。

## 测试（Testing）

**验证**

公开测试为 `labs/lab01_packets/test_public.py`；根目录 `make grade` 使用统一评分器。隐藏测试还覆盖独立模型和大负载。所有输入生成固定种子，结果可复现。

## 评分（Grading）

公开和隐藏测试各以 100 分计，完整评分按公开 60%、隐藏 40% 合成；每个测试的权重与类别见 `@graded`。

## 提交（Submission）

**提交**

仅编辑并提交 `labs/lab01_packets/student.py`；保留公开函数签名，不导入 instructor。`api.py` 定义不可变模型。

## 常见问题（FAQ）

问：为什么 UDP 结果为零时要写 0xffff？答：线上零表示 IPv4 中未使用校验和。

**性能**

编解码及 checksum 应为 O(n) 时间、O(n) 或更少额外空间，n 为报文长度。不要逐字节反复拼接不可变 bytes 导致平方时间。

## 进一步探索（Further Exploration）

推导单比特错误可被检测而某些多比特错误无法被检测的原因；比较 CRC 的检错能力。

**延伸阅读与来源**

[RFC 791](https://www.rfc-editor.org/rfc/rfc791)、[RFC 768](https://www.rfc-editor.org/rfc/rfc768)、[RFC 1071](https://www.rfc-editor.org/rfc/rfc1071)、[Stanford CS144](https://cs144.github.io/)。
