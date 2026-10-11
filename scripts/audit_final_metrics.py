#!/usr/bin/env python3
"""Recompute all frozen heldout errors from raw nav, independent of evaluator.

No estimator/evaluation helper imports. Original sealed results are read-only.
This is an archive audit after test opening, never another blind experiment.
"""
import hashlib,json,os
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
out=Path(os.environ['LIO_GINS_RUN_DIR'])
matrixfile=ROOT/'outputs/20261011T154446522435Z_P5_ae13844a/heldout_matrix.json'
m=json.loads(matrixfile.read_text());icfile=Path(m['initialization'])/'initial_condition.json';ic=json.loads(icfile.read_text())
eventsfile=Path(m['stress'])/'event_manifest.json';events=json.loads(eventsfile.read_text())
refpath=ROOT/'data/i2nav-dataset/parking00/parking00_groundtruth.nav';ref=np.loadtxt(refpath)
data=json.loads((ROOT/'data/manifests/DATA_MANIFEST.json').read_text());end=min(ref[-1,0],next(f['metadata']['time_max'] for f in data['files'] if f['filename']=='parking00_ADIS16465_IMU.txt'))
times=np.arange(int(np.ceil(ic['reference_epoch_sow']*10)),int(np.floor(end*10))+1)/10
# Explicit scalar-axis interpolation and gap mask independently construct truth.
truth=np.column_stack([np.interp(times,ref[:,0],ref[:,axis]) for axis in (1,2,3)])
right=np.searchsorted(ref[:,0],times,side='left');left=np.maximum(right-1,0);right=np.minimum(right,len(ref)-1)
refgood=(times>=ref[0,0])&(times<=ref[-1,0])&((ref[right,0]-ref[left,0])<=ic['protocol']['reference_max_interpolation_gap_s'])
truth[~refgood]=np.nan
configs=json.loads((ROOT/'configs/final_evaluation_methods.json').read_text());checks=[];binding={}
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def rmse(err):
    valid=np.isfinite(err).all(axis=1)
    return float(np.sqrt(np.mean(err[valid,0]**2+err[valid,1]**2))) if valid.any() else None
for method,records in m['complete_methods'].items():
    for r in records:
        backend=Path(r['backend']['output']);navfile=backend/'trajectory.csv';nav=np.loadtxt(navfile,delimiter=',',skiprows=1)
        loc=np.searchsorted(nav[:,0],times);loc=np.clip(loc,0,len(nav)-1);good=(abs(nav[loc,0]-times)<1e-8)&(nav[loc,6]==1)
        err=nav[loc,1:4]-truth;err[~good]=np.nan;expected=r['metrics']['metrics'];whole=rmse(err)
        case=next(c for c in events['cases'] if c['id']==r['case']);ev=[]
        for event in case['events']:
            low,high=event['window_sow'];ev.append(rmse(err[(times>=low)&(times<=high)]))
        identity=json.loads((backend/'backend_identity.json').read_text());conf=json.loads((backend/'backend_resolved.json').read_text())
        binding.setdefault(method,[]).append({'case':r['case'],'backend_run':str(backend),'evaluation_run':r['evaluation'],'trajectory_SHA':sha(navfile),'update_SHA':sha(backend/'per_update.jsonl'),'configuration_SHA':sha(backend/'backend_resolved.json'),'input_SHA':identity['gnss_sha256'],'cache_SHA':identity['source_cache_sha256'],'initialization_SHA':identity['initialization_sha256']})
        exact_input=identity['source_cache_run']==m['cache'] and identity['initialization_run']==m['initialization'] and identity['gnss_sha256']==case['sha256'] and conf==configs[method]
        deltas=[abs(a-b['metrics']['horizontal_rmse_m']) for a,b in zip(ev,r['metrics']['events'])]
        valid_count=int(np.isfinite(err).all(axis=1).sum());passed=abs(whole-expected['horizontal_rmse_m'])<1e-10 and all(x<1e-10 for x in deltas) and expected['samples_expected']==len(times) and expected['samples_valid']==valid_count and exact_input
        checks.append({'method':method,'case':r['case'],'whole_RMSE_m':whole,'whole_difference_m':whole-expected['horizontal_rmse_m'],'event_RMSE_m':ev,'maximum_event_difference_m':max(deltas,default=0),'samples_expected':len(times),'samples_valid':valid_count,'coverage':valid_count/len(times),'shared_input_config_binding':exact_input,'passed':passed})
freeze=Path(m['freeze_directory']);f=json.loads((freeze/'scientific_freeze.json').read_text())
unchanged={p:sha(ROOT/p)==h for group in ['source_SHA','config_SHA'] for p,h in f[group].items()}
passed=all(c['passed'] for c in checks) and len(checks)==80 and all(unchanged.values())
(out/'final_metric_audit.json').write_text(json.dumps({'all_passed':passed,'matrix_run':str(matrixfile.parent),'checks':checks,'freeze_current_files_unchanged':unchanged,'claim_bindings':binding,'input_SHA':{str(p):sha(p) for p in [matrixfile,icfile,eventsfile,refpath]},'scope':'independent recomputation from raw trajectories/reference; no new estimates, no retuning, no new blind test'},indent=2)+'\n')
print(json.dumps({'all_passed':passed,'pairs':len(checks),'max_whole_difference_m':max(abs(c['whole_difference_m']) for c in checks),'max_event_difference_m':max(c['maximum_event_difference_m'] for c in checks),'all_frozen_source_config_unchanged':all(unchanged.values())}))
if not passed:raise SystemExit(2)
