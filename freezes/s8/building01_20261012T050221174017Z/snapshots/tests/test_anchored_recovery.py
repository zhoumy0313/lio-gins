import unittest
import numpy as np
from src.observation_manager.anchored_recovery import AnchoredRecovery
from src.observation_manager.availability_recovery import AvailabilityRecovery

class AnchorChecks(unittest.TestCase):
    params={'window_s':5,'score_limit':4,'good_duration_s':2}
    def new(self,**kwargs):return AnchoredRecovery(anchor_score_limit=9,anchor_good_duration_s=5,anchor_Q_growth_multiplier=1,**self.params,**kwargs)
    def observe(self,m,t,bias=0,nis=0,healthy=True):
        local=np.array([t,0,0]);return m.decide(t,local+[bias,0,0],local,np.eye(3),nis,healthy=healthy,travel_m=t,observation_id=int(t))

    def test_anchor_requires_sustained_past_validation(self):
        m=self.new()
        for t in range(10):self.observe(m,t)
        self.assertIsNone(m.anchor)
        self.observe(m,10);self.assertEqual(m.anchor['observation_id'],10)

    def test_stable_recovery_bias_does_not_wash_the_anchor(self):
        m=self.new()
        for t in range(21):self.observe(m,t)
        old=m.anchor['observation_id']
        for t in range(50,140):
            r=self.observe(m,t,bias=10,nis=50)
            self.assertFalse(r['admit']);self.assertEqual(m.anchor['observation_id'],old)
        self.assertEqual(r['state'],'UNRESOLVED')
        self.assertEqual(r['motion_score'],0.)  # Short consistency alone is blind.

    def test_legal_large_global_innovation_can_reintegrate(self):
        m=self.new()
        for t in range(21):self.observe(m,t)
        results=[self.observe(m,t,nis=100) for t in range(50,60)]
        self.assertTrue(results[7]['admit']);self.assertEqual(results[7]['state'],'RECOVERING')
        self.assertEqual(results[7]['anchor_score'],0.)

    def test_missing_local_health_uses_mature_policy_not_anchor_veto(self):
        m=self.new()
        for t in range(21):self.observe(m,t)
        r=self.observe(m,50,bias=10,nis=0,healthy=False)
        self.assertEqual(r['state'],'UNRESOLVED');self.assertIsNone(r['anchor_score'])
        # Same shadow fixed policy's ordinary post-outage wait is allowed.
        self.assertEqual(r['reason'],'unavailable_local_evidence_mature_recovery_fallback')

    def test_no_anchor_ablation_equals_r02_decisions(self):
        a=self.new(use_anchor=False);b=AvailabilityRecovery(**self.params)
        for t in list(range(21))+list(range(50,90)):
            bias=10 if t>=50 else 0;r=self.observe(a,t,bias=bias);local=np.array([t,0,0]);s=b.decide(t,local+[bias,0,0],local,np.eye(3),0,travel_m=t)
            for key in ['admit','state','r_multiplier','motion_score','qualification_elapsed_s']:self.assertEqual(r[key],s[key])

    def test_observation_equivalent_drift_and_bias_cannot_be_identified(self):
        # World A has accurate local motion and GNSS +10m. World B has accurate
        # GNSS and local drift -10m accumulated during the unobserved gap.
        # The estimator sees the same pair, hence cannot distinguish the worlds.
        results=[]
        for world in ['GNSS_bias','local_drift']:
            m=self.new()
            for t in range(21):self.observe(m,t)
            results.append([self.observe(m,t,bias=10) for t in range(50,65)])
        self.assertEqual(results[0],results[1]);self.assertTrue(all(not r['admit'] for r in results[1]))

    def test_future_bias_change_does_not_alter_trusted_past(self):
        def replay(bias):
            m=self.new();return [self.observe(m,t,bias=bias if t>=30 else 0) for t in range(40)]
        self.assertEqual(replay(0)[:30],replay(100)[:30])
