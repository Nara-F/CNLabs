"""有界字节流重组接口。所有位置均为从零开始的绝对字节偏移。"""
from __future__ import annotations

class Reassembler:
    def __init__(self, capacity: int):
        if type(capacity) is not int: raise TypeError('容量必须为整数')
        if capacity <= 0: raise ValueError('容量必须为正')
        raise NotImplementedError
    def insert(self, index: int, data: bytes, eof: bool = False) -> None:
        raise NotImplementedError
    def read(self, n: int) -> bytes:
        raise NotImplementedError
    @property
    def pending(self) -> int: raise NotImplementedError
    @property
    def available(self) -> int: raise NotImplementedError
    @property
    def finished(self) -> bool: raise NotImplementedError
