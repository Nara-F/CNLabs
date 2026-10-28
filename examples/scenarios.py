"""展示独立实验轨迹；使用 NETLAB_IMPL_ROOT 选择实现目录。"""
import argparse
from netlab.testing import load_impl


def lab01():
    m = load_impl('lab01_packets')
    packet = m.IPv4Packet('192.0.2.1', '198.51.100.2', 17, b'abc', ttl=5)
    wire = m.encode_ipv4(packet)
    print('输入 IPv4:', packet)
    print('编码 hex:', wire.hex())
    print('解码:', m.decode_ipv4(wire))


def lab02():
    m = load_impl('lab02_reassembly'); r = m.Reassembler(4)
    for index, data in ((2, b'cd'), (0, b'ab')):
        r.insert(index, data)
        print('插入:', index, data, 'pending:', r.pending, 'available:', r.available)
    print('读取:', r.read(2))
    r.insert(4, b'ef', True)
    print('读取:', r.read(4), 'finished:', r.finished)


def lab03():
    m = load_impl('lab03_transport')
    s = m.Sender(b'ab', 2, 1); r = m.Receiver(4)
    first = s.send(0); print('时间 0，发送:', first)
    ack = r.receive(first[0]); print('接收端 ACK:', ack); s.ack(ack, 0)
    following = s.send(0); print('后续发送（暂丢弃）:', following)
    retry = s.tick(1); print('时间 1，重传:', retry)
    for seg in retry: s.ack(r.receive(seg), 1)
    for seg in following[1:]: s.ack(r.receive(seg), 1)
    print('应用读取:', r.read(4), '发送完成:', s.finished, '接收完成:', r.finished)


def lab04(integrated=False):
    m = load_impl('lab04_router')
    if integrated:
        packets = load_impl('lab01_packets')
        wire = packets.encode_ipv4(packets.IPv4Packet('192.0.2.1', '198.51.100.2', 17, b'abc', ttl=5))
        print('实验 01 编码:', wire.hex())
    else:
        # 预先编码的完整 IPv4 报文，示例独立于实验 01 实现。
        wire = bytes.fromhex('45000017000000000511c99fc0000201c6336402616263')
    r = m.Router([m.Route('0.0.0.0/0', 'eth0', '192.0.2.254')])
    print('输入 IPv4 hex:', wire.hex())
    print('接收事件:', r.receive(wire, 0))
    print('学习地址释放队列:', r.learn('eth0', '192.0.2.254', '02:00:00:00:00:01', 0))


def lab05():
    m = load_impl('lab05_routing')
    a = m.Router('A'); b = m.Router('B'); c = m.Router('C')
    a.set_link('B', 1); b.set_link('A', 1); b.set_link('C', 2); c.set_link('B', 2)
    a.receive('B', b.advertise('A'))
    print('A 从 B 收到通告后的路由:', a.routes())
    print('A 发往 B 的通告（毒性逆转）:', a.advertise('B'))
    a.set_link('B', None); print('链路断开后的路由:', a.routes())


def main():
    parser = argparse.ArgumentParser(description='运行网络实验状态轨迹')
    parser.add_argument('lab', choices=[f'lab{i:02d}_{name}' for i, name in enumerate(('packets','reassembly','transport','router','routing'), 1)])
    parser.add_argument('--integrated', action='store_true', help='实验 04 使用实验 01 的编码结果')
    args = parser.parse_args()
    if args.integrated and args.lab != 'lab04_router': parser.error('--integrated 仅用于 lab04_router')
    if args.lab == 'lab04_router': lab04(args.integrated)
    else: {'lab01_packets':lab01, 'lab02_reassembly':lab02, 'lab03_transport':lab03, 'lab05_routing':lab05}[args.lab]()


if __name__ == '__main__':
    main()
