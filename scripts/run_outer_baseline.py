#!/usr/bin/env python3
"""Shared cached LIO/F9P B2-B6 replay. No reference or fault-label access."""
import argparse,hashlib,json,os,sys,time
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.adapters.geodesy import llh_to_ned
from src.adapters.sensor_text import receiver_covariance
from src.adapters.causal_lio import BufferedLIO
from src.fusion.position_kf import PositionKF
from src.fusion.fixed_recovery import FixedRecovery
p=argparse.ArgumentParser();p.add_argument('cache_run');p.add_argument('initialization_run');p.add_argument('config');p.add_argument('--gnss-ned');a=p.parse_args()
root=Path(__file__).resolve().parents[1];out=Path(os.environ['LIO_GINS_RUN_DIR']);cache=Path(a.cache_run).resolve();ic_path=Path(a.initialization_run)/'initial_condition.json';ic=json.loads(ic_path.read_text());conf=json.loads(Path(a.config).read_text());cache_id=json.loads((cache/'cache_identity.json').read_text());cache_path=cache/'lio_cache.npz'
if ic['sequence']!='building00' or cache_id['role']!='development':raise ValueError('heldout replay is closed')
if hashlib.sha256(cache_path.read_bytes()).hexdigest()!=cache_id['cache_sha256']:raise ValueError('cache identity changed')
method=conf['method']
if method not in ['B2','B3','B4','B5','B6']:raise ValueError('this entry runs established baselines only')
c=np.load(cache_path);buffer=BufferedLIO(c['sow'],c['position'],c['quaternion_xyzw'],c['available_sow'],max_span_s=conf['max_LIO_span_s'])
start=ic['reference_epoch_sow'];initial=buffer.query(start)
if not initial['valid']:raise ValueError('initial LIO epoch unavailable')
A=np.array(ic['R_NED_body_initial'])@initial['rotation'].T
translation=np.array(ic['reference_initial_local_NED_m']);kf=PositionKF(translation,np.diag(np.array(ic['initial_F9P_std_NED_m'])**2),A)
lever=np.array(ic['antenna_lever_FRD_m']);floor=np.array(ic['protocol']['GNSS_std_floor_NED_m'])
if a.gnss_ned:
    source=Path(a.gnss_ned).resolve();input_id=json.loads(source.with_suffix('.identity.json').read_text())
    if input_id['role']!='development' or input_id['sequence']!='building00' or input_id['fault_labels_included']:raise ValueError('closed heldout or labeled algorithm input')
    if hashlib.sha256(source.read_bytes()).hexdigest()!=input_id['derived_sha256'] or hashlib.sha256(ic_path.read_bytes()).hexdigest()!=input_id['initialization_sha256']:raise ValueError('derived input/initialization identity changed')
    g=np.loadtxt(source,delimiter=',',skiprows=1,ndmin=2)
    # Explicit observed-data-only schema: rowID,SOW,N,E,D,stdN,stdE,stdD.
    if g.shape[1]!=8:raise ValueError('derived GNSS schema mismatch')
else:
    source=root/'data/i2nav-dataset/building00/building00_F9P_GNSS.pos';raw=np.loadtxt(source)
    g=np.column_stack([np.arange(len(raw)),raw[:,0],llh_to_ned(raw[:,1:4],ic['origin_ADIS_llh_deg_m'])+translation,raw[:,4:7]])
if np.any(np.diff(g[:,1])<=0) or len(set(g[:,0]))!=len(g):raise ValueError('GNSS ordering/IDs changed ambiguously')
end=float(c['sow'][-1]);grid=np.arange(int(np.ceil(start*10)),int(np.floor(end*10))+1)/10
# All raw sensor-supported times stay in the output, even after reference ends.
g=g[(g[:,1]>start)&(g[:,1]<=grid[-1])];events=np.unique(np.r_[grid,g[:,1]])
grid_set=set(grid.tolist())
recovery=FixedRecovery(**conf['recovery']) if method=='B6' else None
last_l=initial['position'];last_t=start;previous_output_available=initial['available_time'];gid=0;rows=[];updates=[];replay_start=time.monotonic();broken=False
for t in events:
    l=buffer.query(t)
    if not l['valid'] or broken:
        broken=True
        if t in grid_set:rows.append([t,np.nan,np.nan,np.nan,np.nan,np.nan,0])
        # No silent reset/jump or future reference substitution.
        continue
    dt=t-last_t;delta=l['position']-last_l;distance=float(np.linalg.norm(delta))
    qscale=conf['q_time_m2ps']*dt+conf['q_distance_m2pm']*distance
    kf.propagate(delta,np.diag(np.array(conf['q_axis_scale'])*qscale));last_l=l['position'];last_t=t
    available=max(previous_output_available,l['available_time'],t);previous_output_available=available
    if gid<len(g) and g[gid,1]==t:
        row=g[gid];gid+=1;obs_id=int(row[0]);R_nb=A@l['rotation'];log={'original_gnss_id':obs_id,'measurement_sow':float(t),'available_sow':float(available),'accepted':False,'reason':'LIO_only','state':'NORMAL','r_multiplier':1.,'correction_norm_m':0.,'nominal_nis':None}
        if method!='B2':
            try:r=receiver_covariance(row[5:8],floor)
            except ValueError:
                kf.seen_gnss_ids.add(obs_id);log['reason']='invalid_receiver_std'
            else:
                residual=row[2:5]-(kf.p+R_nb@lever);nominal_nis=float(residual@np.linalg.solve(kf.P+r,residual));log['nominal_nis']=nominal_nis
                decision=recovery.decide(float(t),nominal_nis) if recovery else {'admit':True,'state':'NORMAL','r_multiplier':1.}
                log['state']=decision['state'];protection=decision['r_multiplier']
                if decision['admit']:
                    policy={'B3':'disabled','B4':'nis','B5':'huber','B6':'huber'}[method]
                    result=kf.update(obs_id,row[2:5],r,R_nb,lever,policy=policy,nis_limit=conf['nis_limit'],huber_limit=conf['huber_limit'],external_r_multiplier=protection);log.update(result)
                else:
                    if obs_id in kf.seen_gnss_ids:raise ValueError('GNSS ID reused while waiting')
                    kf.seen_gnss_ids.add(obs_id);log.update(reason='fixed_wait')
        updates.append(log)
    if t in grid_set:rows.append([t,*kf.p,available,available-t,1])
np.savetxt(out/'trajectory.csv',np.array(rows),delimiter=',',header='sow,N,E,D,available_sow,delay_s,valid',comments='')
(out/'per_update.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in updates));(out/'backend_resolved.json').write_text(json.dumps(conf,indent=2)+'\n')
(out/'backend_identity.json').write_text(json.dumps({'method':method,'kind':'cached_backend','source_cache_run':str(cache),'source_cache_sha256':cache_id['cache_sha256'],'gnss_source':str(source),'gnss_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'initialization_run':str(Path(a.initialization_run).resolve()),'initialization_sha256':hashlib.sha256(ic_path.read_bytes()).hexdigest(),'A_NED_local':A.tolist(),'initial_lio_position':initial['position'].tolist(),'outputs_expected':len(grid),'outputs_valid':sum(int(r[-1]) for r in rows),'consumed_gnss_updates':len(updates),'no_reference_access':True,'output_delay_policy':'two endpoints required; availability from conservative replay clock-resolution bound','replay_wall_seconds':time.monotonic()-replay_start,'timing_scope':'Python cached backend only, includes logging construction, excludes frontend/initial loading','LIO_gap_policy':'mark unavailable through remaining route, no hidden jump','all_GNSS_used_at_most_once':True},indent=2)+'\n')
print(json.dumps({'method':method,'output_rows':len(rows),'updates':len(updates),'broken_LIO':broken}))
if broken:sys.exit(2)
