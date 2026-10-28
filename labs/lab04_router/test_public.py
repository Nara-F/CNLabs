import struct
import unittest
from netlab.testing import load_impl, graded
from labs.lab04_router.api import Route, Frame
M=load_impl('lab04_router')

def packet(ttl=3, dst='10.1.2.3'):
    import ipaddress
    h=bytearray(struct.pack('!BBHHHBBH4s4s',0x45,0,23,1,0,ttl,17,0,ipaddress.IPv4Address('192.0.2.1').packed,ipaddress.IPv4Address(dst).packed))
    s=sum(int.from_bytes(h[i:i+2],'big') for i in range(0,20,2)); s=(s&65535)+(s>>16); s=(s&65535)+(s>>16); h[10:12]=struct.pack('!H',(~s)&65535)
    return bytes(h)+b'abc'

def router(**kw): return M.Router([Route('0.0.0.0/0','wan','192.0.2.2'),Route('10.0.0.0/8','lan')],**kw)

class RouterTests(unittest.TestCase):
    @graded(category='functional', points=5)
    def test_longest(self): self.assertEqual(router().lookup('10.1.2.3').interface,'lan')
    @graded(category='functional', points=5)
    def test_default(self): self.assertEqual(router().lookup('8.8.8.8').interface,'wan')
    @graded(category='boundary', points=5)
    def test_none(self): self.assertIsNone(M.Router([]).lookup('8.8.8.8'))
    @graded(category='functional', points=5)
    def test_arp(self): self.assertEqual(router().receive(packet(),0),[Frame('arp','lan','10.1.2.3')])
    @graded(category='state', points=5)
    def test_queue(self):
        r=router(); r.receive(packet(),0); self.assertEqual(r.receive(packet(),0),[]); self.assertEqual(len(r.learn('lan','10.1.2.3','00:11:22:33:44:55',0)),2)
    @graded(category='integration', points=5)
    def test_forward(self):
        r=router(); r.learn('lan','10.1.2.3','00:11:22:33:44:55',0); f=r.receive(packet(),0)[0]; self.assertEqual((f.kind,f.target,f.payload[8],f.payload[20:]),('ipv4','00:11:22:33:44:55',2,b'abc')); self.assertEqual(sum(int.from_bytes(f.payload[i:i+2],'big') for i in range(0,20,2))%65535,0)
    @graded(category='state', points=5)
    def test_retry(self):
        r=router(); r.receive(packet(),0); self.assertEqual(r.advance(1),[Frame('arp','lan','10.1.2.3')])
    @graded(category='state', points=5)
    def test_no_early_retry(self):
        r=router(); r.receive(packet(),0); self.assertEqual(r.advance(.9),[])
    @graded(category='state', points=5)
    def test_expire_pending(self):
        r=router(); r.receive(packet(),0); self.assertEqual(len(r.advance(3)),2); self.assertEqual(r.learn('lan','10.1.2.3','00:11:22:33:44:55',3),[])
    @graded(category='state', points=5)
    def test_cache_expiry(self):
        r=router(cache_ttl=2); r.learn('lan','10.1.2.3','00:11:22:33:44:55',0); self.assertEqual(r.receive(packet(),2)[0].kind,'arp')
    @graded(category='boundary', points=5)
    def test_ttl_one(self): self.assertEqual(router().receive(packet(1),0),[])
    @graded(category='error', points=5)
    def test_corrupt(self):
        b=bytearray(packet()); b[8]^=1; self.assertEqual(router().receive(bytes(b),0),[])
    @graded(category='error', points=5)
    def test_truncated(self): self.assertEqual(router().receive(b'\x45',0),[])
    @graded(category='error', points=5)
    def test_clock(self):
        r=router(); r.advance(2)
        with self.assertRaises(ValueError): r.advance(1)
    @graded(category='error', points=5)
    def test_invalid_mac(self):
        with self.assertRaises(ValueError): router().learn('lan','10.1.2.3','invalid',0)
    @graded(category='boundary', points=5)
    def test_queue_limit(self):
        r=router(queue_limit=1); r.receive(packet(),0); r.receive(packet(),0); self.assertEqual(len(r.learn('lan','10.1.2.3','00:11:22:33:44:55',0)),1)
    @graded(category='functional', points=5)
    def test_next_hop(self): self.assertEqual(router().receive(packet(dst='8.8.8.8'),0),[Frame('arp','wan','192.0.2.2')])
    @graded(category='state', points=5)
    def test_learn_cache(self):
        r=router(); r.learn('lan','10.1.2.3','AA:BB:CC:DD:EE:FF',0); self.assertEqual(r.receive(packet(),0)[0].target,'aa:bb:cc:dd:ee:ff')
    @graded(category='error', points=5)
    def test_bad_route(self):
        with self.assertRaises(ValueError): M.Router([Route('10.1.2.3/8','x')])
    @graded(category='interface', points=5)
    def test_wrong_type(self):
        with self.assertRaises(TypeError): router().receive('bad',0)
