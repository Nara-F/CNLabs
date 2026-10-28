"""路由实验的独立数据模型。"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Route:
    network: str
    interface: str
    next_hop: str | None = None

@dataclass(frozen=True)
class Frame:
    kind: str                 # 'arp' 或 'ipv4'
    interface: str
    target: str               # ARP 的目标 IP；IPv4 的目标 MAC
    payload: bytes = b''
