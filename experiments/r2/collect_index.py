"""Read old evidence without modifying any R1 output or interpreting it as new test."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def load(rel):return json.loads((ROOT/rel).read_text())
def old_index():
    rows=[]
    final=load('outputs/20261011T151637778113Z_P4_bc2078b6/final_verification.json')
    for cache,methods in final['records'].items():
        for method,records in methods.items():
            for r in records:rows.append({'cache':cache,'method':'Clock2' if method=='P_time_only' else method,'case':r['case'],'backend':r['backend']['output'],'evaluation':r['evaluation'],'config':r['config'],'inherited':True})
    selected=load('outputs/20261011T141054205503Z_P3_e03a0b15/selected_baselines.json')
    for r in selected['complete_selected']['B2']:rows.append({'cache':'primary','method':'B2','case':r['case'],'backend':r['backend']['output'],'evaluation':r['evaluation'],'config':r['config'],'inherited':True})
    long=load('outputs/20261011T161516459969Z_P4_caf05023/long_wait_audit.json')
    for key,records in long['records'].items():
        cache='primary' if key.startswith('20261011T141044') else 'sensitivity'
        for r in records:rows.append({'cache':cache,'method':'Clock'+key.rsplit('_',1)[-1],'case':r['case'],'backend':r['backend']['output'],'evaluation':r['evaluation'],'config':r['config'],'inherited':True})
    parking=load('outputs/20261011T154446522435Z_P5_ae13844a/heldout_matrix.json')
    for method,records in parking['complete_methods'].items():
        for r in records:rows.append({'cache':'parking','method':'Clock2' if method=='P_time_only' else method,'case':r['case'],'backend':r['backend']['output'],'evaluation':r['evaluation'],'config':r['config'],'inherited':True})
    return rows
if __name__=='__main__':
    import os
    out=Path(os.environ['LIO_GINS_RUN_DIR']);rows=old_index();(out/'inherited_index.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps({'inherited_pairs':len(rows),'performance_new_route_accessed':False}))
