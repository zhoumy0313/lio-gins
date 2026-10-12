import tempfile
from pathlib import Path
import unittest
import numpy as np
from scipy.spatial.transform import Rotation
from src.adapters.geodesy import llh_to_ecef, llh_to_ned, check_rotation, quat_xyzw_rotation, antenna_position
from src.adapters.sensor_text import gps_to_unix, unix_to_gps, load_sensor, audit_table, receiver_covariance
from src.fusion.position_kf import PositionKF
from src.evaluation.reference import load_kf_gins_llh, load_i2nav_local_ned, interpolate_with_gaps, horizontal_metrics


class GeometryAndInput(unittest.TestCase):
    def test_known_wgs84_points_and_ned_signs(self):
        np.testing.assert_allclose(llh_to_ecef([0,0,0]),[6378137,0,0])
        np.testing.assert_allclose(llh_to_ecef([0,90,0]),[0,6378137,0],atol=1e-8)
        p = llh_to_ned([[0.001,0,0],[0,0.001,0],[0,0,10]],[0,0,0])
        self.assertGreater(p[0,0],110)
        self.assertGreater(p[1,1],111)
        self.assertAlmostEqual(p[2,2],-10)

    def test_quaternion_convention_and_lever_under_turn(self):
        for rpy in [[0,0,90],[37,-12,75],[-90,0,0]]:
            r = Rotation.from_euler('xyz',rpy,degrees=True)
            np.testing.assert_allclose(quat_xyzw_rotation(r.as_quat()),r.as_matrix(),atol=1e-12)
        r = Rotation.from_euler('z',90,degrees=True).as_matrix()
        np.testing.assert_allclose(antenna_position([0,0,0],r,[1,0,0]),[0,1,0],atol=1e-12)
        with self.assertRaises(ValueError): check_rotation(np.diag([1,1,-1]))
        with self.assertRaises(ValueError): quat_xyzw_rotation([0,0,0,2])

    def test_explicit_week_and_boundary(self):
        for week,sow in [(2017,456300.125),(2400,0),(2400,604799.999)]:
            w,s = unix_to_gps(gps_to_unix(week,sow))
            self.assertEqual(w,week); self.assertAlmostEqual(s,sow,places=6)
        with self.assertRaises(ValueError): gps_to_unix(2400,604800)

    def test_increment_units_and_anomalies_preserved(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'imu.txt'; a=np.array([[1,.01,.02,.03,1,2,3],[1,.02,.04,.06,4,5,6],[.5,0,0,0,0,0,0]])
            np.savetxt(p,a); actual=load_sensor(p,'adis_increment')
            np.testing.assert_array_equal(actual,a)
            audit=audit_table(actual,'adis_increment')
            self.assertEqual(audit['duplicate_times'],1);self.assertEqual(audit['backward_times'],1)

    def test_std_squared_once_and_invalid_rejected(self):
        np.testing.assert_array_equal(receiver_covariance([2,3,4],[1,1,1]),np.diag([4,9,16]))
        for bad in [[0,1,1],[np.nan,1,1],[-1,1,1]]:
            with self.assertRaises(ValueError): receiver_covariance(bad,[1,1,1])

    def test_incompatible_nav_schemas(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'reference.nav';np.savetxt(p,np.zeros((2,10)))
            self.assertEqual(load_i2nav_local_ned(p).shape,(2,10))
            with self.assertRaises(ValueError): load_kf_gins_llh(p)
            np.savetxt(p,np.zeros((2,11)))
            self.assertEqual(load_kf_gins_llh(p).shape,(2,11))
            with self.assertRaises(ValueError): load_i2nav_local_ned(p)


class FilterAndEvaluation(unittest.TestCase):
    def new(self):return PositionKF(np.zeros(3),np.eye(3),np.eye(3))
    def test_zero_noise_and_no_random_mean(self):
        k=self.new()
        for _ in range(30):k.propagate([0,0,0],np.eye(3)*.1)
        np.testing.assert_array_equal(k.p,np.zeros(3))
        k.propagate([1,2,3],np.zeros((3,3)))
        k.update('one',[1,2,3],np.eye(3),np.eye(3),np.zeros(3))
        np.testing.assert_array_equal(k.p,[1,2,3])

    def test_closed_form_and_once_only(self):
        k=self.new();k.update('one',[2,4,6],np.eye(3),np.eye(3),np.zeros(3))
        np.testing.assert_array_equal(k.p,[1,2,3]);np.testing.assert_array_equal(k.P,np.eye(3)*.5)
        with self.assertRaises(ValueError):k.update('one',[2,4,6],np.eye(3),np.eye(3),np.zeros(3))

    def test_bad_r_does_not_corrupt_filter(self):
        for r in [np.diag([0,1,1]),np.eye(3)*np.nan,np.diag([-1,1,1])]:
            k=self.new();result=k.update('bad',[1,2,3],r,np.eye(3),np.zeros(3))
            self.assertFalse(result['accepted']);np.testing.assert_array_equal(k.p,np.zeros(3))
            with self.assertRaises(ValueError):k.update('bad',[1,2,3],np.eye(3),np.eye(3),np.zeros(3))

    def test_robust_baselines_suppress_outlier(self):
        ks=[self.new() for _ in range(3)]
        for k,policy in zip(ks,['disabled','nis','huber']):k.update('one',[100,0,0],np.eye(3),np.eye(3),np.zeros(3),policy=policy)
        self.assertEqual(ks[1].p[0],0);self.assertLess(ks[2].p[0],ks[0].p[0])

    def test_joseph_psd_in_long_sequence(self):
        rng=np.random.default_rng(11);k=self.new()
        for i in range(100):
            k.propagate(rng.normal(size=3),np.eye(3)*1e-9)
            k.update(str(i),rng.normal(size=3),np.diag([1e-6,1,1e6]),np.eye(3),np.zeros(3))
            np.testing.assert_allclose(k.P,k.P.T,atol=1e-12)
            self.assertGreaterEqual(np.linalg.eigvalsh(k.P).min(),0)

    def test_future_inputs_cannot_change_past_outputs(self):
        def replay(values):
            k=self.new();out=[]
            for i,v in enumerate(values):
                k.propagate([.1,0,0],np.eye(3)*.01)
                k.update(i,[v,0,0],np.eye(3),np.eye(3),np.zeros(3),policy='huber');out.append(k.p.copy())
            return out
        np.testing.assert_array_equal(replay([1,2,3,4,5])[:3],replay([1,2,3,-1000,500])[:3])
        np.testing.assert_array_equal(replay([1,2,3]),replay([1,2,3,4,5])[:3])

    def test_no_gnss_identical_propagation(self):
        ks=[self.new() for _ in range(3)]
        for k in ks:
            for _ in range(20):k.propagate([1,-2,.2],np.eye(3)*.1)
        for k in ks[1:]:np.testing.assert_array_equal(k.p,ks[0].p)

    def test_reference_gaps_and_rmse(self):
        v,valid=interpolate_with_gaps([0,1,10,11],np.zeros((4,3)),[0,.5,1,5,10,11,12],2)
        np.testing.assert_array_equal(valid,[True,True,True,False,True,True,False])
        m=horizontal_metrics([[3,4,0],[0,0,0],[np.nan,np.nan,np.nan]],3)
        self.assertAlmostEqual(m['horizontal_rmse_m'],np.sqrt(12.5));self.assertEqual(m['coverage'],2/3)

    def test_reference_duplicate_times_rejected_without_explicit_policy(self):
        with self.assertRaises(ValueError):
            interpolate_with_gaps([0,1,1,2],np.zeros((4,3)),[.5,1,1.5],2)

    def test_online_modules_do_not_read_reference(self):
        root=Path(__file__).resolve().parents[1]
        for d in ['src/fusion','src/adapters']:
            for p in (root/d).glob('*.py'):
                self.assertNotIn('src.evaluation',p.read_text());self.assertNotIn('groundtruth',p.read_text())
