"""学生实现：请实现 api.py 中的有界重组契约。"""
from labs.lab02_reassembly.api import Reassembler as ReassemblerAPI

class Reassembler(ReassemblerAPI):
    def __init__(self, capacity: int):
        super().__init__(capacity)
