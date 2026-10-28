# 实验 06：并发 HTTP 缓存代理

## 概览（Overview）

本实验属于 CNLabs，独立完成学生接口后通过公开和隐藏测试验证。

**学习目标**

构造真实 TCP 代理，掌握 HTTP 报文边界、短读短写、线程同步、有界资源和缓存资格。先实现顺序转发，再增加并发和缓存。

## 学习目标（Learning Objectives）

用真实 TCP 连接验证 HTTP 报文边界、并发处理和共享缓存。

**前置知识**

熟悉 Python socket、线程和 HTTP 首部；了解 HTTP/1.0 连接关闭与 Content-Length。建议 16–22 小时（含测试报告），环境为 Linux 与 Python 3.11+，仅使用标准库。

## 先修要求（Prerequisites）

使用 Python 3.11 或更新版本，具备基本网络、字节序和标准库知识。

## 背景（Background）

协议头中的长度、状态和边界都由接收者验证；本课程为可复现实验定义明确子集。

**实验范围**

代理仅处理明文 HTTP 的绝对 URI GET，使用 HTTP/1.0 请求上游并关闭连接。本实验明确不实现 HTTPS、CONNECT、请求体、持久连接、chunked 编码或完整 RFC 缓存；禁止测试访问外网。

## 必读资料（Required Readings）

请先阅读第 18 节所列 RFC 和课程原始资料中与本实验相关的章节。

## 架构总览（Architecture Overview）

数据模型位于 api.py，学生实现位于 student.py；测试通过公开接口调用。

**Request**

`Request(method, target, version, headers)` 是不可变 dataclass；headers 为 `(名称, 值)` 元组的元组，保留输入顺序、大小写和重复字段。目标地址为请求行字符串。

## 起始代码指南（Starter Code Guide）

只在 student.py 中实现约定接口，允许使用 Python 标准库，不得导入 instructor。

## 分阶段任务（Tasks）

先完成基础功能，再实现边界与异常，最后通过独立向量、状态轨迹和压力测试检查。

**推荐步骤**

先单测 parse_request 和 LRU，再实现单请求转发与严谨报文边界；增加失败清理；最后使用线程、信号量及锁。以不同 URL 创建并发请求，证明慢 origin 不阻塞另一个请求。

阶段 1：解析与顺序代理；阶段 2：有限线程和关闭；阶段 3：原子 LRU 与缓存资格；阶段 4：分片、慢连接和压力测试。

## 接口规范（Interface Specifications）

**请求解析**

`parse_request(data: bytes) -> Request` 接受且仅接受以 CRLF CRLF 结尾的完整首部，不含额外字节。首行为三个空格分隔部分，method 和字段名必须为 HTTP token，版本仅 HTTP/1.0 或 HTTP/1.1；值去除首尾空格或水平制表符，拒绝控制字符、折行、缺冒号。按 ISO-8859-1 解码。格式错误 ValueError，非 bytes TypeError。

**缓存接口**

`LRUCache(max_bytes, max_object, *, max_entries=1024, max_key=4096)`：前两项为非负整数，后两项为正整数，均不接受 bool，否则 ValueError。`get(key)` 返回 bytes 或 None，命中提升为最近使用；`put(key, value)` 接受 str 和 bytes，否则 TypeError。值长度超过任一字节限制或键的 UTF-8 编码超过 max_key 字节时返回 False 且保留旧值；否则原子替换、按最久未使用顺序驱逐，最多保留 max_entries 项，返回 True；即使值为空也计入项数上限。大小只计算值字节，不计键。方法线程安全；单次操作 O(1) 均摊，驱逐按实际对象数计。

**服务器生命周期**

`ProxyServer(host='127.0.0.1', port=0, *, max_workers=16, timeout=2.0, max_header=16384, max_response=1048576, cache_bytes=1048576, max_object=102400)`。仅允许监听 127.0.0.1；端口 0..65535；max_workers 为正整数，timeout 为有限正数，两个报文限制均为不小于 64 的整数；上述数值不接受 bool。参数无效 ValueError。`start() -> int` 启动后台监听并返回实际端口，重复启动或关闭后启动抛 RuntimeError。`shutdown()` 关闭监听和活动客户端并等待工作线程；可多次调用。

## 行为要求（Behavioral Requirements）

相同输入和状态应得到确定结果；所有未声明支持的协议扩展不属于实现范围。

**资源与并发**

最多 max_workers 个活跃处理线程，超限的新客户端返回 503 并关闭。每个连接的 socket 操作受 timeout 秒限制。每次连接处理一个请求，成功或失败均关闭客户端；shutdown 不遗留监听。测试使用事件同步，不依赖计时猜测并发。

**客户端请求**

累计读到 CRLF CRLF；超过 max_header 返回 431，截断或格式无效返回 400。只支持 GET，其他方法返回 501。绝对 URI 必须是 `http://host[:port]/path[?query]`，host 采用 IPv4 或 DNS 名称（不含 IPv6 字面量），缺省路径为 `/`，禁止 userinfo、fragment、非法端口（显式 0、空端口或超过 65535）、请求体及 Content-Length 或 Transfer-Encoding 首部。请求行或首部后出现额外字节也视为无效。

**上游请求**

将绝对 URI 改为 origin-form，发送 `GET path HTTP/1.0`、规范 Host（非 80 端口包含端口号）和 `Connection: close`。保留其他端到端首部；删除原 Host、Connection、Proxy-Connection、Keep-Alive、TE、Trailer、Transfer-Encoding、Upgrade、Proxy-Authorization、Proxy-Authenticate，以及 Connection 值中列出的首部，名称不区分大小写。

**上游响应**

读取完整首部和响应体，响应总字节数不超过 max_response，首部不超过 max_header。接受 HTTP/1.0 或 1.1 状态行；Content-Length 至多出现一次且为十进制非负整数。若有长度，读取恰好那么多字节，截断或已随首部一起读入的多余字节失败；之后到达的多余字节不属于该响应，连接关闭时丢弃；没有长度时读取到 EOF。拒绝 Transfer-Encoding。删除 hop-by-hop 响应字段及 Connection 指名字段，写入实际 Content-Length 和 Connection: close，再返回二进制数据。此子集不处理特殊无主体状态及 chunked。

**缓存资格**

key 是小写主机名、有效端口和原始路径/查询组成的规范绝对 URI（端口 80 省略）。请求有 Authorization 时不读也不写缓存。仅完整成功的 200 响应可缓存；原始上游首部有 Set-Cookie、Vary 或 Cache-Control 的 private、no-store、no-cache 指令则不缓存，即便 Connection 将这些字段列为逐跳首部。缓存完整的重写后响应，仍受 max_object 和总字节限额约束。无需 TTL、条件请求或合并同时未命中请求。

**错误语义**

失败响应为 HTTP/1.0，包含 Content-Length 和 Connection: close。请求解析失败 400，首部过大 431，方法不支持 501，满载 503，上游连接、协议、截断或响应过大 502，socket 超时 504。完整响应验证结束后再发送，故不向客户端泄漏半个成功响应。

**缓存模型：** 这是教学用的受限缓存，不实施 RFC 9111 新鲜度或重验证；假设本实验的可缓存对象在一次代理运行期间保持不变；合格对象一直保存至 LRU 驱逐或服务器关闭。请求 Cache-Control 的 no-store、no-cache、private 同样绕过读取与写入。大响应先写入临时文件验证，再分块发送，不将整个对象放入内存；可缓存的小对象才装入内存。

## 边界情况（Edge Cases）

覆盖空输入、精确上限、超过上限、非法类型、截断及重复调用。

## 构建与运行（Build & Run）

在仓库根目录运行 `make grade LAB=lab06_proxy MODE=student SUITE=public`；教师可运行 `make grade LAB=lab06_proxy MODE=reference SUITE=full`。`make build` 编译检查。

## 调试指南（Debugging Guide）

缩小输入、逐字段打印并与独立向量比较；检查资源释放和错误分支。

**思考与排错**

`recv` 可返回少于请求长度的数据，EOF 不等于一条完整响应。检查 Content-Length、超时与 finally 中的关闭路径。考虑请求共享缓存为何对 Authorization 和 Vary 不安全，以及单线程缓存更新为何仍需锁。

## 测试（Testing）

**测试**

`test_public.py` 的 origin 是真实 loopback socket，OS 分配端口，不依赖互联网；覆盖短分片、半关闭、缓存、请求改写。隐藏测试增加大二进制、上游失败、截断、并发事件、超时、LRU 及缓存资格。根目录 `make grade` 运行评分；Linux 沙箱必须允许创建本机 TCP socket。

## 评分（Grading）

公开和隐藏测试各以 100 分计，完整评分按公开 60%、隐藏 40% 合成；每个测试的权重与类别见 `@graded`。

## 提交（Submission）

**文件和提交**

`api.py` 提供 `Request`，仅修改提交 `student.py`；不得导入 instructor。`python -m labs.lab06_proxy [port]` 运行学生代理，端口省略时由操作系统分配。Ctrl-C 停止。根目录 `make grade` 运行统一评分。

## 常见问题（FAQ）

问：为什么大响应先写临时文件？答：必须验证完整长度后才能决定返回成功，同时避免把大对象整体保存在内存。

## 进一步探索（Further Exploration）

实现带显式时钟的 max-age 和条件重验证，分析 Vary 对缓存键的影响。

**官方资料**

[CMU CS:APP Proxy Lab](https://csapp.cs.cmu.edu/3e/proxylab.pdf) 的顺序、并发、缓存分阶段启发本实验；评分规则和接口按本课程契约。[RFC 9110 HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110)、[RFC 9111 HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111)、[RFC 9112 HTTP/1.1](https://www.rfc-editor.org/rfc/rfc9112) 规定完整协议；本实验只实现上述明确子集。
