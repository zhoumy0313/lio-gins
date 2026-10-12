import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import macro,improvement,clocks,qualified,method_role,window
from mechanism_support import event_window_updates
import numpy as np
class Metrics(unittest.TestCase):
 def test_diagnostic_window_does_not_label_unsupported_route_tail(self):
  rows=[{'measurement_sow':t} for t in [0,60,100,279,280,999]]
  self.assertEqual(event_window_updates(rows,[{'recovery_start_sow':100}]),[{'measurement_sow':t} for t in [60,100,279]])
 def test_event_macro_not_pooled(self):self.assertEqual(macro([1.,2.,6.]),3.);self.assertNotEqual(macro([1.,2.,6.]),np.sqrt(41/3))
 def test_missing_retained(self):self.assertIsNone(macro([1.,None,3.]));self.assertRaises(ValueError,macro,[1.,2.])
 def test_percentage_direction(self):self.assertEqual(improvement(3.,4.),.25);self.assertEqual(improvement(5.,4.),-.25);self.assertIsNone(improvement(0.,0.))
 def test_censor_and_zero(self):self.assertEqual(clocks([],10),(None,None,None));self.assertEqual(clocks([{'measurement_sow':10,'available_sow':10.2,'accepted':True,'original_gnss_id':7}],10),(0,.1999999999999993,7));self.assertEqual(clocks([{'measurement_sow':190,'available_sow':190,'accepted':True,'original_gnss_id':7}],10),(None,None,None))
 def test_service_cost(self):self.assertTrue(qualified(2,2,[0,7,15]));self.assertFalse(qualified(2,2,[0,7,None]));self.assertFalse(qualified(2.001,2,[0,7,15]));self.assertFalse(qualified(2,2,[0,7,15.001]));self.assertFalse(qualified(2,2,[0,7,15],False))
 def test_nis_alias(self):self.assertEqual(method_role('NIS0',{'nis_limit':11.3448667301}),'strict NIS 11.3448667301');self.assertEqual(method_role('B4',{}),'wide NIS100')
 def test_full_grid_missing_not_removed(self):g=np.arange(900)/10;e=np.ones((900,3));self.assertAlmostEqual(window(g,e,0,90)['RMSE'],np.sqrt(2));e[10]=np.nan;self.assertIsNone(window(g,e,0,90)['RMSE']);self.assertEqual(window(g,e,0,90)['coverage'],899/900)
if __name__=='__main__':unittest.main()
