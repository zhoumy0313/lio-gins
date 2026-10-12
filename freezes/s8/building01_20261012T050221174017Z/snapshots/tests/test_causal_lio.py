import unittest
import numpy as np
from src.adapters.causal_lio import BufferedLIO


class CausalLIOTests(unittest.TestCase):
    def make(self,position=None,times=None):
        t=np.array([0.,.1,.2]) if times is None else np.array(times)
        p=np.array([[0,0,0],[1,0,0],[2,0,0]]) if position is None else np.array(position)
        return BufferedLIO(t,p,np.tile([0,0,0,1],(3,1)),t+.02,max_span_s=.15)

    def test_next_endpoint_is_unavailable_before_arrival(self):
        result=self.make().query(.05,available_until=.1)
        self.assertFalse(result['valid']);self.assertEqual(result['reason'],'endpoint_not_available')
        result=self.make().query(.05,available_until=.12)
        np.testing.assert_allclose(result['position'],[.5,0,0]);self.assertAlmostEqual(result['delay_s'],.07)

    def test_future_beyond_interpolation_endpoint_does_not_change_output(self):
        a=self.make().query(.05);b=self.make(position=[[0,0,0],[1,0,0],[9999,9999,9999]]).query(.05)
        np.testing.assert_array_equal(a['position'],b['position']);self.assertEqual(a['available_time'],b['available_time'])

    def test_missing_LIO_span_is_unavailable(self):
        result=self.make(times=[0,.3,.4]).query(.1)
        self.assertFalse(result['valid']);self.assertEqual(result['reason'],'LIO_gap')

    def test_queries_cannot_retroactively_use_past(self):
        l=self.make();l.query(.15)
        with self.assertRaises(ValueError):l.query(.1)

    def test_availability_cannot_precede_measurement(self):
        with self.assertRaises(ValueError):BufferedLIO([0,.1],np.zeros((2,3)),np.tile([0,0,0,1],(2,1)),[-.1,.09])
