import unittest
from netlab.testing import load_impl, graded
from labs.lab05_routing.api import Route, INFINITY
M = load_impl('lab05_routing')

class RoutingTests(unittest.TestCase):
    def setUp(self): self.r = M.Router('A', timeout=2)
    @graded(category='basic', points=5)
    def test_self(self): self.assertEqual(self.r.routes(), {'A': Route(0,None)})
    @graded(category='basic', points=5)
    def test_direct(self):
        self.r.set_link('B',2); self.assertEqual(self.r.routes()['B'],Route(2,'B'))
    @graded(category='basic', points=5)
    def test_change_cost(self):
        self.r.set_link('B',2); self.r.set_link('B',4); self.assertEqual(self.r.routes()['B'].metric,4)
    @graded(category='basic', points=5)
    def test_disconnect(self):
        self.r.set_link('B',2); self.r.set_link('B',None); self.assertNotIn('B',self.r.routes())
    @graded(category='distance_vector', points=5)
    def test_learn(self):
        self.r.set_link('B',2); self.r.receive('B',{'C':3}); self.assertEqual(self.r.routes()['C'],Route(5,'B'))
    @graded(category='distance_vector', points=5)
    def test_replace(self):
        self.r.set_link('B',2); self.r.receive('B',{'C':3}); self.r.receive('B',{}); self.assertNotIn('C',self.r.routes())
    @graded(category='distance_vector', points=5)
    def test_poison(self):
        self.r.set_link('B',2); self.r.receive('B',{'C':3}); self.assertEqual(self.r.advertise('B')['C'],16)
    @graded(category='distance_vector', points=5)
    def test_other_advertisement(self):
        self.r.set_link('B',2); self.r.set_link('D',1); self.r.receive('B',{'C':3}); self.assertEqual(self.r.advertise('D')['C'],5)
    @graded(category='distance_vector', points=5)
    def test_tie(self):
        self.r.set_link('C',1); self.r.set_link('B',1); self.r.receive('B',{'D':2}); self.r.receive('C',{'D':2}); self.assertEqual(self.r.routes()['D'],Route(3,'B'))
    @graded(category='distance_vector', points=5)
    def test_infinity(self):
        self.r.set_link('B',2); self.r.receive('B',{'C':14}); self.assertNotIn('C',self.r.routes())
    @graded(category='expiry', points=5)
    def test_expire(self):
        self.r.set_link('B',2); self.r.receive('B',{'C':1}); self.r.tick(); self.r.tick(); self.assertNotIn('C',self.r.routes()); self.assertIn('B',self.r.routes())
    @graded(category='expiry', points=5)
    def test_refresh(self):
        self.r.set_link('B',2); self.r.receive('B',{'C':1}); self.r.tick(); self.r.receive('B',{'C':1}); self.r.tick(); self.assertIn('C',self.r.routes())
    @graded(category='input', points=5)
    def test_invalid_cost(self):
        with self.assertRaises(ValueError): self.r.set_link('B',16)
    @graded(category='input', points=5)
    def test_self_link(self):
        with self.assertRaises(ValueError): self.r.set_link('A',1)
    @graded(category='input', points=5)
    def test_unknown_sender(self):
        with self.assertRaises(ValueError): self.r.receive('B',{})
    @graded(category='input', points=5)
    def test_bad_vector(self):
        self.r.set_link('B',1)
        with self.assertRaises(ValueError): self.r.receive('B',{'C':-1})
    @graded(category='input', points=5)
    def test_bad_advertise(self):
        with self.assertRaises(ValueError): self.r.advertise('B')
    @graded(category='isolation', points=5)
    def test_input_copy(self):
        self.r.set_link('B',1); v={'C':2}; self.r.receive('B',v); v['C']=9; self.assertEqual(self.r.routes()['C'].metric,3)
    @graded(category='isolation', points=5)
    def test_output_copy(self):
        self.r.routes().clear(); self.assertIn('A',self.r.routes())
    @graded(category='distance_vector', points=5)
    def test_direct_precedence(self):
        self.r.set_link('B',2); self.r.receive('B',{'B':15}); self.assertEqual(self.r.routes()['B'].metric,2)
