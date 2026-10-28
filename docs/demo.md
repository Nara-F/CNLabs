# 可执行实验轨迹

在仓库根目录运行以下命令，默认加载各实验的 student.py。先完成对应实现，再比较输入、状态及输出。

```sh
python -m examples.scenarios lab01_packets
python -m examples.scenarios lab02_reassembly
python -m examples.scenarios lab03_transport
python -m examples.scenarios lab04_router
python -m examples.scenarios lab05_routing
```

01 展示 IPv4 编解码；02 展示乱序、窗口前移与 EOF；03 模拟数据丢失与定时重传；04 使用固定 IPv4 字节展示 ARP 与队列释放；05 展示距离向量和毒性逆转。04 默认使用独立报文字节，不依赖实验 01。跨层示例 `python -m examples.scenarios lab04_router --integrated` 使用实验 01 生成报文交给实验 04，需要两个实现均已完成。实验 06 的 socket 代理入口见其 README。

课程维护者可将 `NETLAB_IMPL_ROOT=instructor/reference` 加在命令前，使用完整仓库中的参考实现校准轨迹。
