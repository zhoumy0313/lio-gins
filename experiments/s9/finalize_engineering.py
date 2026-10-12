"""Validate common time/window/cache support, no GT trajectory comparison."""
import json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT));import numpy as np
from src.adapters.causal_lio import BufferedLIO
route=sys.argv[1];art=ROOT/'artifacts/s9'/route;c=json.loads((art/'technical_context.json').read_text());a=json.loads((art/'data_manifest.json').read_text());ic=json.loads((Path(c['initialization'])/'initial_condition.json').read_text());e=json.loads((Path(c['stress'])/'event_manifest.json').read_text());cache=np.load(Path(c['cache'])/'lio_cache.npz');b=BufferedLIO(cache['sow'],cache['position'],cache['quaternion_xyzw'],cache['available_sow'],max_span_s=.15)
start=ic['reference_epoch_sow'];end=min(f['metadata']['time_max'] for f in a['files'] if f['schema'] in ['reference_time_only','adis_increment']);assert b.query(start,available_until=start+.25)['valid']
assert start>=max(f['metadata']['time_min'] for f in a['files'] if f['schema'] in ['reference_time_only','adis_increment','f9p_spp'])
events=[]
for case in e['cases']:
 for ev in case['events']:
  assert ev['window_sow'][0]>=start and ev['window_sow'][1]<=end
  events.append({'case':case['id'],'offset_s':ev['requested_offset_s'],'direction':ev['direction_NED'],'fault_start_sow':ev['fault_start_sow'],'t_return_lower_bound_sow':ev['recovery_start_sow'],'post180_supported':True})
assert len(events)==21
r={'sequence':route,'common_sow':[start,end],'single_state_original_row':ic['reference_row_index'],'state_rows_read':ic['reference_state_rows_read'],'timestamp_only_selection':True,'earlier_reference_uncovered_not_evaluated':start-a['files'][3]['metadata']['time_min'],'duplicate_reference_policy':'stable first row by timestamp, all raw rows retained','events':events,'precision_opened':False,'initialization_SHA':hashlib.sha256((Path(c['initialization'])/'initial_condition.json').read_bytes()).hexdigest(),'cache_SHA':hashlib.sha256((Path(c['cache'])/'lio_cache.npz').read_bytes()).hexdigest()}
(art/'final_common_support.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
