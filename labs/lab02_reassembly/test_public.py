import unittest
from netlab.testing import load_impl, graded
M = load_impl('lab02_reassembly')

class Tests(unittest.TestCase):
    @graded(category='interface', points=4)
    def test_initial(self):
        r=M.Reassembler(4); self.assertEqual((r.pending,r.available,r.finished),(0,0,False))

    @graded(category='error', points=4)
    def test_capacity(self):
        self.assertRaises(ValueError,M.Reassembler,0)

    @graded(category='functional', points=4)
    def test_ordered(self):
        r=M.Reassembler(8); r.insert(0,b'abc'); self.assertEqual(r.read(8),b'abc')

    @graded(category='functional', points=4)
    def test_reorder(self):
        r=M.Reassembler(8); r.insert(2,b'cd'); r.insert(0,b'ab'); self.assertEqual(r.read(8),b'abcd')

    @graded(category='state', points=4)
    def test_pending(self):
        r=M.Reassembler(8); r.insert(2,b'cd'); self.assertEqual(r.pending,2)

    @graded(category='state', points=4)
    def test_duplicate(self):
        r=M.Reassembler(8); r.insert(2,b'cd'); r.insert(2,b'cd'); self.assertEqual(r.pending,2)

    @graded(category='robustness', points=4)
    def test_overlap(self):
        r=M.Reassembler(8); r.insert(1,b'BC'); r.insert(0,b'abc'); self.assertEqual(r.read(8),b'aBC')

    @graded(category='boundary', points=4)
    def test_window(self):
        r=M.Reassembler(3); r.insert(0,b'abcde'); self.assertEqual(r.read(9),b'abc')

    @graded(category='state', points=4)
    def test_retransmit(self):
        r=M.Reassembler(3); r.insert(0,b'abcde'); r.read(3); r.insert(3,b'de'); self.assertEqual(r.read(9),b'de')

    @graded(category='boundary', points=4)
    def test_partial_read(self):
        r=M.Reassembler(5); r.insert(0,b'abcd'); self.assertEqual((r.read(2),r.available),(b'ab',2))

    @graded(category='boundary', points=4)
    def test_zero_read(self):
        r=M.Reassembler(4); r.insert(0,b'a'); self.assertEqual(r.read(0),b'')

    @graded(category='state', points=4)
    def test_eof(self):
        r=M.Reassembler(4); r.insert(0,b'abc',True); self.assertFalse(r.finished); r.read(3); self.assertTrue(r.finished)

    @graded(category='state', points=4)
    def test_empty_eof(self):
        r=M.Reassembler(4); r.insert(0,b'',True); self.assertTrue(r.finished)

    @graded(category='error', points=4)
    def test_negative(self):
        r=M.Reassembler(4); self.assertRaises(ValueError,r.insert,-1,b'a'); self.assertRaises(ValueError,r.read,-1)

    @graded(category='error', points=4)
    def test_conflict(self):
        r=M.Reassembler(4); r.insert(2,b'',True); self.assertRaises(ValueError,r.insert,3,b'',True)

    @graded(category='error', points=4)
    def test_type(self):
        r=M.Reassembler(4); self.assertRaises(TypeError,r.insert,0,'x')

    @graded(category='state', points=4)
    def test_eof_reorder(self):
        r=M.Reassembler(8); r.insert(2,b'cd',True); r.insert(0,b'ab'); self.assertEqual(r.read(8),b'abcd'); self.assertTrue(r.finished)

    @graded(category='error', points=4)
    def test_past_eof(self):
        r=M.Reassembler(8); r.insert(2,b'',True); self.assertRaises(ValueError,r.insert,2,b'x')

    @graded(category='boundary', points=4)
    def test_clipped_overlap(self):
        r=M.Reassembler(3); r.insert(1,b'bcde'); r.insert(0,b'a'); self.assertEqual(r.read(5),b'abc')

    @graded(category='robustness', points=4)
    def test_stale(self):
        r=M.Reassembler(4); r.insert(0,b'ab'); r.read(2); r.insert(0,b'abcd'); self.assertEqual(r.read(4),b'cd')
    @graded(category='interface', points=4)
    def test_integer_types(self):
        for value in (True, 1.5):
            self.assertRaises(TypeError, M.Reassembler, value)
            r = M.Reassembler(4)
            self.assertRaises(TypeError, r.insert, value, b'a')
            self.assertRaises(TypeError, r.read, value)

    @graded(category='error', points=4)
    def test_invalid_eof_flag(self):
        r = M.Reassembler(4)
        self.assertRaises(TypeError, r.insert, 0, b'a', 1)
        self.assertEqual((r.available, r.pending, r.finished), (0, 0, False))

    @graded(category='state', points=4)
    def test_conflict_is_atomic(self):
        r = M.Reassembler(4); r.insert(2, b'c', True)
        self.assertRaises(ValueError, r.insert, 0, b'zzzz', True)
        r.insert(0, b'ab'); self.assertEqual(r.read(4), b'abc'); self.assertTrue(r.finished)

    @graded(category='state', points=4)
    def test_full_window_gap(self):
        r = M.Reassembler(4); r.insert(2, b'cd'); r.insert(4, b'e')
        r.insert(0, b'ab'); self.assertEqual(r.read(4), b'abcd')
        self.assertEqual(r.read(4), b'')

    @graded(category='robustness', points=4)
    def test_stale_eof_before_accepted_data(self):
        r = M.Reassembler(4); r.insert(0, b'ab'); r.read(2)
        self.assertRaises(ValueError, r.insert, 1, b'', True)
        r.insert(2, b'c', True); self.assertEqual(r.read(4), b'c'); self.assertTrue(r.finished)
