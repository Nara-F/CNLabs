# Lab 02：有界字节流与乱序重组

## Overview

实现固定容量的字节接收与重组器，建议投入 12–16 小时。输入片段可重排、重复、部分重叠；应用通过读取产生背压和释放容量。

## Learning Objectives

理解绝对偏移、接收窗口、连续前缀、去重、流结束和空间上界；设计可复现边界测试。

## Prerequisites

Python bytes、字典、循环、异常与 unittest；理解可靠字节流与窗口。

## Background

窗口左边是应用已读取位置，右边是左边加容量；已组装未读字节与乱序字节共享这个窗口。缺口阻止后续字节交付。

## Required Readings

- [Stanford CS144 实验材料](https://cs144.github.io/)，特别是 stream reassembler。
- [RFC 9293 TCP](https://www.rfc-editor.org/rfc/rfc9293.html) 中序号及接收窗口；本实验是简化模型。

## Architecture Overview

网络片段进入 Reassembler，连续前缀进入可读取缓冲，应用读取后窗口前移。该模型无连接、握手、校验和及 TCP 序号回绕。

## Starter Code Guide

api.py 定义接口；student.py 的关键算法留待实现；test_public.py 包含公开测试。不得把 reference 作为实现依赖。

## Tasks

按顺序完成：

1. 验证参数并建立读位置、连续位置和窗口右边界。
2. 截取窗口交集，按先到优先存储独立字节，提升连续前缀。
3. 实现读取、容量释放及唯一 EOF；设计状态转换和异常原子性测试。
4. 用大偏移和大输入验证内存上界与运行时间。

状态轨迹（容量 4）：`insert(2,b'cd')` 后 pending=2、available=0；`insert(0,b'ab')` 后 pending=0、available=4；`read(2)` 返回 `b'ab'`，available=2、窗口右边界由 4 增至 6；`insert(4,b'ef',True)` 后可读取 `b'cdef'`，读空后 finished 才为真。

## Interface Specifications

`Reassembler(capacity: int)` 要求正容量，否则 ValueError。`insert(index, data, eof=False)` 以非负绝对偏移插入 bytes；负偏移 ValueError，非 bytes TypeError。`read(n)` 返回至多 n 字节，负数 ValueError。所有整数参数均要求精确 `int`，不接受 bool 或 float，类型错误 TypeError；eof 必须为 bool。所有成功的 insert 返回 None，read 返回 bytes；失败调用不改变任何状态。只读属性 `pending` 为乱序独立字节数，`available` 为连续未读字节数，`finished` 为 EOF 已到达且所有连续字节已读。

## Behavioral Requirements

每次插入仅接收 `[next, read_position + capacity)` 的交集；已读或已组装数据不变。对仍在乱序缓存中的重叠字节先到者获胜。连续字节立即提升。`eof=True` 表示片段末尾是唯一流末位置；允许相同 EOF 重复。冲突 EOF、EOF 在已接收字节之前或数据超出已知 EOF 均抛 ValueError。EOF 标记可位于当前窗口之外；标记本身不占容量。

## Edge Cases

空数据、零长度读取、重复片段、跨窗口截断、缺口、同偏移不同内容和应用读空均需处理。缓存字节总数不超过 capacity；处理超长输入时工作量应随接收交集而非输入长度增长；可用字节级实现，常规插入开销 O(窗口交集 + 新提升字节)，空间 O(capacity)。

## Build & Run

在仓库根目录运行：

```sh
make build
make grade LAB=lab02_reassembly
make grade MODE=reference LAB=lab02_reassembly
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

**为什么读后仍需重传窗口外字节？** 窗口外的内容没有被保存；读取只是扩大接收范围。

## Further Exploration

比较按字节与区间存储的空间和时间成本，设计基准并解释权衡。
