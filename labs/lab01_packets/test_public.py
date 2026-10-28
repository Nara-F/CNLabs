import random
import unittest
from netlab.testing import load_impl, graded
from labs.lab01_packets.api import IPv4Packet, UDPSegment
M = load_impl('lab01_packets')
A, B = '192.0.2.1', '198.51.100.2'

class PacketTests(unittest.TestCase):
    @graded(category='functional', points=5)
    def test_checksum_vector(self):
        self.assertEqual(M.checksum(bytes.fromhex('0001f203f4f5f6f7')), 0x220d)
    @graded(category='boundary', points=5)
    def test_checksum_empty(self): self.assertEqual(M.checksum(b''), 65535)
    @graded(category='boundary', points=5)
    def test_checksum_odd(self): self.assertEqual(M.checksum(b'\x01'), 0xfeff)
    @graded(category='functional', points=5)
    def test_ipv4_roundtrip(self):
        p = IPv4Packet(A,B,17,b'hello',42,123,0x4000,4)
        self.assertEqual(M.decode_ipv4(M.encode_ipv4(p)), p)
    @graded(category='functional', points=5)
    def test_ipv4_header(self):
        b = M.encode_ipv4(IPv4Packet(A,B,17,b''))
        self.assertEqual(b.hex(), '450000140000000040118ea2c0000201c6336402')
    @graded(category='functional', points=5)
    def test_udp_roundtrip(self):
        p = UDPSegment(1,65535,b'abc'); self.assertEqual(M.decode_udp(M.encode_udp(p,A,B),A,B),p)
    @graded(category='boundary', points=5)
    def test_udp_empty(self):
        p=UDPSegment(0,0,b''); self.assertEqual(M.decode_udp(M.encode_udp(p,A,B),A,B),p)
    @graded(category='error', points=5)
    def test_ip_short(self):
        with self.assertRaises(ValueError): M.decode_ipv4(b'\x45')
    @graded(category='error', points=5)
    def test_ip_corrupt(self):
        b=bytearray(M.encode_ipv4(IPv4Packet(A,B,1,b'x'))); b[8]^=1
        with self.assertRaises(ValueError): M.decode_ipv4(bytes(b))
    @graded(category='error', points=5)
    def test_ip_options(self):
        b=bytearray(M.encode_ipv4(IPv4Packet(A,B,1,b''))); b[0]=0x46
        with self.assertRaises(ValueError): M.decode_ipv4(bytes(b))
    @graded(category='error', points=5)
    def test_ip_extra(self):
        with self.assertRaises(ValueError): M.decode_ipv4(M.encode_ipv4(IPv4Packet(A,B,1,b''))+b'x')
    @graded(category='error', points=5)
    def test_ip_bad_address(self):
        with self.assertRaises(ValueError): M.encode_ipv4(IPv4Packet('bad',B,1,b''))
    @graded(category='error', points=5)
    def test_ip_bad_ttl(self):
        with self.assertRaises(ValueError): M.encode_ipv4(IPv4Packet(A,B,1,b'',256))
    @graded(category='error', points=5)
    def test_udp_short(self):
        with self.assertRaises(ValueError): M.decode_udp(b'',A,B)
    @graded(category='error', points=5)
    def test_udp_corrupt(self):
        b=bytearray(M.encode_udp(UDPSegment(4,5,b'hi'),A,B)); b[-1]^=1
        with self.assertRaises(ValueError): M.decode_udp(bytes(b),A,B)
    @graded(category='error', points=5)
    def test_udp_pseudo(self):
        b=M.encode_udp(UDPSegment(1,2,b'hi'),A,B)
        with self.assertRaises(ValueError): M.decode_udp(b,B,A.replace('1','3'))
    @graded(category='boundary', points=5)
    def test_udp_no_checksum(self):
        self.assertEqual(M.decode_udp(bytes.fromhex('0001000200080000'),A,B),UDPSegment(1,2,b''))
    @graded(category='error', points=5)
    def test_udp_length(self):
        with self.assertRaises(ValueError): M.decode_udp(bytes.fromhex('0001000200090000'),A,B)
    @graded(category='interface', points=5)
    def test_wrong_type(self):
        with self.assertRaises(TypeError): M.checksum('abc')
    @graded(category='stress', points=5)
    def test_roundtrip_random(self):
        r=random.Random(19)
        for _ in range(100):
            p=IPv4Packet(A,B,r.randrange(256),r.randbytes(r.randrange(200)),r.randrange(256))
            self.assertEqual(M.decode_ipv4(M.encode_ipv4(p)),p)
