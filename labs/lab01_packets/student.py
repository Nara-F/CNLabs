"""请完成这里的算法；不得导入 instructor。"""
from labs.lab01_packets.api import IPv4Packet, UDPSegment

def checksum(data: bytes) -> int:
    raise NotImplementedError

def encode_ipv4(packet: IPv4Packet) -> bytes:
    raise NotImplementedError

def decode_ipv4(data: bytes) -> IPv4Packet:
    raise NotImplementedError

def encode_udp(segment: UDPSegment, src: str, dst: str) -> bytes:
    raise NotImplementedError

def decode_udp(data: bytes, src: str, dst: str) -> UDPSegment:
    raise NotImplementedError
