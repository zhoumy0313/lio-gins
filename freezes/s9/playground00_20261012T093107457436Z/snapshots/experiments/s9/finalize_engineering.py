"""Validate common time/window/cache support, no GT trajectory comparison."""
import json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT));import numpy as np
from src.adapters.causal_lio import BufferedLIO
route=sys.argv[1];art=ROOT/'artifacts/s9'/route;c=json.loads((art/'technical_context.json').read_text());a=json.loads((art/'data_manifest.json').read_text());ic=json.loads((Path(c['initialization'])/'initial_condition.json').read_text());e=json.loads((Path(c['stress'])/'event_manifest.json').read_text());cache=np.load(Path(c['cache'])/'lio_cache.npz');b=BufferedLIO(cache['sow'],cache['position'],cache['quaternion_xyzw'],cache['available_sow'],max_span_s=.15)
start=ic['reference_epoch_sow'];end=min(f['metadata']['time_max'] for f in a['files'] if f['schema'] in ['reference_time_only','adis_increment']);end=min(end,float(cache['sow'][-1]));assert b.query(start,available_until=start+.25)['valid']
assert start>=max(f['metadata']['time_min'] for f in a['files'] if f['schema'] in ['reference_time_only','adis_increment','f9p_spp'])
events=[]
for case in e['cases']:
 for ev in case['events']:
  assert ev['window_sow'][0]>=start and ev['window_sow'][1]<=end
  events.append({'case':case['id'],'offset_s':ev['requested_offset_s'],'direction':ev['direction_NED'],'fault_start_sow':ev['fault_start_sow'],'t_return_lower_bound_sow':ev['recovery_start_sow'],'post180_supported':True})
assert len(events)==21
conf=json.loads((ROOT/'configs/s9/P.json').read_text());deadline=conf['max_LIO_availability_delay_s'];grid=np.arange(np.ceil(start*10),np.floor(end*10)+1)/10;g=np.loadtxt(Path(c['stress'])/'natural.csv',delimiter=',',skiprows=1);times=np.unique(np.r_[grid,g[(g[:,1]>start)&(g[:,1]<=grid[-1]),1]]);invalid=[float(t) for t in times if not b.query(t,available_until=t+deadline)['valid']]
assert not invalid,{'unsupported_timestamps':invalid,'rule':'technical input-time support, no error values or method result selection'}

r={'sequence':route,'common_sow':[start,end],'single_state_original_row':ic['reference_row_index'],'state_rows_read':ic['reference_state_rows_read'],'timestamp_only_selection':True,'earlier_reference_uncovered_not_evaluated':start-a['files'][3]['metadata']['time_min'],'duplicate_reference_policy':'stable first row by timestamp, all raw rows retained','events':events,'ADIS_end_minus_common_end_s':next(f['metadata']['time_max'] for f in a['files'] if f['schema']=='adis_increment')-end,'whole_grid_expected_samples':int(np.floor(end*10)-np.ceil(start*10)+1),'whole_common_output_and_GNSS_times_checked':len(times),'invalid_interpolation_or_availability_timestamps':invalid,'availability_deadline_s':deadline,'precision_opened':False,'initialization_SHA':hashlib.sha256((Path(c['initialization'])/'initial_condition.json').read_bytes()).hexdigest(),'cache_SHA':hashlib.sha256((Path(c['cache'])/'lio_cache.npz').read_bytes()).hexdigest()}
(art/'final_common_support.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
