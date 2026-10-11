"""Physical integration check: a rotating nonzero lever creates no IMU translation."""
import hashlib,json,os,subprocess,sys,unittest
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[1]

class RotatingLever(unittest.TestCase):
    def test_pure_rotation_is_not_false_position_or_motion_fault(self):
        folder=Path(os.environ['LIO_GINS_RUN_DIR'])/'rotating_lever_fixture';folder.mkdir();cache=folder/'cache';cache.mkdir();t=np.arange(101)/10;rot=Rotation.from_euler('z',t*np.pi/10)
        np.savez(cache/'lio_cache.npz',sow=t,position=np.zeros((len(t),3)),quaternion_xyzw=rot.as_quat(),available_sow=t+.01,effective_points=np.ones(len(t))*1000,mean_abs_plane_residual_m=np.zeros(len(t)))
        (cache/'cache_identity.json').write_text(json.dumps({'role':'development','synthetic_fixture':True,'cache_sha256':hashlib.sha256((cache/'lio_cache.npz').read_bytes()).hexdigest()}))
        init=folder/'initial';init.mkdir();lever=np.array([0,-.07,-.365]);ic=init/'initial_condition.json';ic.write_text(json.dumps({'sequence':'building00','synthetic_fixture':True,'reference_epoch_sow':0,'R_NED_body_initial':np.eye(3).tolist(),'reference_initial_local_NED_m':[0,0,0],'initial_F9P_std_NED_m':[1,1,2],'antenna_lever_FRD_m':lever.tolist(),'origin_ADIS_llh_deg_m':[30,114,20],'protocol':{'GNSS_std_floor_NED_m':[1,1,2]}}))
        epochs=np.arange(1,10);gnss=np.column_stack([epochs-1,epochs,Rotation.from_euler('z',epochs*np.pi/10).apply(np.tile(lever,(len(epochs),1))),np.tile([1,1,2],(len(epochs),1))]);data=folder/'observations.csv';np.savetxt(data,gnss,delimiter=',',header='id,sow,N,E,D,stdN,stdE,stdD',comments='');data.with_suffix('.identity.json').write_text(json.dumps({'role':'development','sequence':'building00','fault_labels_included':False,'derived_sha256':hashlib.sha256(data.read_bytes()).hexdigest(),'initialization_sha256':hashlib.sha256(ic.read_bytes()).hexdigest()}))
        conf={'method':'P','revision':'r02','max_LIO_span_s':.15,'max_LIO_availability_delay_s':.25,'q_time_m2ps':.001,'q_distance_m2pm':.001,'q_axis_scale':[1,1,4],'nis_limit':16.266236,'huber_limit':2.5,'recovery':{'wait_s':2,'recovery_s':15,'protection':15,'onset_nis':16.266236,'gap_s':2},'motion':{'window_s':1,'score_limit':4,'good_duration_s':1},'health_min_points':100,'health_max_residual_m':.2};cp=folder/'config.json';cp.write_text(json.dumps(conf));result=folder/'result';result.mkdir();env=os.environ.copy();env['LIO_GINS_RUN_DIR']=str(result)
        command=[sys.executable,str(ROOT/'scripts/run_candidate.py'),str(cache),str(init),str(cp),'--gnss-ned',str(data)];r=subprocess.run(command,env=env,capture_output=True,text=True);(folder/'command.json').write_text(json.dumps({'argv':command,'exit_code':r.returncode}));(folder/'stdout.log').write_text(r.stdout);(folder/'stderr.log').write_text(r.stderr);self.assertEqual(r.returncode,0,r.stderr)
        nav=np.loadtxt(result/'trajectory.csv',delimiter=',',skiprows=1);np.testing.assert_allclose(nav[:,1:4],0,atol=1e-12)
        updates=[json.loads(x) for x in (result/'per_update.jsonl').read_text().splitlines()];self.assertTrue(all(u['accepted'] for u in updates));self.assertTrue(all(u['motion_score'] is None or u['motion_score']<1e-20 for u in updates))
