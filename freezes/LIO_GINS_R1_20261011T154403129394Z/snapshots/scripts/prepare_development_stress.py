#!/usr/bin/env python3
"""Generate declared GNSS-only perturbations; no truth and no heldout access."""
import argparse,hashlib,json,os,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.adapters.geodesy import llh_to_ned
from src.adapters.research_access import verify_access,record_opening,check_raw_identity
p=argparse.ArgumentParser();p.add_argument('initialization_run');p.add_argument('--freeze');a=p.parse_args();root=Path(__file__).resolve().parents[1];out=Path(os.environ['LIO_GINS_RUN_DIR']);icpath=Path(a.initialization_run)/'initial_condition.json';ic=json.loads(icpath.read_text());protocolpath=root/'configs/development_experiment_protocol.json';protocol=json.loads(protocolpath.read_text())
seq=ic['sequence'];role=ic['role'];access=verify_access(seq,role,a.freeze);record_opening(access,'fixed_observed_data_pressure_preparation')
source=root/'data/i2nav-dataset'/seq/(seq+'_F9P_GNSS.pos');check_raw_identity(access,source);raw=np.loadtxt(source);g=np.column_stack([np.arange(len(raw)),raw[:,0],llh_to_ned(raw[:,1:4],ic['origin_ADIS_llh_deg_m'])+np.array(ic['reference_initial_local_NED_m']),raw[:,4:7]])
manifest={'sequence':seq,'role':role,'raw_gnss_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'initialization_sha256':hashlib.sha256(icpath.read_bytes()).hexdigest(),'protocol_sha256':hashlib.sha256(protocolpath.read_bytes()).hexdigest(),'derived_schema':['original_rowID','SOW','N','E','D','stdN','stdE','stdD'],'algorithm_access':'observed-data-only CSV; event manifest stays with offline evaluator','experiment_kind':'artificial_GNSS_pressure_on_real_route','cases':[],'no_truth_access':True,'holdout_performance_opened':role=='heldout'}
# End of usable reference metadata is read from identity manifest, not trajectory values.
data_manifest=json.loads((root/'data/manifests/DATA_MANIFEST.json').read_text());end=next(x['metadata']['time_max'] for x in data_manifest['files'] if x['filename']==seq+'_groundtruth.nav')
for case in [{'id':'natural','kind':'none'}]+protocol['stress_cases']:
 observed=g.copy();keep=np.ones(len(g),bool);events=[]
 for offset,direction in ([] if case['kind']=='none' else zip(protocol['event_starts_seconds_from_common_initial_epoch'],protocol['directions_NED'])):
  minimum=ic['reference_epoch_sow']+offset;j=int(np.searchsorted(g[:,1],minimum));t=float(g[j,1]);direction=np.array(direction)
  if case['kind']=='jump':
   stop=j+case['epochs'];observed[j:stop,2:5]+=direction*case['amplitude_m'];fault_end=float(g[stop-1,1])+1;recover_at=fault_end
  elif case['kind']=='loss':
   fault_end=t+case['duration_s'];keep[(g[:,1]>=t)&(g[:,1]<fault_end)]=False;recover_at=fault_end
   if case['recovery_bias_m']:
    bias=(g[:,1]>=fault_end)&(g[:,1]<fault_end+case['bias_hold_s']);observed[bias,2:5]+=direction*case['recovery_bias_m']
  elif case['kind']=='ramp':
   fault_end=t+case['ramp_s']+case['hold_s'];recover_at=fault_end
   active=(g[:,1]>=t)&(g[:,1]<fault_end);amplitude=np.minimum((g[active,1]-t)/case['ramp_s'],1)*case['amplitude_m'];observed[active,2:5]+=amplitude[:,None]*direction
  else:raise ValueError('unknown perturbation')
  window_end=fault_end+90
  if window_end>end:raise ValueError('predeclared event lacks recovery support; do not select by performance')
  events.append({'fault_start_sow':t,'fault_end_sow':fault_end,'recovery_start_sow':recover_at,'window_sow':[t-10,window_end],'direction_NED':direction.tolist(),'original_start_row_id':int(g[j,0]),'requested_offset_s':offset,'actual_offset_s':t-ic['reference_epoch_sow'],'fault_parameters':case})
 derived=out/(case['id']+'.csv');np.savetxt(derived,observed[keep],delimiter=',',fmt='%.12f',header=','.join(manifest['derived_schema']),comments='')
 identity={'sequence':seq,'role':role,'input_kind':'observed_GNSS_NED_only','derived_sha256':hashlib.sha256(derived.read_bytes()).hexdigest(),'raw_gnss_sha256':manifest['raw_gnss_sha256'],'initialization_sha256':manifest['initialization_sha256'],'columns':manifest['derived_schema'],'fault_labels_included':False}
 derived.with_suffix('.identity.json').write_text(json.dumps(identity,indent=2)+'\n')
 manifest['cases'].append({'id':case['id'],'data_path':str(derived),'sha256':hashlib.sha256(derived.read_bytes()).hexdigest(),'events':events,'original_rows':len(g),'kept_rows':int(keep.sum()),'deleted_original_row_ids':g[~keep,0].astype(int).tolist()})
if access is not None:manifest['freeze_id']=access['freeze_id']
(out/'event_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'cases':len(manifest['cases']),'events':sum(len(c['events']) for c in manifest['cases']),'no_performance_evaluation':True}))
