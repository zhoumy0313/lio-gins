import unittest
from src.fusion.fixed_recovery import FixedRecovery


class RecoveryTests(unittest.TestCase):
    def test_wait_ends_and_recovery_finishes_without_truth(self):
        b=FixedRecovery(wait_s=2,recovery_s=3,protection=10)
        self.assertEqual(b.decide(0,20)['state'],'WAIT')
        self.assertFalse(b.decide(1,0)['admit'])
        self.assertEqual(b.decide(2,0)['r_multiplier'],10)
        self.assertGreater(b.decide(3,0)['r_multiplier'],1)
        self.assertEqual(b.decide(5,0)['state'],'NORMAL')

    def test_missing_data_restarts_recovery_protection(self):
        b=FixedRecovery(wait_s=0,recovery_s=5)
        self.assertEqual(b.decide(0,0)['state'],'NORMAL')
        self.assertEqual(b.decide(30,0)['state'],'RECOVERY')
        self.assertGreater(b.decide(31,0)['r_multiplier'],1)

    def test_later_anomaly_does_not_change_prior_decisions(self):
        a=FixedRecovery();b=FixedRecovery()
        self.assertEqual(a.decide(0,0),b.decide(0,0))
        self.assertEqual(a.decide(1,0),b.decide(1,0))
        a.decide(2,9999);b.decide(2,0)
        self.assertNotEqual(a.state,b.state)

    def test_duplicate_time_is_rejected(self):
        b=FixedRecovery();b.decide(0,0)
        with self.assertRaises(ValueError):b.decide(0,0)

class MatchedRobustCovarianceTests(unittest.TestCase):
    def test_fixed_protection_uses_the_same_nominal_Huber_score(self):
        import numpy as np
        from src.fusion.position_kf import PositionKF
        k=PositionKF([0,0,0],np.eye(3),np.eye(3))
        result=k.update('g1',[10,0,0],np.eye(3),np.eye(3),[0,0,0],policy='huber',huber_limit=2,external_r_multiplier=10)
        gamma=max(1,np.sqrt(50)/2)*10
        self.assertAlmostEqual(result['nis'],50)
        self.assertAlmostEqual(result['r_multiplier'],gamma)
        self.assertAlmostEqual(k.p[0],10/(1+gamma))
        with self.assertRaises(ValueError):k.update('g1',[10,0,0],np.eye(3),np.eye(3),[0,0,0])
