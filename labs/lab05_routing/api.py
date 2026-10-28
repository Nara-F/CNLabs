"""距离向量实验公共数据类型。"""
from dataclasses import dataclass

INFINITY = 16
@dataclass(frozen=True)
class Route:
    metric: int
    next_hop: str | None
