import unittest
from netlab.testing import load_impl, graded
M = load_impl('lab03_transport')
from labs.lab03_transport.api import Segment, Ack

class Tests(unittest.TestCase):
    @graded(category='interface', points=4)
    def test_types(self):
        self.assertEqual(Segment(1,b'a',False).seq,1); self.assertEqual(Ack(1,2).window,2)

    @graded(category='interface', points=4)
    def test_sender_init(self):
        s=M.Sender(b'abc',2,1); self.assertFalse(s.finished)

    @graded(category='error', points=4)
    def test_bad_sender(self):
        self.assertRaises(ValueError,M.Sender,b'a',0,1); self.assertRaises(ValueError,M.Sender,b'a',1,0)

    @graded(category='functional', points=4)
    def test_initial_window(self):
        s=M.Sender(b'abc',2,1); self.assertEqual(s.send(0),[Segment(0,b'a')])

    @graded(category='state', points=4)
    def test_ack_window(self):
        s=M.Sender(b'abc',2,1); s.send(0); s.ack(Ack(1,3),0); self.assertEqual(s.send(0),[Segment(1,b'bc'),Segment(3,b'',True)])

    @graded(category='state', points=4)
    def test_timeout(self):
        s=M.Sender(b'a',1,1); a=s.send(0); self.assertEqual(s.tick(.9),[]); self.assertEqual(s.tick(1),a)

    @graded(category='state', points=4)
    def test_backoff(self):
        s=M.Sender(b'a',1,1); s.send(0); s.tick(1); self.assertEqual(s.tick(2),[]); self.assertEqual(s.tick(3),[Segment(0,b'a')])

    @graded(category='functional', points=4)
    def test_future_ack(self):
        s=M.Sender(b'abc',1,1); s.send(0); s.ack(Ack(9,9),0); self.assertEqual(s.send(0),[])

    @graded(category='state', points=4)
    def test_finish(self):
        s=M.Sender(b'',1,1); self.assertEqual(s.send(0),[Segment(0,b'',True)]); s.ack(Ack(1,1),0); self.assertTrue(s.finished)

    @graded(category='interface', points=4)
    def test_receiver_init(self):
        r=M.Receiver(3); self.assertEqual(r.ack(),Ack(0,3))

    @graded(category='functional', points=4)
    def test_receiver_order(self):
        r=M.Receiver(4); self.assertEqual(r.receive(Segment(0,b'ab')),Ack(2,2)); self.assertEqual(r.read(4),b'ab')

    @graded(category='robustness', points=4)
    def test_receiver_reorder(self):
        r=M.Receiver(4); r.receive(Segment(2,b'cd')); r.receive(Segment(0,b'ab')); self.assertEqual(r.read(4),b'abcd')

    @graded(category='robustness', points=4)
    def test_receiver_duplicate(self):
        r=M.Receiver(4); r.receive(Segment(0,b'ab')); r.receive(Segment(0,b'ab')); self.assertEqual(r.read(4),b'ab')

    @graded(category='state', points=4)
    def test_receiver_fin(self):
        r=M.Receiver(4); self.assertEqual(r.receive(Segment(0,b'a',True)).next_seq,2); self.assertFalse(r.finished); r.read(1); self.assertTrue(r.finished)

    @graded(category='boundary', points=4)
    def test_receiver_zero(self):
        r=M.Receiver(2); r.receive(Segment(0,b'ab')); self.assertEqual(r.ack().window,0); r.read(1); self.assertEqual(r.ack().window,1)

    @graded(category='error', points=4)
    def test_bad_receiver(self):
        self.assertRaises(ValueError,M.Receiver,0); r=M.Receiver(1); self.assertRaises(ValueError,r.read,-1)

    @graded(category='error', points=4)
    def test_negative_seq(self):
        r=M.Receiver(2); self.assertRaises(ValueError,r.receive,Segment(-1,b'a'))

    @graded(category='error', points=4)
    def test_time(self):
        s=M.Sender(b'a',1,1); s.send(2); self.assertRaises(ValueError,s.tick,1)

    @graded(category='state', points=4)
    def test_zero_window(self):
        s=M.Sender(b'abc',2,1); s.send(0); s.ack(Ack(1,0),0); self.assertEqual(s.send(0),[]); s.ack(Ack(1,2),0); self.assertEqual(s.send(0),[Segment(1,b'bc')])

    @graded(category='state', points=4)
    def test_empty_fin(self):
        r=M.Receiver(1); r.receive(Segment(0,b'',True)); self.assertTrue(r.finished)
    @graded(category='interface', points=4)
    def test_exact_integer_fields(self):
        for value in (True, 1.5):
            self.assertRaises(TypeError, M.Sender, b'a', value, 1)
            self.assertRaises(TypeError, M.Receiver, value)
            s = M.Sender(b'a', 1, 1); r = M.Receiver(4)
            self.assertRaises(TypeError, s.ack, Ack(value, 1), 0)
            self.assertRaises(TypeError, r.receive, Segment(value, b'a'))
            self.assertRaises(TypeError, r.read, value)

    @graded(category='error', points=4)
    def test_nonfinite_time(self):
        for value in (float('nan'), float('inf'), -float('inf')):
            self.assertRaises(ValueError, M.Sender, b'a', 1, value)
            s = M.Sender(b'a', 1, 1)
            self.assertRaises(ValueError, s.send, value)
            self.assertEqual(s.send(0), [Segment(0, b'a')])

    @graded(category='state', points=4)
    def test_invalid_ack_time_is_atomic(self):
        s = M.Sender(b'a', 1, 1); s.send(0)
        self.assertRaises(ValueError, s.ack, Ack(-1, 2), 10)
        self.assertEqual(s.tick(1), [Segment(0, b'a')])

    @graded(category='state', points=4)
    def test_duplicate_ack_timer(self):
        s = M.Sender(b'a', 1, 1); s.send(0); s.ack(Ack(0, 1), .9)
        self.assertEqual(s.tick(1), [Segment(0, b'a')])

    @graded(category='robustness', points=4)
    def test_fin_conflict_atomic(self):
        r = M.Receiver(4); r.receive(Segment(2, b'c', True))
        self.assertRaises(ValueError, r.receive, Segment(0, b'abcd', True))
        r.receive(Segment(0, b'ab')); self.assertEqual(r.read(4), b'abc'); self.assertTrue(r.finished)
