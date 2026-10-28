"""教学传输协议的数据类型与接口。时间为调用者提供的非负秒数。"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Segment:
    seq: int
    data: bytes = b''
    fin: bool = False

@dataclass(frozen=True)
class Ack:
    next_seq: int
    window: int

class Sender:
    def __init__(self, data: bytes, mss: int, rto: float): raise NotImplementedError
    def send(self, now: float) -> list[Segment]: raise NotImplementedError
    def ack(self, ack: Ack, now: float) -> None: raise NotImplementedError
    def tick(self, now: float) -> list[Segment]: raise NotImplementedError
    @property
    def finished(self) -> bool: raise NotImplementedError

class Receiver:
    def __init__(self, capacity: int): raise NotImplementedError
    def receive(self, segment: Segment) -> Ack: raise NotImplementedError
    def read(self, n: int) -> bytes: raise NotImplementedError
    def ack(self) -> Ack: raise NotImplementedError
    @property
    def finished(self) -> bool: raise NotImplementedError
