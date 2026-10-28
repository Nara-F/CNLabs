"""实现路由器：见 README。"""
from labs.lab05_routing.api import INFINITY, Route

class Router:
    def __init__(self, name: str, timeout: int = 3):
        raise NotImplementedError
    def set_link(self, neighbor: str, cost: int | None):
        raise NotImplementedError
    def receive(self, neighbor: str, vector: dict[str, int]):
        raise NotImplementedError
    def tick(self):
        raise NotImplementedError
    def advertise(self, neighbor: str) -> dict[str, int]:
        raise NotImplementedError
    def routes(self) -> dict[str, Route]:
        raise NotImplementedError
