"""Post-freeze acceptance checks; frozen estimator sources remain untouched."""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
import numpy as np
from scipy.spatial.transform import Rotation
from scripts.canonicalize_development_gnss import canonicalize

ROOT=Path(__file__).resolve().parents[1]
METHODS=['B2','B3','B4','B5','B6','P','P_without_motion','P_time_only','P_without_decay','P_without_anchor']

class FinalContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(os.environ['LIO_GINS_RUN_DIR'])/'final_contract_fixtures';cls.root.mkdir();cls.counter=0
        cls.cache=cls.root/'cache';cls.cache.mkdir();t=np.arange(501)/10
        np.savez(cls.cache/'lio_cache.npz',sow=t,position=np.column_stack([t,t*0,t*0]),quaternion_xyzw=np.tile([0,0,0,1],(len(t),1)),available_sow=t+.01,effective_points=t*0+1000,mean_abs_plane_residual_m=t*0)
        cls.cache_id={'role':'development','sequence':'building00','synthetic_fixture':True,'cache_sha256':hashlib.sha256((cls.cache/'lio_cache.npz').read_bytes()).hexdigest()}
        (cls.cache/'cache_identity.json').write_text(json.dumps(cls.cache_id))
        cls.init=cls.root/'init';cls.init.mkdir();cls.ic=cls.init/'initial_condition.json'
        cls.ic.write_text(json.dumps({'sequence':'building00','synthetic_fixture':True,'reference_epoch_sow':0,'R_NED_body_initial':np.eye(3).tolist(),'reference_initial_local_NED_m':[0,0,0],'initial_F9P_std_NED_m':[1,1,2],'antenna_lever_FRD_m':[0,-.07,-.365],'origin_ADIS_llh_deg_m':[30,114,20],'protocol':{'GNSS_std_floor_NED_m':[1,1,2]}}))
        cls.conf=json.loads((ROOT/'configs/final_evaluation_methods.json').read_text())

    def replay(self,method,rows=None,canonical=False,cache=None,extra_label=False,labeled=False):
        type(self).counter+=1;d=self.root/str(self.counter);d.mkdir();data=d/'observations.csv'
        if rows is None: rows=np.array([[i,i+1,i+1,-.07,-.365,1,1,2] for i in range(49)],float)
        np.savetxt(data,rows,delimiter=',',header='id,sow,N,E,D,stdN,stdE,stdD',comments='')
        data.with_suffix('.identity.json').write_text(json.dumps({'role':'development','sequence':'building00','fault_labels_included':labeled,'derived_sha256':hashlib.sha256(data.read_bytes()).hexdigest(),'initialization_sha256':hashlib.sha256(self.ic.read_bytes()).hexdigest()}))
        if canonical:data=canonicalize(data,d/'ordered.csv')
        if extra_label:(d/'future_fault_labels.json').write_text(json.dumps({'future_fault_sow':30,'secret_reference':[999,999,999]}))
        conf={**self.conf[method]};cp=d/'config.json';cp.write_text(json.dumps(conf));out=d/'result';out.mkdir();env=os.environ.copy();env['LIO_GINS_RUN_DIR']=str(out)
        script='run_outer_baseline.py' if method.startswith('B') else 'run_candidate.py'
        argv=[sys.executable,str(ROOT/'scripts'/script),str(cache or self.cache),str(self.init),str(cp),'--gnss-ned',str(data)]
        r=subprocess.run(argv,env=env,capture_output=True,text=True)
        (d/'execution.json').write_text(json.dumps({'argv':argv,'exit_code':r.returncode}));(d/'stdout.log').write_text(r.stdout);(d/'stderr.log').write_text(r.stderr)
        return r,out

    def nav(self,method,**kwargs):
        r,out=self.replay(method,**kwargs);self.assertEqual(r.returncode,0,r.stderr)
        return np.loadtxt(out/'trajectory.csv',delimiter=',',skiprows=1),[json.loads(line) for line in (out/'per_update.jsonl').read_text().splitlines()]

    def test_shuffled_file_canonicalization_and_id_renumber_preserve_numerical_output(self):
        g=np.array([[i,i+1,i+1,-.07,-.365,1,1,2] for i in range(49)],float);g[29:,2]+=10
        for method in ['B3','B4','B5','B6','P']:
            a,ua=self.nav(method,rows=g,canonical=True);b,ub=self.nav(method,rows=g[::-1],canonical=True)
            np.testing.assert_array_equal(a,b);self.assertEqual(ua,ub)
            renamed=g.copy();renamed[:,0]=1000-np.arange(len(g))*3
            c,uc=self.nav(method,rows=renamed,canonical=True);np.testing.assert_array_equal(a,c)
            # ID-bearing audit records and byte SHA legitimately change.
            self.assertEqual([u['original_gnss_id'] for u in uc],renamed[:,0].tolist())
            for log in [ua,uc]:self.assertEqual(len({u['original_gnss_id'] for u in log}),len(log))

    def test_all_policies_no_gnss_propagation_identical(self):
        values=[self.nav(m,rows=np.empty((0,8))) for m in METHODS]
        for nav,updates in values:self.assertEqual(updates,[]);np.testing.assert_array_equal(nav,values[0][0])

    def test_r03_disabled_manager_exact_fixed_recovery_and_future_deletion_causal(self):
        a,_=self.nav('B6');b,_=self.nav('P_without_motion');np.testing.assert_array_equal(a,b)
        g=np.array([[i,i+1,i+1,-.07,-.365,1,1,2] for i in range(49)],float)
        a,_=self.nav('P',rows=g);b,_=self.nav('P',rows=g[:20]);np.testing.assert_array_equal(a[a[:,0]<=20],b[b[:,0]<=20])

    def test_future_label_neighbor_has_no_effect_and_labeled_input_is_rejected(self):
        a,ua=self.nav('P');b,ub=self.nav('P',extra_label=True);np.testing.assert_array_equal(a,b);self.assertEqual(ua,ub)
        for method in ['B6','P']:
            r,_=self.replay(method,labeled=True);self.assertNotEqual(r.returncode,0);self.assertIn('labeled algorithm input',r.stderr)

    def test_cache_hash_mutation_rejected_and_gap_marks_failed_coverage(self):
        changed=self.root/'mutated_cache';changed.mkdir();old=self.cache/'lio_cache.npz';(changed/'lio_cache.npz').write_bytes(old.read_bytes()+b'changed');(changed/'cache_identity.json').write_text(json.dumps(self.cache_id))
        r,_=self.replay('P',cache=changed);self.assertNotEqual(r.returncode,0);self.assertIn('cache identity changed',r.stderr)
        gap=self.root/'gap_cache';gap.mkdir();v=dict(np.load(old));mask=(v['sow']<10)|(v['sow']>12)
        np.savez(gap/'lio_cache.npz',**{k:x[mask] for k,x in v.items()});identity={**self.cache_id,'cache_sha256':hashlib.sha256((gap/'lio_cache.npz').read_bytes()).hexdigest()};(gap/'cache_identity.json').write_text(json.dumps(identity))
        r,out=self.replay('P',cache=gap);self.assertEqual(r.returncode,2);n=np.loadtxt(out/'trajectory.csv',delimiter=',',skiprows=1);self.assertTrue(np.isnan(n[n[:,0]>=10,1:4]).all());self.assertTrue((n[n[:,0]>=10,6]==0).all())

    def test_online_import_graph_excludes_reference_and_evaluation(self):
        for folder in ['src/adapters','src/fusion','src/observation_manager']:
            for p in (ROOT/folder).glob('*.py'):
                for node in ast.walk(ast.parse(p.read_text())):
                    if isinstance(node,ast.ImportFrom):self.assertFalse((node.module or '').startswith('src.evaluation'),str(p))
                    if isinstance(node,ast.Import):self.assertFalse(any(x.name.startswith('src.evaluation') for x in node.names),str(p))
        for f in ['scripts/run_outer_baseline.py','scripts/run_candidate.py']:
            text=(ROOT/f).read_text();self.assertNotIn('load_i2nav_local_ned',text);self.assertNotIn('groundtruth.nav',text)

    def test_final_r03_stationary_turn_and_unflagged_pose_reset_do_not_crash(self):
        t=np.arange(501)/10;lever=np.array([0,-.07,-.365])
        for name in ['stationary','turn','unflagged_reset']:
            cache=self.root/name;cache.mkdir();position=np.zeros((len(t),3));angles=t/50*180 if name=='turn' else t*0
            quaternion=Rotation.from_euler('z',angles,degrees=True).as_quat()
            if name=='unflagged_reset':position[t>=25,0]=1000
            np.savez(cache/'lio_cache.npz',sow=t,position=position,quaternion_xyzw=quaternion,available_sow=t+.01,effective_points=t*0+1000,mean_abs_plane_residual_m=t*0)
            identity={**self.cache_id,'cache_sha256':hashlib.sha256((cache/'lio_cache.npz').read_bytes()).hexdigest()};(cache/'cache_identity.json').write_text(json.dumps(identity))
            times=np.arange(1,50);rotations=Rotation.from_euler('z',times/50*180 if name=='turn' else times*0,degrees=True)
            antenna=rotations.apply(np.tile(lever,(len(times),1)));g=np.column_stack([np.arange(len(times)),times,antenna,np.tile([1,1,2],(len(times),1))])
            nav,_=self.nav('P',rows=g,cache=cache);self.assertTrue(np.isfinite(nav).all());self.assertTrue((nav[:,6]==1).all())
            if name!='unflagged_reset':np.testing.assert_allclose(nav[:,1:4],0,atol=1e-12)
            else:
                # A numerical reset without a flag is not detected by this
                # interface. Preserve and disclose its wrong propagated jump.
                self.assertGreater(np.max(abs(nav[:,1])),900)
