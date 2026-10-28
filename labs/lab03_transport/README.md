# Lab 03：可靠传输教学协议

## Overview

实现单向可靠字节传输中的发送方、接收方与可注入时钟，建议投入 14–18 小时。无需使用 Lab02 学生实现。

## Learning Objectives

理解累计 ACK、滑动接收窗口、超时重传、指数退避、EOF、零窗口恢复和乱序处理。

## Prerequisites

Python dataclass、字节流与 Lab02 概念；熟悉状态机与离散时间模拟。

## Background

发送方在 ACK 与窗口约束下发送；接收方仅确认连续前缀。丢失由最早未确认片段的计时器恢复。

## Required Readings

- [CS144 官方实验](https://cs144.github.io/) 的 TCP sender/receiver 教学材料。
- [RFC 9293](https://www.rfc-editor.org/rfc/rfc9293.html) 的序号、累计确认与窗口；[RFC 6298](https://www.rfc-editor.org/rfc/rfc6298.html) 的重传计时器与指数退避。

## Architecture Overview

调用者负责模拟链路并驱动 Sender、Receiver；Segment 和 Ack 是不可变值。FIN 占一个序号，数据每字节占一个序号。这里无握手、拥塞控制、校验和、序号回绕或真实 TCP 报文，也不实现 RTT 估计/Karn 算法；初始 RTO 固定，区别于 RFC 6298 的动态估计。本实验协议不可用于真实网络。

## Starter Code Guide

api.py 提供 Segment、Ack 与类接口；student.py 提供可导入的骨架。完成 Sender 和 Receiver；它们不得依赖 instructor 或其他实验的 student。

## Tasks

按顺序完成：

1. 验证参数，分别实现接收端的容量、乱序和累计确认。
2. 实现发送窗口、分段、FIN 与部分 ACK。
3. 增加最早未确认段的计时器、指数退避、窗口更新和原子异常。
4. 使用多个固定种子的离散链路模拟丢失、重复和重排；拥塞控制为拓展。

状态轨迹：Sender(b'ab', 2, 1) 在时间 0 发送 seq=0 的 `b'a'`；收到 Ack(1,2) 后发送 seq=1 的 `b'b'` 和 seq=2 的 FIN。若数据段丢失，时间 1 重传最早未确认段且下一次截止时间为 3。Receiver 先收到 FIN 会保持累计 ACK=0；收到前两字节后 ACK=3，读出 `b'ab'` 后 finished 为真。

## Interface Specifications

`Segment(seq, data=b'', fin=False)`、`Ack(next_seq, window)` 是 dataclass。`Sender(data: bytes, mss: int, rto: float)` 要求 bytes、正 MSS 和正 RTO；类型错误 TypeError，值错误 ValueError。`send(now)` 返回新发送片段列表；`ack(ack: Ack, now)` 处理确认并返回 None；`tick(now)` 返回零个或一个重传片段；`finished` 表示 FIN 已确认。时间为调用者提供的非负、有限、单调不减秒数，支持 int 或 float（不接受 bool）；倒退、NaN 或无穷为 ValueError，错误类型为 TypeError。RTO 同样要求有限、正数且不接受 bool。

`Receiver(capacity: int)` 要求正容量；`receive(segment)` 返回当前 Ack，`read(n: int)` 返回至多 n 个字节的 bytes，`ack()` 可在读取后生成窗口更新，`finished` 在 FIN 到达且数据读空后为真。所有容量、MSS、序号、ACK 字段及读取长度要求精确 int，不接受 bool 或 float；类型错误 TypeError。Segment.fin 必须为 bool，Ack 和 Segment 必须为对应类型；失败调用不改变任何状态（包括计时器时间）。负序号、负读取、冲突 FIN 或 FIN 前有已接受的更后字节，以及越过已知 FIN 的数据均 ValueError；数据不是 bytes 时 TypeError。

## Behavioral Requirements

初始发送窗口为 1；收到合法 ACK 后窗口更新为其 window。窗口右边界为累计 ACK 加 window；发送按 MSS 切分，FIN 在有窗口空间时单独发送。未来 ACK 被忽略；旧 ACK 不更新窗口；重复当前 ACK 可更新窗口。部分 ACK 切掉已确认前缀。最早未确认片段计时器从首次发送或新确认时启动；到期仅重传最早片段，RTO 加倍，新确认重置为初始 RTO。所有确认后停止计时器。零窗口不主动探测：应用读取后调用 `ack()` 并可靠地向发送方传递窗口更新。链路模拟允许数据段及普通 ACK 丢失、重排和重复；假设周期性窗口更新通过可靠控制信道送达，使零窗口恢复有明确的活性前提。

接收方窗口为 `[read_position, read_position + capacity)`；截断窗口之外字节，先到的重叠字节获胜，累计 ACK 为连续数据后位置，接收 FIN 后增加一。乱序 FIN 可记录，等缺口填满后确认；重复 FIN 必须一致。窗口为右边界减连续数据末尾；乱序字节位于该区间内，不重复计费。

## Edge Cases

空流也须发送 FIN；数据可与 FIN 同段接收；FIN 不占接收缓存。重复确认不重启计时器；超时相等时触发。测试窗口关闭后显式窗口更新、重复和缺口、错误 ACK 与单调时间。接收空间 O(capacity)，单次处理应与窗口交集相关。

## Build & Run

在仓库根目录运行：

```sh
make build
make grade LAB=lab03_transport
make grade MODE=reference LAB=lab03_transport
```

## Debugging Guide

记录每次操作前后的绝对位置、缓存、窗口与状态；先缩小为两次操作的复现。不要依赖墙钟、网络或第三方库。

## Testing

公开测试是可执行契约的一部分，隐藏测试覆盖重排、边界、资源与状态。独立构造反例并反复检查不变量；不得调用其他测试方法复用测试。

## Grading

公开与隐藏测试各计 100 分；full 模式公开占 60%，隐藏占 40%。接口、行为、边界和异常均计分。

## Submission

只提交本实验的 student.py，保持公开接口不变，不导入 instructor。Python 3.11+，仅标准库。

## FAQ

**截断数据会自动缓存吗？** 不会；窗口之外的数据须由发送方重传。

**为什么零窗口需要额外更新？** 该教学协议不实现持续探测，接收方读取后须显式提供可靠窗口更新。

## Further Exploration

比较按字节与区间存储的空间和时间成本，设计基准并解释权衡。
