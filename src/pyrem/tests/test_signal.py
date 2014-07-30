__author__ = 'quentin'


__author__ = 'quentin'


import unittest
from pyrem.signal.signal  import *
import numpy as np
import os
import tempfile


def compare_signals(a,b, test_values=True):
    out = True
    if test_values:
        out &= np.allclose(a, b)
    out &= (a.type == b.type)
    out &= (a.name == b.name)
    out &= (a.fs == b.fs)
    out &= (a.metadata == b.metadata)
    return out



class TestFeatures(unittest.TestCase):
    np.random.seed(1)
    random_walk = np.cumsum(np.random.normal(0,1,(int(1e4))))


    def test_attributes(self):
        a = Signal(self.random_walk, 10,type="eeg", name="foo", metadata={"animal":"joe", "treatment":18})
        self.assertEqual(a.type, "eeg")
        self.assertEqual(a.name,"foo")
        self.assertEqual(a.metadata, {"animal":"joe", "treatment":18})

    def test_ufuncs(self):
        a = Signal(self.random_walk, 10,type="eeg", name="foo", metadata={"animal":"joe", "treatment":18})
        self.assertTrue(isinstance(a,Signal))

        b = a + 1
        b -= 1
        self.assertTrue(compare_signals(a, b))

        b = a[0 : 300]
        self.assertTrue(compare_signals(a,b,False))

    def test_copy(self):
        a = Signal(self.random_walk, 10,type="eeg", name="foo", metadata={"animal":"joe", "treatment":18})
        b = a.copy()

        self.assertTrue(compare_signals(a, b))

        b+=1
        self.assertFalse(compare_signals(a, b))

    def test_save_load(self):

        file, path = tempfile.mkstemp(suffix=".pkl")


        a = Signal(self.random_walk, 10,type="eeg", name="foo", metadata={"animal":"joe", "treatment":18})
        a.save(path)


        b = signal_from_pkl(path)

        try:
            os.remove(path)
        except Exception as e:
            print e
            pass
        self.assertTrue(compare_signals(a,b))

    def test_duration(self):
        a = Signal(self.random_walk, 10,type="eeg", name="foo", metadata={"animal":"joe", "treatment":18})
        d_total = a.duration
        d_0 = a[:a.size/2].duration
        d_1 = a[a.size/2 :].duration

        self.assertEqual(d_total, d_0 + d_1)

    def test_indexing(self):
        a = Signal(self.random_walk, 10,type="eeg", name="foo", metadata={"animal":"joe", "treatment":18})
        view = a[0:100]
        view += 1
        self.assertTrue(compare_signals(a[0:100],view))


        self.assertEqual(a[:"201w"].size, 2)
        self.assertEqual(a[:"199w"].size, 1)

    def test_indexing(self):
        a = Signal(self.random_walk, 10,type="eeg", name="foo", metadata={"animal":"joe", "treatment":18})
        ws = [w for o,w in a.iter_window(1.3,1)]
        b = np.array(ws).flatten()

        c = a[:b.size]

        b = c._copy_attrs_to_array(b)

        self.assertTrue(compare_signals(c,b))




    def test_dummy(self):
        a = Signal(np.random.normal(size=int(1e6)), 10,type="eeg", name="foo", metadata={"animal":"joe", "treatment":18})
        a._represent_long_time_series()




