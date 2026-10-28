"""代理实验的数据模型。headers 保留顺序与重复字段。"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Request:
    method: str
    target: str
    version: str
    headers: tuple[tuple[str, str], ...]
