import copy,unittest
import numpy as np
from src.observation_manager.motion_recovery import MotionRecovery

class MotionManagerChecks(unittest.TestCase):
    def manager(self,**kwargs):return MotionRecovery(window_s=1,score_limit=4,good_duration_s=2,**kwargs)
    def observe(self,m,t,bias=0,nis=0,healthy=True):
        local=np.array([t,0,0]);return m.decide(t,local+[bias,0,0],local,np.eye(3),nis,healthy=healthy,travel_m=t)

    def test_jump_isolation_and_failed_verification_reset(self):
        m=self.manager()
        result=[]
        for t in range(14):result.append(self.observe(m,t,bias=10 if t in [5,9] else 0))
        self.assertTrue(result[4]['admit']);self.assertFalse(result[5]['admit']);self.assertFalse(result[8]['admit']);self.assertFalse(result[9]['admit']);self.assertFalse(result[12]['admit'])
        self.assertTrue(result[13]['admit']);self.assertEqual(result[13]['r_multiplier'],15)

    def test_constant_bias_after_outage_is_an_explicit_r01_blind_spot(self):
        m=self.manager()
        for t in range(5):self.observe(m,t)
        result=[self.observe(m,t,bias=10,nis=50) for t in range(40,45)]
        self.assertFalse(result[0]['admit']);self.assertIsNone(result[0]['motion_score'])
        self.assertTrue(result[-1]['admit']);self.assertEqual(result[-1]['motion_score'],0.)

    def test_legitimate_large_innovation_can_reintegrate(self):
        m=self.manager()
        for t in range(5):self.observe(m,t)
        result=[self.observe(m,t,nis=50) for t in range(40,45)]
        self.assertTrue(result[-1]['admit']);self.assertEqual(result[-1]['state'],'RECOVERING')

    def test_unhealthy_local_evidence_never_adds_a_veto(self):
        m=self.manager();self.observe(m,0)
        r=self.observe(m,1,bias=100,nis=1e6,healthy=False)
        self.assertTrue(r['admit']);self.assertEqual(r['state'],'UNRESOLVED');self.assertEqual(r['r_multiplier'],1);self.assertIsNone(r['motion_score'])

    def test_missing_samples_do_not_create_a_window_difference(self):
        m=self.manager();self.observe(m,0);self.observe(m,1)
        r=self.observe(m,3)
        self.assertIsNone(r['motion_score'])

    def test_unqualified_wait_cannot_display_normal_indefinitely(self):
        m=self.manager(max_wait_s=5)
        for t in range(10):r=self.observe(m,t,bias=10*t)
        self.assertEqual(r['state'],'UNRESOLVED');self.assertFalse(r['admit'])
        self.assertEqual(m.output_state(20),'OUTAGE')

    def test_future_change_cannot_change_past_decisions(self):
        def replay(fault):
            m=self.manager();return [self.observe(m,t,bias=100 if fault and t>=10 else 0) for t in range(15)]
        self.assertEqual(replay(False)[:10],replay(True)[:10])

    def test_duplicate_and_backward_observation_times_rejected(self):
        m=self.manager();self.observe(m,2)
        for t in [2,1]:
            with self.assertRaises(ValueError):self.observe(m,t)
