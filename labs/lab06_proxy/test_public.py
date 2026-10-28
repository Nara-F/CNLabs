import socket
import threading
import unittest
from netlab.testing import load_impl, graded
from labs.lab06_proxy.api import Request
M=load_impl('lab06_proxy')

class Origin:
    def __init__(self, response=None, callback=None):
        self.sock=socket.socket(); self.sock.bind(('127.0.0.1',0)); self.sock.listen(); self.sock.settimeout(.2); self.port=self.sock.getsockname()[1]
        self.response=response or b'HTTP/1.0 200 OK\r\nContent-Length: 2\r\n\r\nok'; self.callback=callback; self.count=0; self.requests=[]; self.stop=threading.Event(); self.threads=[]
        self.thread=threading.Thread(target=self.run,daemon=True); self.thread.start()
    def run(self):
        while not self.stop.is_set():
            try: c,_=self.sock.accept()
            except socket.timeout: continue
            except OSError: break
            t=threading.Thread(target=self.handle,args=(c,),daemon=True); self.threads.append(t); t.start()
    def handle(self,c):
        with c:
            c.settimeout(2); data=b''
            try:
                while b'\r\n\r\n' not in data:
                    b=c.recv(4096)
                    if not b: return
                    data+=b
                self.count+=1; self.requests.append(data)
                if self.callback: self.callback(c,data)
                else: c.sendall(self.response)
            except OSError: pass
    def close(self):
        self.stop.set(); self.sock.close(); self.thread.join(1)
        for t in self.threads: t.join(2)

def fetch(port, target, method='GET', headers=b'', fragments=False):
    with socket.create_connection(('127.0.0.1',port),timeout=3) as c:
        c.settimeout(3); wire=method.encode()+b' '+target.encode()+b' HTTP/1.1\r\n'+headers+b'\r\n'
        if fragments:
            for b in wire: c.sendall(bytes([b]))
        else: c.sendall(wire)
        c.shutdown(socket.SHUT_WR); out=b''
        while True:
            chunk=c.recv(65536)
            if not chunk: return out
            out+=chunk

class ProxyTests(unittest.TestCase):
    def setUp(self):
        self.origin=Origin(); self.proxy=M.ProxyServer(); self.port=self.proxy.start(); self.url=f'http://127.0.0.1:{self.origin.port}/x'
    def tearDown(self): self.proxy.shutdown(); self.origin.close()
    @graded(category='interface',points=5)
    def test_parse(self):
        self.assertEqual(M.parse_request(b'GET http://example.com/ HTTP/1.1\r\nX-A: a\r\n\r\n'),Request('GET','http://example.com/','HTTP/1.1',(('X-A','a'),)))
    @graded(category='error',points=5)
    def test_parse_invalid(self):
        with self.assertRaises(ValueError): M.parse_request(b'GET / HTTP/1.1\n\n')
    @graded(category='error',points=5)
    def test_parse_field(self):
        with self.assertRaises(ValueError): M.parse_request(b'GET / HTTP/1.1\r\nBad Field: x\r\n\r\n')
    @graded(category='boundary',points=5)
    def test_cache_empty(self): self.assertIsNone(M.LRUCache(10,10).get('missing'))
    @graded(category='functional',points=5)
    def test_cache_get(self):
        c=M.LRUCache(10,10); self.assertTrue(c.put('a',b'xyz')); self.assertEqual(c.get('a'),b'xyz')
    @graded(category='state',points=5)
    def test_cache_lru(self):
        c=M.LRUCache(4,4); c.put('a',b'aa'); c.put('b',b'bb'); c.get('a'); c.put('c',b'cc'); self.assertIsNone(c.get('b')); self.assertEqual(c.get('a'),b'aa')
    @graded(category='boundary',points=5)
    def test_cache_object_limit(self):
        c=M.LRUCache(10,2); self.assertFalse(c.put('a',b'abc')); self.assertIsNone(c.get('a'))
    @graded(category='state',points=5)
    def test_cache_replace(self):
        c=M.LRUCache(3,3); c.put('a',b'aaa'); c.put('a',b'b'); c.put('b',b'cc'); self.assertEqual(c.get('a'),b'b')
    @graded(category='integration',points=5)
    def test_fetch(self): self.assertTrue(fetch(self.port,self.url).endswith(b'\r\n\r\nok'))
    @graded(category='integration',points=5)
    def test_origin_form(self):
        fetch(self.port,self.url+'?q=1'); self.assertTrue(self.origin.requests[0].startswith(b'GET /x?q=1 HTTP/1.0\r\n'))
    @graded(category='integration',points=5)
    def test_cache_hit(self):
        a=fetch(self.port,self.url); b=fetch(self.port,self.url); self.assertEqual(a,b); self.assertEqual(self.origin.count,1)
    @graded(category='integration',points=5)
    def test_fragmented(self): self.assertIn(b'200',fetch(self.port,self.url,fragments=True).split(b'\r\n')[0])
    @graded(category='error',points=5)
    def test_method(self): self.assertIn(b'501',fetch(self.port,self.url,method='POST').split(b'\r\n')[0])
    @graded(category='error',points=5)
    def test_relative_target(self): self.assertIn(b'400',fetch(self.port,'/x').split(b'\r\n')[0])
    @graded(category='integration',points=5)
    def test_hop_headers(self):
        fetch(self.port,self.url,headers=b'Connection: X-Secret\r\nX-Secret: yes\r\nX-Keep: ok\r\n'); req=self.origin.requests[0].lower(); self.assertNotIn(b'x-secret:',req); self.assertIn(b'x-keep: ok',req)
    @graded(category='state',points=5)
    def test_authorization(self):
        fetch(self.port,self.url,headers=b'Authorization: token\r\n'); fetch(self.port,self.url,headers=b'Authorization: token\r\n'); self.assertEqual(self.origin.count,2)
    @graded(category='error',points=5)
    def test_request_body(self): self.assertIn(b'400',fetch(self.port,self.url,headers=b'Content-Length: 1\r\n').split(b'\r\n')[0])
    @graded(category='boundary',points=5)
    def test_no_query(self):
        fetch(self.port,f'http://127.0.0.1:{self.origin.port}'); self.assertTrue(self.origin.requests[0].startswith(b'GET / HTTP/1.0'))
    @graded(category='error',points=5)
    def test_bad_port(self): self.assertIn(b'400',fetch(self.port,'http://127.0.0.1:999999/').split(b'\r\n')[0])
    @graded(category='interface',points=5)
    def test_bound_port(self): self.assertGreater(self.port,0)
