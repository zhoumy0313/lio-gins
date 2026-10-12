"""S10 read-only sources and explicit inherited metric conventions."""
import csv, gzip, hashlib, json, math, os, sys
from functools import lru_cache
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation, Slerp
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from src.evaluation.reference import interpolate_with_gaps
BASE='4f7a4b4c5b87040d7d7307f25a06cd785b1ff7b9'
ROUTES=[('building00','primary','artifacts/r2/S3','seen development',False),('building00_repeat','sensitivity','artifacts/r2/S3','same-bag sensitivity',True),('parking00','parking','artifacts/r2/S3','seen retrospective',False),('building01','building01','artifacts/s8/C','S8 test, now seen',False),('street00','street00','artifacts/s9/street00/C','S9 test, now seen',False),('playground00','playground00','artifacts/s9/playground00/C','S9 test, now seen',False),('building02','building02','artifacts/s9/building02/C','S9 test, now seen',False)]
METHODS=['B2','B3','B4','B5','B6','NIS0','NIS1','NIS2','Clock2','Clock5','Clock10','Clock15','Clock30','Clock60','Clock90','P','P_without_motion','P_without_anchor','P_without_decay']
CASES=['loss30_bias3','loss30_bias10','loss30_normal']
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def resolve(p):
 p=Path(p)
 if p.exists():return p.resolve()
 # Relocation only with later SHA verification, never a favorable-run search.
 for marker in ['/outputs_s9/','/outputs_s8/','/outputs_r2/','/outputs/']:
  if marker in str(p):
   q=ROOT/(marker.strip('/')+'/'+str(p).split(marker,1)[1])
   if q.exists():return q
 raise FileNotFoundError(p)
def read_json(p):
 p=resolve(p)
 with (gzip.open(p,'rt') if p.suffix=='.gz' else p.open()) as f:return json.load(f)
def csv_write(p,rows):
 if not rows:raise ValueError('empty output is not a completed analysis')
 with Path(p).open('x',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def json_write(p,obj):
 with Path(p).open('x') as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')
def macro(values):
 if len(values)!=3:raise ValueError('exactly three registered events required')
 return float(np.mean(values)) if all(v is not None and math.isfinite(v) for v in values) else None
def improvement(p,n):return (n-p)/n if p is not None and n is not None and n>0 else None
def clocks(updates,returned,horizon=180):
 first=next((u for u in updates if returned<=u['measurement_sow']<returned+horizon and u['accepted'] is True),None)
 return (first['measurement_sow']-returned,first['available_sow']-returned,first['original_gnss_id']) if first else (None,None,None)
def qualified(natural,cap,delays,coverage=True):return bool(natural is not None and natural<=cap+1e-12 and len(delays)==3 and all(t is not None and t<=15+1e-8 for t in delays) and coverage)
def method_role(m,config):
 if m.startswith('NIS'):return 'strict NIS '+str(config['nis_limit'])
 return {'B2':'LIO-only','B3':'direct position fusion','B4':'wide NIS100','B5':'Huber2.5','B6':'availability recovery','P_without_motion':'B6 alias'}.get(m,m)
@lru_cache(None)
def archived(folder):return read_json(ROOT/folder/'event_results.json.gz')
@lru_cache(None)
def catalog():
 result={}
 for route,label,folder,role,repeat in ROUTES:
  rows=[r for r in archived(folder) if r['cache']==label]
  assert len(rows)==152 and {r['method'] for r in rows}==set(METHODS)
  result[route]={'route':route,'cache_label':label,'folder':folder,'role':role,'repeat':repeat,'rows':{(r['method'],r['case']):r for r in rows}}
 return result
@lru_cache(None)
def route_context(route):
 item=catalog()[route];row=item['rows'][('P','loss30_bias3')];run=resolve(row['backend']);identity=read_json(run/'backend_identity.json');icp=resolve(Path(identity['initialization_run'])/'initial_condition.json');ic=read_json(icp);stress=resolve(identity['gnss_source']).parent;cache=resolve(identity['source_cache_run']);seq=ic['sequence'];refp=ROOT/'data/i2nav-dataset'/seq/(seq+'_groundtruth.nav');ref=np.loadtxt(refp,ndmin=2)
 assert ref.shape[1]==10 and np.isfinite(ref).all() and np.all(np.diff(ref[:,0])>=0)
 ref=ref[np.r_[True,np.diff(ref[:,0])>0]]
 manifestp=ROOT/('artifacts/s9/'+route+'/data_manifest.json' if route in ['street00','playground00','building02'] else 'artifacts/s8/data_manifest.json' if route=='building01' else 'data/manifests/DATA_MANIFEST.json')
 meta=read_json(manifestp);end=min(ref[-1,0],next(f['metadata']['time_max'] for f in meta['files'] if f['filename']==seq+'_ADIS16465_IMU.txt'))
 if route in ['street00','playground00','building02']:end=min(end,read_json(cache/'cache_identity.json')['time_sow_range'][1])
 grid=np.arange(math.ceil(ic['reference_epoch_sow']*10),math.floor(end*10)+1)/10
 truth,valid=interpolate_with_gaps(ref[:,0],ref[:,1:4],grid,ic['protocol']['reference_max_interpolation_gap_s'])
 assert len(grid)==item['rows'][('P','natural')]['whole']['samples_expected']
 return dict(item,identity=identity,ic=ic,icp=icp,stress=stress,cache=cache,reference=ref,reference_path=refp,grid=grid,truth=truth,reference_valid=valid,event_manifest=read_json(stress/'event_manifest.json'))
def load_gnss(p):
 a=np.loadtxt(p,delimiter=',',skiprows=1,ndmin=2)
 assert a.shape[1]==8 and np.isfinite(a).all() and np.all(np.diff(a[:,1])>0) and len(set(a[:,0]))==len(a)
 return a
@lru_cache(maxsize=8)
def updates(run):
 rows=[json.loads(s) for s in (resolve(run)/'per_update.jsonl').read_text().splitlines()]
 assert rows and all({'original_gnss_id','measurement_sow','available_sow','accepted','reason','nominal_nis','correction_norm_m'}<=r.keys() for r in rows)
 assert len({r['original_gnss_id'] for r in rows})==len(rows) and np.all(np.diff([r['measurement_sow'] for r in rows])>0)
 assert all(r['available_sow']>=r['measurement_sow'] and isinstance(r['accepted'],bool) for r in rows)
 return rows
def trajectory_errors(route,run):
 c=route_context(route);a=np.loadtxt(resolve(run)/'trajectory.csv',delimiter=',',skiprows=1,ndmin=2)
 assert a.shape[1]==7 and np.all(np.diff(a[:,0])>0)
 j=np.searchsorted(a[:,0],c['grid']);ix=np.clip(j,0,len(a)-1);valid=(j<len(a))&(abs(a[ix,0]-c['grid'])<1e-8)&(a[ix,6]==1)
 error=a[ix,1:4]-c['truth'];error[~valid]=np.nan
 return c['grid'],error
def window(grid,error,start,duration):
 selected=(grid>=start-1e-8)&(grid<start+duration-1e-8);h=np.linalg.norm(error[selected,:2],axis=1);expected=round(duration*10);n=int(np.isfinite(h).sum());complete=len(h)==expected and n==expected
 return {'RMSE':float(np.sqrt(np.mean(h*h))) if complete else None,'P95':float(np.percentile(h,95)) if complete else None,'Max':float(np.max(h)) if complete else None,'coverage':n/expected,'samples':len(h),'expected':expected}
def events(route,case):return next(c for c in route_context(route)['event_manifest']['cases'] if c['id']==case)['events']
def antenna_truth(c,t):
 ref=c['reference'];t=np.asarray(t,float);p,v=interpolate_with_gaps(ref[:,0],ref[:,1:4],t,c['ic']['protocol']['reference_max_interpolation_gap_s']);assert v.all(),'missing reference support retained as failure'
 rot=Slerp(ref[:,0],Rotation.from_euler('ZYX',ref[:,7:10][:,::-1],degrees=True))(t)
 return p+rot.apply(np.tile(c['ic']['antenna_lever_FRD_m'],(len(t),1)))
def local_antenna(c,t):
 n=np.load(c['cache']/'lio_cache.npz');t=np.asarray(t,float);assert np.all((t>=n['sow'][0])&(t<=n['sow'][-1]))
 p=np.column_stack([np.interp(t,n['sow'],n['position'][:,j]) for j in range(3)]);rot=Slerp(n['sow'],Rotation.from_quat(n['quaternion_xyzw']))(t).as_matrix();A=np.array(c['identity']['A_NED_local']);lever=np.array(c['ic']['antenna_lever_FRD_m'])
 return (p-np.array(c['identity']['initial_lio_position']))@A.T+np.array(c['ic']['reference_initial_local_NED_m'])+np.einsum('ij,njk,k->ni',A,rot,lever)
