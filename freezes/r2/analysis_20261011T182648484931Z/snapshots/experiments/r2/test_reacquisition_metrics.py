import unittest
import numpy as np
from reanalyse import accepted_clock,full_window,error_recovery
class MetricsContracts(unittest.TestCase):
    def test_transition_without_update_is_censored(self):
        updates=[{'measurement_sow':10,'available_sow':10.1,'accepted':False,'state':'RECOVERY'}]
        r=accepted_clock(updates,10);self.assertEqual(r['status'],'CENSORED');self.assertIsNone(r['T_admit_s']);self.assertEqual(r['censor_bound_s'],180)
    def test_first_actual_update_and_available_bound(self):
        updates=[{'measurement_sow':10,'available_sow':10.1,'accepted':False,'state':'NORMAL'},{'measurement_sow':17,'available_sow':17.125,'accepted':True,'original_gnss_id':9,'correction_norm_m':2}]
        r=accepted_clock(updates,10);self.assertEqual(r['T_admit_s'],7);self.assertEqual(r['T_available_bound_s'],7.125);self.assertEqual(r['first_gnss_id'],9)
    def test_future_and_horizon_updates_excluded(self):
        u={'measurement_sow':190,'available_sow':190.1,'accepted':True,'original_gnss_id':1,'correction_norm_m':1};self.assertEqual(accepted_clock([u],10)['status'],'CENSORED')
    def test_full_grid_known_error(self):
        g=np.arange(101)/10;e=np.tile([3,4,2],(len(g),1));r=full_window(g,e,0,10);self.assertEqual(r['samples_expected'],100);self.assertEqual(r['horizontal_RMSE_m'],5);self.assertEqual(r['coverage'],1)
    def test_missing_success_intersection_rejected(self):
        g=np.arange(101)/10;e=np.tile([3,4,2],(len(g),1));r=full_window(g[1:],e[1:],0,10);self.assertEqual(r['status'],'PARTIAL_OR_MISSING');self.assertIsNone(r['horizontal_RMSE_m']);self.assertEqual(r['samples_expected'],100)
    def test_nan_coverage_is_retained(self):
        g=np.arange(101)/10;e=np.zeros((len(g),3));e[2]=np.nan;r=full_window(g,e,0,10);self.assertEqual(r['samples_valid'],99);self.assertIsNone(r['horizontal_RMSE_m'])
    def test_alias_name_and_labels_cannot_affect_numerical_metrics(self):
        g=np.arange(101)/10;e=np.zeros((len(g),3));a={'name':'P','labels':[1],'metric':full_window(g,e,0,10)};b={'name':'Clock renamed','labels':[9],'metric':full_window(g,e,0,10)};self.assertEqual(a['metric'],b['metric'])
    def test_error_recovery_can_precede_any_gnss_admission(self):
        g=np.arange(1001)/10;e=np.zeros((len(g),3));self.assertEqual(error_recovery(g,e,0)['time_s'],0);self.assertEqual(accepted_clock([],0)['status'],'CENSORED')
    def test_sustained_error_condition(self):
        g=np.arange(1001)/10;e=np.zeros((len(g),3));e[g<4,0]=4;self.assertAlmostEqual(error_recovery(g,e,0)['time_s'],4)
if __name__=='__main__':unittest.main()
