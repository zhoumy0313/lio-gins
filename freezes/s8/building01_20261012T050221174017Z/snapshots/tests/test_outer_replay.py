"""Integration checks for shared replay; synthetic fixtures are retained in run."""
import hashlib,json,os,subprocess,sys,unittest
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]

class ReplayIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder=Path(os.environ['LIO_GINS_RUN_DIR'])/'synthetic_replay_fixtures';cls.folder.mkdir()
        cls.cache=cls.folder/'cache';cls.cache.mkdir();t=np.arange(31)/10
        np.savez(cls.cache/'lio_cache.npz',sow=t,position=np.column_stack([t,t*0,t*0]),quaternion_xyzw=np.tile([0,0,0,1],(len(t),1)),available_sow=t+.01)
        (cls.cache/'cache_identity.json').write_text(json.dumps({'role':'development','experiment_kind':'synthetic_unit_fixture','cache_sha256':hashlib.sha256((cls.cache/'lio_cache.npz').read_bytes()).hexdigest()}))
        cls.initial=cls.folder/'initial';cls.initial.mkdir()
        (cls.initial/'initial_condition.json').write_text(json.dumps({'sequence':'building00','synthetic_fixture':True,'reference_epoch_sow':0,'R_NED_body_initial':np.eye(3).tolist(),'reference_initial_local_NED_m':[0,0,0],'initial_F9P_std_NED_m':[1,1,2],'antenna_lever_FRD_m':[0,-.07,-.365],'origin_ADIS_llh_deg_m':[30,114,20],'protocol':{'GNSS_std_floor_NED_m':[1,1,2]}}))
        cls.counter=0

    def run_case(self,method,last_fault=False,delete_all=False):
        type(self).counter+=1;n=type(self).counter;folder=self.folder/('case_'+str(n));folder.mkdir();gnss=folder/'observations.csv'
        g=np.array([[0,.5,.5,-.07,-.365,1,1,2],[1,1.5,1.5,-.07,-.365,1,1,2],[2,2.5,2.5,-.07,-.365,1,1,2]],float)
        if last_fault:g[-1,2]+=100
        if delete_all:g=g[:0]
        np.savetxt(gnss,g,delimiter=',',header='id,sow,N,E,D,stdN,stdE,stdD',comments='')
        gnss.with_suffix('.identity.json').write_text(json.dumps({'role':'development','sequence':'building00','fault_labels_included':False,'derived_sha256':hashlib.sha256(gnss.read_bytes()).hexdigest(),'initialization_sha256':hashlib.sha256((self.initial/'initial_condition.json').read_bytes()).hexdigest()}))
        conf={'method':method,'max_LIO_span_s':.15,'q_time_m2ps':.01,'q_distance_m2pm':.01,'q_axis_scale':[1,1,4],'nis_limit':11.3448667301,'huber_limit':2.5,'recovery':{'wait_s':2,'recovery_s':5,'protection':15,'onset_nis':16.266236,'gap_s':2}}
        config=folder/'config.json';config.write_text(json.dumps(conf));result=folder/'result';result.mkdir();env=os.environ.copy();env['LIO_GINS_RUN_DIR']=str(result)
        completed=subprocess.run([sys.executable,str(ROOT/'scripts/run_outer_baseline.py'),str(self.cache),str(self.initial),str(config),'--gnss-ned',str(gnss)],env=env,capture_output=True,text=True)
        (folder/'stdout.log').write_text(completed.stdout);(folder/'stderr.log').write_text(completed.stderr);(folder/'exit.json').write_text(json.dumps({'exit_code':completed.returncode}))
        self.assertEqual(completed.returncode,0,completed.stderr)
        return np.loadtxt(result/'trajectory.csv',delimiter=',',skiprows=1),[json.loads(x) for x in (result/'per_update.jsonl').read_text().splitlines()]

    def test_zero_innovation_correct_lever_and_unique_ids(self):
        for method in ['B2','B3','B4','B5','B6']:
            nav,updates=self.run_case(method)
            np.testing.assert_allclose(nav[:,1],nav[:,0],atol=1e-12);np.testing.assert_allclose(nav[:,2:4],0,atol=1e-12)
            self.assertEqual(len({u['original_gnss_id'] for u in updates}),len(updates));self.assertTrue(np.all(nav[:,4]>=nav[:,0]))

    def test_future_observation_change_does_not_change_past_outputs(self):
        for method in ['B3','B4','B5','B6']:
            a,_=self.run_case(method);b,_=self.run_case(method,last_fault=True)
            np.testing.assert_array_equal(a[a[:,0]<2.5],b[b[:,0]<2.5])

    def test_all_GNSS_removed_identical_propagation(self):
        outputs=[]
        for method in ['B3','B4','B5','B6']:
            nav,updates=self.run_case(method,delete_all=True);self.assertEqual(updates,[]);outputs.append(nav)
        for nav in outputs[1:]:np.testing.assert_array_equal(nav,outputs[0])
