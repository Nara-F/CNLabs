# 实验 04：最长前缀、ARP 与转发

## 概览（Overview）

本实验属于 CNLabs，独立完成学生接口后通过公开和隐藏测试验证。

**目标**

实现确定性的 IPv4 转发器与 ARP 解析状态机，理解路由选择、TTL 与缓存生命周期。

## 学习目标（Learning Objectives）

推导最长前缀选择、TTL 更新和 ARP 重试的状态变化。

**前置知识**

建议先完成实验 01；了解 CIDR、链路层寻址及 ARP。预估 10–14 小时（含测试报告）。接口自包含，不依赖实验 01 的实现。

## 先修要求（Prerequisites）

使用 Python 3.11 或更新版本，具备基本网络、字节序和标准库知识。

## 背景（Background）

协议头中的长度、状态和边界都由接收者验证；本课程为可复现实验定义明确子集。

**场景**

路由器收到完整 IPv4 字节串，选择最长匹配前缀并递减 TTL。下一跳的 MAC 未知时排队并发出 ARP 事件；学到 MAC 后按 FIFO 转发。

## 必读资料（Required Readings）

请先阅读第 18 节所列 RFC 和课程原始资料中与本实验相关的章节。

## 架构总览（Architecture Overview）

数据模型位于 api.py，学生实现位于 student.py；测试通过公开接口调用。

**模型**

`Route(network, interface, next_hop=None)`：network 是规范 IPv4 CIDR（主机位必须为零），interface 是非空字符串；next_hop 为 IPv4 字符串或 None。`Frame(kind, interface, target, payload=b'')` 表示输出事件；`arp` 的 target 是请求 IP、payload 为空；`ipv4` 的 target 是目标 MAC、payload 是实际 IPv4 bytes。

## 起始代码指南（Starter Code Guide）

只在 student.py 中实现约定接口，允许使用 Python 标准库，不得导入 instructor。

## 分阶段任务（Tasks）

先完成基础功能，再实现边界与异常，最后通过独立向量、状态轨迹和压力测试检查。

**实施建议**

先独立验证最长前缀，再处理报文和校验和，最后增加缓存、队列和计时器。用显式 now 写精确边界测试；不要调用 `sleep()` 或依赖系统时间。本实验不生成 ICMP、不执行 IPv4 分片或完整以太网封装。

阶段 1：前缀查询；阶段 2：TTL 与头校验；阶段 3：ARP 缓存、排队和定时器；阶段 4：端到端状态轨迹。

## 接口规范（Interface Specifications）

**构造**

`Router(routes, *, cache_ttl=30, retry_interval=1, max_attempts=3, queue_limit=16, max_pending=256, max_cache=256)`。cache_ttl 和 retry_interval 为有限正数；max_attempts、queue_limit、max_pending、max_cache 为正整数，均不接受 bool；非法路由或参数抛 ValueError。初始时间为 0，空缓存和待发队列。单位是虚拟秒。

**路由查询**

`lookup(destination) -> Route | None`：IPv4 字符串无效抛 ValueError；匹配最多前缀位的路由；相同前缀保持输入顺序，第一个胜出；无匹配返回 None。支持 /0 和 /32。

**报文接收**

`receive(packet, now) -> list[Frame]` 首先执行 `advance(now)` 并把产生的事件置于输出列表前面。packet 非 bytes 抛 TypeError。仅处理完整无选项 IPv4：首字节 0x45、总长度等于输入长度、首部 checksum 正确、TTL 大于 1；否则丢弃。无路由也丢弃。合法报文 TTL 减一并重新计算首部 checksum，其他字节不变。

**下一跳与缓存**

路由有 next_hop 就解析它，否则解析目的地址。缓存按 `(interface, IP)` 隔离。命中后产生一个 ipv4 事件；MAC 以小写冒号分隔字符串输出。

**等待队列**

缓存未命中且该键没有待处理队列：创建队列、放入转发报文，立即产生一次 arp 事件。达到 max_pending 个不同等待键时，新的键及其报文被丢弃；已有队列则按 FIFO 添加；达到每键 `queue_limit` 时丢弃新报文，不发送额外请求。

**定时器**

`advance(now) -> list[Frame]` 要求有限数字时间单调不减（不接受 bool），否则 ValueError。先移除到期缓存（`expiry <= now`），然后按待处理键创建顺序处理：从初次请求时间起每 `retry_interval` 重试；最多发送 `max_attempts` 次（包含初次）。到下一次定时点若已达次数上限则丢弃队列。一次时间跳跃按键创建顺序处理，每个键内部按截止时间先后补发到期重试并在必要时清除队列；不同键的事件不做全局时间排序。

**学习地址**

`learn(interface, ip, mac, now) -> list[Frame]` 先执行 advance 并保留其事件。验证非空字符串接口、IPv4 地址以及六组两位十六进制、冒号分隔 MAC；错误抛 ValueError。记录缓存直到 `now + cache_ttl`，刷新原记录；缓存最多 max_cache 项，满时按最后学习顺序淘汰最早项；随后释放该键队列的全部报文，按 FIFO 产生 ipv4 事件。即使没有队列也可预先学习。

## 行为要求（Behavioral Requirements）

相同输入和状态应得到确定结果；所有未声明支持的协议扩展不属于实现范围。

**示例**

默认路由 `Route('0.0.0.0/0', 'eth0', '192.0.2.1')` 将任意未知目的地址解析为下一跳 192.0.2.1。收到 ARP 学习事件后，转发结果的 TTL 比输入小一，IPv4 首部校验和随之变化。

**状态轨迹：** t=0 收到两份同下一跳报文，首次发 ARP，第二份排队；t=1 重试；t=1.5 学习 MAC 后按 FIFO 释放两份，之后命中缓存；过期时间恰好到达时下一份报文重新触发解析。

## 边界情况（Edge Cases）

覆盖空输入、精确上限、超过上限、非法类型、截断及重复调用。

## 构建与运行（Build & Run）

在仓库根目录运行 `make grade LAB=lab04_router MODE=student SUITE=public`；教师可运行 `make grade LAB=lab04_router MODE=reference SUITE=full`。`make build` 编译检查。

**环境**

Linux、Python 3.11+、标准库；根目录 `make grade` 运行统一评分。无需网络权限、真实时钟或网卡。

## 调试指南（Debugging Guide）

缩小输入、逐字段打印并与独立向量比较；检查资源释放和错误分支。

## 测试（Testing）

**边界与测试**

公开测试在 `test_public.py`；评分器另有独立隐藏测试。覆盖重复前缀、/0、TTL 1、畸形包、精确到期、重试上限、队列溢出、多个接口以及时间跳跃。可按根目录说明选择参考实现验证。

## 评分（Grading）

公开和隐藏测试各以 100 分计，完整评分按公开 60%、隐藏 40% 合成；每个测试的权重与类别见 `@graded`。

## 提交（Submission）

**提交**

编辑 `labs/lab04_router/student.py`，不得导入 instructor 或其他学生实验；保持 `api.py` 中模型和接口签名。

## 常见问题（FAQ）

问：报文排队时还是发出时减少 TTL？答：接收并决定转发时只减少一次，队列释放不重复修改。

**复杂度**

设路由数 R、待处理键数 P、释放报文数 Q。线性路由查找 O(R) 足够；推进计时器 O(P + 到期重试次数)，释放队列 O(Q)。最多 max_pending 个等待键，每键最多 queue_limit 份报文，缓存最多 max_cache 项；路由数由输入决定。

## 进一步探索（Further Exploration）

比较线性表与前缀树的查询/更新复杂度，扩展 ICMP 超时错误并考虑限速。

**来源**

[RFC 791 IPv4](https://www.rfc-editor.org/rfc/rfc791)、[RFC 826 ARP](https://www.rfc-editor.org/rfc/rfc826)、[Stanford CS144 Spring 2008 Simple Router](https://www.scs.stanford.edu/08sp-cs144/labs/router.html)。定时器和事件接口由本课程定义，以显式时间实现可复现测试。
