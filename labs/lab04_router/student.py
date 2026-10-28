"""在不依赖其他学生实验的情况下实现路由器。"""
from labs.lab04_router.api import Route, Frame

class Router:
    def __init__(self, routes, *, cache_ttl=30, retry_interval=1, max_attempts=3, queue_limit=16, max_pending=256, max_cache=256):
        raise NotImplementedError

    def lookup(self, destination):
        raise NotImplementedError

    def receive(self, packet, now):
        raise NotImplementedError

    def advance(self, now):
        raise NotImplementedError

    def learn(self, interface, ip, mac, now):
        raise NotImplementedError
