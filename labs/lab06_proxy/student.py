"""完成 HTTP 请求解析、有界 LRU 和并发代理。"""
import socket
import threading
from labs.lab06_proxy.api import Request

def parse_request(data: bytes) -> Request:
    raise NotImplementedError

class LRUCache:
    def __init__(self, max_bytes: int, max_object: int, *, max_entries: int = 1024, max_key: int = 4096):
        self.max_bytes = max_bytes
        self.max_object = max_object
        self.max_entries = max_entries
        self.max_key = max_key
    def get(self, key: str) -> bytes | None:
        raise NotImplementedError
    def put(self, key: str, value: bytes) -> bool:
        raise NotImplementedError

class ProxyServer:
    def __init__(self, host='127.0.0.1', port=0, *, max_workers=16, timeout=2.0, max_header=16384, max_response=1048576, cache_bytes=1048576, max_object=102400):
        self.host, self.port = host, port
        self.max_workers, self.timeout = max_workers, timeout
        self.max_header, self.max_response = max_header, max_response
        self.cache = LRUCache(cache_bytes, max_object)
        self._listener = None
        self._stop = threading.Event()
        self._thread = None

    def start(self) -> int:
        if self._listener is not None or self._stop.is_set():
            raise RuntimeError('已启动或关闭')
        self._listener = socket.socket()
        self._listener.bind((self.host, self.port))
        self._listener.listen()
        self._listener.settimeout(0.2)
        self.port = self._listener.getsockname()[1]
        self._thread = threading.Thread(target=self._accept, daemon=True)
        self._thread.start()
        return self.port

    def _accept(self):
        while not self._stop.is_set():
            try:
                client, _ = self._listener.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            # TODO: 添加有界并发处理；当前骨架立即关闭客户端。
            client.close()

    def shutdown(self) -> None:
        self._stop.set()
        if self._listener is not None:
            self._listener.close()
        if self._thread is not None:
            self._thread.join(timeout=self.timeout + 1)
