"""Copied candidate geometry must equal B6 when the manager is removed."""
import hashlib,json,os,subprocess,sys,unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]

class CandidateFoundation(unittest.TestCase):
    def test_same_KF_geometry_once_only_and_future_causality(self):
        folder=Path(os.environ['LIO_GINS_RUN_DIR'])/'candidate_parity_fixtures';folder.mkdir()
        cache=folder/'cache';cache.mkdir();t=np.arange(101)/10
        np.savez(cache/'lio_cache.npz',sow=t,position=np.column_stack([t,t*0,t*0]),quaternion_xyzw=np.tile([0,0,0,1],(len(t),1)),available_sow=t+.01,effective_points=np.ones(len(t))*1000,mean_abs_plane_residual_m=np.zeros(len(t)))
        (cache/'cache_identity.json').write_text(json.dumps({'role':'development','synthetic_fixture':True,'cache_sha256':hashlib.sha256((cache/'lio_cache.npz').read_bytes()).hexdigest()}))
        init=folder/'initial';init.mkdir();ic=init/'initial_condition.json';ic.write_text(json.dumps({'sequence':'building00','synthetic_fixture':True,'reference_epoch_sow':0,'R_NED_body_initial':np.eye(3).tolist(),'reference_initial_local_NED_m':[0,0,0],'initial_F9P_std_NED_m':[1,1,2],'antenna_lever_FRD_m':[0,-.07,-.365],'origin_ADIS_llh_deg_m':[30,114,20],'protocol':{'GNSS_std_floor_NED_m':[1,1,2]}}))
        def run(method,index,fault=False):
            d=folder/str(index);d.mkdir();g=np.array([[i,float(i+1),float(i+1),-.07,-.365,1,1,2] for i in range(9)])
            g[4,2]+=10
            if fault:g[-1,2]+=100
            data=d/'GNSS.csv';np.savetxt(data,g,delimiter=',',header='id,sow,N,E,D,stdN,stdE,stdD',comments='');data.with_suffix('.identity.json').write_text(json.dumps({'role':'development','sequence':'building00','fault_labels_included':False,'derived_sha256':hashlib.sha256(data.read_bytes()).hexdigest(),'initialization_sha256':hashlib.sha256(ic.read_bytes()).hexdigest()}))
            conf={'method':method,'max_LIO_span_s':.15,'max_LIO_availability_delay_s':.25,'q_time_m2ps':.001,'q_distance_m2pm':.001,'q_axis_scale':[1,1,4],'nis_limit':16.266236,'huber_limit':2.5,'recovery':{'wait_s':2,'recovery_s':15,'protection':15,'onset_nis':16.266236,'gap_s':2},'motion':{'window_s':1,'score_limit':4,'good_duration_s':1},'health_min_points':100,'health_max_residual_m':.2};cp=d/'config.json';cp.write_text(json.dumps(conf));result=d/'result';result.mkdir();env=os.environ.copy();env['LIO_GINS_RUN_DIR']=str(result)
            script='run_outer_baseline.py' if method=='B6' else 'run_candidate.py';command=[sys.executable,str(ROOT/'scripts'/script),str(cache),str(init),str(cp),'--gnss-ned',str(data)];r=subprocess.run(command,env=env,capture_output=True,text=True);(d/'command.json').write_text(json.dumps({'argv':command,'exit_code':r.returncode}));(d/'stdout.log').write_text(r.stdout);(d/'stderr.log').write_text(r.stderr);self.assertEqual(r.returncode,0,r.stderr)
            nav=np.loadtxt(result/'trajectory.csv',delimiter=',',skiprows=1);updates=[json.loads(line) for line in (result/'per_update.jsonl').read_text().splitlines()];self.assertEqual(len(set(u['original_gnss_id'] for u in updates)),len(g));return nav
        np.testing.assert_array_equal(run('B6',0),run('P_without_motion',1))
        a=run('P',2);b=run('P',3,fault=True);np.testing.assert_array_equal(a[a[:,0]<9],b[b[:,0]<9])
