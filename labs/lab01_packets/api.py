"""实验 1 的不可变数据模型；地址使用 IPv4Address 可接受的字符串。"""
from dataclasses import dataclass

@dataclass(frozen=True)
class IPv4Packet:
    src: str
    dst: str
    protocol: int
    payload: bytes
    ttl: int = 64
    identification: int = 0
    flags_offset: int = 0
    tos: int = 0

@dataclass(frozen=True)
class UDPSegment:
    src_port: int
    dst_port: int
    payload: bytes
