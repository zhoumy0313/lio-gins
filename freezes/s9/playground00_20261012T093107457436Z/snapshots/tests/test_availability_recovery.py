import unittest
import numpy as np
from src.observation_manager.availability_recovery import AvailabilityRecovery
from src.fusion.fixed_recovery import FixedRecovery

class AvailabilityChecks(unittest.TestCase):
    def new(self):return AvailabilityRecovery(window_s=2,score_limit=9,good_duration_s=2)
    def observe(self,m,t,bias=0,nis=0,healthy=True):
        local=np.array([t,0,0]);return m.decide(t,local+[bias,0,0],local,np.eye(3),nis,healthy=healthy,travel_m=t)

    def test_unavailable_then_fresh_window_does_not_latch_GNSS_fault(self):
        m=self.new();fixed=FixedRecovery(wait_s=2,recovery_s=15,protection=15)
        for t in range(35):
            nis=30 if 10<=t<=14 else 0
            r=self.observe(m,t,nis=nis,healthy=t not in [5,12,13,22]);b=fixed.decide(t,nis)
            self.assertEqual(r['admit'],b['admit']);self.assertEqual(r['r_multiplier'],b['r_multiplier'])

    def test_actual_outage_still_requires_qualified_motion(self):
        m=self.new()
        for t in range(5):self.observe(m,t)
        results=[self.observe(m,t) for t in range(40,46)]
        self.assertFalse(results[0]['admit']);self.assertFalse(results[3]['admit']);self.assertTrue(results[4]['admit']);self.assertEqual(results[4]['state'],'RECOVERING')

    def test_available_motion_violation_overrides_mature_acceptance(self):
        m=self.new()
        for t in range(5):self.observe(m,t)
        r=self.observe(m,5,bias=100)
        self.assertFalse(r['admit']);self.assertGreater(r['motion_score'],9)

    def test_future_bias_change_cannot_change_past(self):
        def replay(bias):
            m=self.new();return [self.observe(m,t,bias=bias if t>=10 else 0) for t in range(20)]
        self.assertEqual(replay(0)[:10],replay(100)[:10])
