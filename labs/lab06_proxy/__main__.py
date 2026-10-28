"""python -m labs.lab06_proxy [port] 启动学生代理。"""
import sys
import threading
from .student import ProxyServer

def main():
    server = ProxyServer(port=int(sys.argv[1]) if len(sys.argv)>1 else 0)
    port = server.start()
    print(f'代理监听 127.0.0.1:{port}', flush=True)
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()

if __name__ == '__main__':
    main()
