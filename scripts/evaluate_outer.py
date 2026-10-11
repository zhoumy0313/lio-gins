#!/usr/bin/env python3
"""Independent offline baseline evaluator; fixed grid and preregistered events."""
import argparse,hashlib,json,os,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.evaluation.reference import load_i2nav_local_ned,interpolate_with_gaps,horizontal_metrics
from src.adapters.research_access import verify_access,record_opening,check_raw_identity
p=argparse.ArgumentParser();p.add_argument('backend_run');p.add_argument('event_manifest');p.add_argument('case_id');p.add_argument('--freeze');a=p.parse_args();root=Path(__file__).resolve().parents[1];out=Path(os.environ['LIO_GINS_RUN_DIR']);run=Path(a.backend_run).resolve();manifest=json.loads((run/'manifest.json').read_text());identity=json.loads((run/'backend_identity.json').read_text());eventpath=Path(a.event_manifest).resolve();event_manifest=json.loads(eventpath.read_text());case=next(c for c in event_manifest['cases'] if c['id']==a.case_id)
seq=event_manifest['sequence'];role=event_manifest['role'];access=verify_access(seq,role,a.freeze);record_opening(access,'offline_fixed_protocol_evaluation')
if identity.get('sequence',seq)!=seq or identity.get('role',role)!=role:raise ValueError('backend/evaluation route mismatch')
if manifest['status'] not in ['PASSED','FAILED','BLOCKED']:raise ValueError('unfinished backend')
if identity['gnss_sha256']!=case['sha256']:raise ValueError('event manifest/input identity mismatch')
ic_path=Path(identity['initialization_run'])/'initial_condition.json';ic=json.loads(ic_path.read_text());protocol_path=root/'configs/development_experiment_protocol.json';protocol=json.loads(protocol_path.read_text())
if hashlib.sha256(protocol_path.read_bytes()).hexdigest()!=event_manifest['protocol_sha256']:raise ValueError('experiment protocol changed after event preparation')
refpath=root/'data/i2nav-dataset'/seq/(seq+'_groundtruth.nav');check_raw_identity(access,refpath);ref=load_i2nav_local_ned(refpath);nav=np.loadtxt(run/'trajectory.csv',delimiter=',',skiprows=1,ndmin=2)
if nav.shape[1]!=7 or np.any(np.diff(nav[:,0])<=0):raise ValueError('invalid backend output clock/schema')
loc_manifest=json.loads((root/'data/manifests/DATA_MANIFEST.json').read_text());sensor_end=next(x['metadata']['time_max'] for x in loc_manifest['files'] if x['filename']==seq+'_ADIS16465_IMU.txt');start=ic['reference_epoch_sow'];end=min(sensor_end,ref[-1,0]);grid=np.arange(int(np.ceil(start*10)),int(np.floor(end*10))+1)/10
j=np.searchsorted(nav[:,0],grid);index=np.clip(j,0,len(nav)-1);matches=(j<len(nav))&(np.abs(nav[index,0]-grid)<1e-8)&(nav[index,6]==1);n=nav[index,1:4].copy();n[~matches]=np.nan
r,refvalid=interpolate_with_gaps(ref[:,0],ref[:,1:4],grid,ic['protocol']['reference_max_interpolation_gap_s']);err=n-r;h=np.linalg.norm(err[:,:2],axis=1);metrics=horizontal_metrics(err,len(grid));metrics['vertical_rmse_m']=float(np.sqrt(np.nanmean(err[:,2]**2)))
np.savetxt(out/'per_epoch.csv',np.column_stack([grid,n,r,err,matches,refvalid,nav[index,5]]),delimiter=',',header='sow,N,E,D,ref_N,ref_E,ref_D,error_N,error_E,error_D,output_available,reference_available,delay_s',comments='')
updates=[json.loads(x) for x in (run/'per_update.jsonl').read_text().splitlines()];updates=[u for u in updates if grid[0]<=u['measurement_sow']<=grid[-1]];corrections=np.array([u['correction_norm_m'] for u in updates],float)
events=[]
for event in case['events']:
 window=event['window_sow'];selected=(grid>=window[0])&(grid<=window[1]);m=horizontal_metrics(err[selected],int(selected.sum()));valid=np.isfinite(h[selected]);m['horizontal_MAE_integral_m_s']=float(np.sum(h[selected][valid])*.1) if valid.all() else None
 recovery_start=event['recovery_start_sow'];ri=np.flatnonzero((grid>=recovery_start)&(grid<=recovery_start+protocol['recovery_timeout_s']));needed=int(np.ceil(protocol['recovery_required_duration_s']*10))+1;recovered=None
 for k in range(max(0,len(ri)-needed+1)):
  chunk=ri[k:k+needed]
  if np.all(np.isfinite(h[chunk])&(h[chunk]<=protocol['recovery_error_threshold_m'])):recovered=float(grid[chunk[0]]-recovery_start);break
 m['recovery_time_s']=recovered;m['recovered_within_timeout']=recovered is not None
 events.append({'event':event,'metrics':m})
rawgnss=np.loadtxt(root/'data/i2nav-dataset'/seq/(seq+'_F9P_GNSS.pos'));gi=np.searchsorted(rawgnss[:,0],grid,side='right')-1;gi=np.clip(gi,0,len(rawgnss)-1);quality=(np.linalg.norm(rawgnss[gi,4:6],axis=1)<=2)&(rawgnss[gi,6]<=4)&(grid-rawgnss[gi,0]<=1.5);normal_quality=horizontal_metrics(err[quality],int(quality.sum()))
result={'method':identity['method'],'source_backend_run':str(run),'source_cache_run':identity['source_cache_run'],'source_cache_sha256':identity['source_cache_sha256'],'case_id':case['id'],'case_data_sha256':case['sha256'],'sequence':seq,'role':role,'freeze_id':access['freeze_id'] if access else None,'experiment_kind':'natural' if case['id']=='natural' else 'artificial_GNSS_pressure_on_real_route','metrics':metrics,'receiver_STD_defined_quality_subset':normal_quality,'quality_subset_note':'input quality only; not truth-defined GNSS correctness; normal-cost gate applies natural case only','events':events,'event_macro_RMSE_m':float(np.mean([e['metrics']['horizontal_rmse_m'] for e in events])) if events and all(e['metrics']['horizontal_rmse_m'] is not None for e in events) else None,'update_correction_max_m':float(corrections.max()) if len(corrections) else None,'update_correction_p95_m':float(np.percentile(corrections,95)) if len(corrections) else None,'GNSS_rejection_fraction':float(np.mean([not u['accepted'] for u in updates])) if updates and identity['method']!='B2' else None,'output_delay_max_s':float(np.nanmax(nav[index,5])),'output_delay_p95_s':float(np.nanpercentile(nav[index,5],95)),'reference_point':'ADIS16465_center','alignment':'one common predetermined initial translation/rotation; no full-trajectory fit','quantity':'initial_position_conditioned_error_not_absolute_WGS84','reference_dependency':'MM/INS uses AT128, not independent reference sensing','grid_source':'declared initial epoch and raw IMU/reference overlap, not successful output intersection','backend_status':manifest['status'],'holdout_performance_opened':role=='heldout','input_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [refpath,run/'trajectory.csv',run/'per_update.jsonl',eventpath,protocol_path,ic_path]}}
(out/'metrics.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if metrics['coverage']<.99:sys.exit(2)
