"""Bounded read-only comparison; no new frontend, parameter tuning, or causal guess."""
import json,os,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=Path(os.environ['LIO_GINS_RUN_DIR']);names=['20261011T141044340351Z_P2_9dd3f300','20261011T134125698776Z_P2_0de7714e'];identities=[json.loads((ROOT/'outputs'/n/'cache_identity.json').read_text()) for n in names];caches=[np.load(ROOT/'outputs'/n/'lio_cache.npz') for n in names];a,b=caches
assert np.array_equal(a['sow'],b['sow']);diff=np.linalg.norm(a['position']-b['position'],axis=1);changed=np.flatnonzero(diff>1e-8);first=int(changed[0]);common={k:identities[0]['input_identity'][k]==identities[1]['input_identity'][k] for k in ['bag','sha256','image','sensors']}
front=[Path(i['source_frontend_run']) for i in identities];logs=[]
for run in front:
    selected={}
    for f in run.rglob('*'):
        if f.is_file() and f.suffix in ['.log','.json','.yaml'] and f.stat().st_size<2**20:
            text=f.read_text(errors='replace');lines=[l for l in text.splitlines() if any(w in l.lower() for w in ['thread','clock','rosbag play','initial','end of file','eof','point','rate'])];selected[str(f.relative_to(run))]={'SHA':hashlib.sha256(f.read_bytes()).hexdigest(),'diagnostic_lines':lines[:12]}
    logs.append({'frontend_run':str(run),'files':selected})
result={'cache_runs':names,'common_identities':common,'same_pose_timestamps':True,'rows':len(diff),'3D_position_RMS_difference_m':float(np.sqrt(np.mean(diff**2))),'first_nonidentical_index':first,'first_nonidentical_sow':float(a['sow'][first]),'first_nonidentical_elapsed_s':float(a['sow'][first]-a['sow'][0]),'maximum_position_difference_m':float(diff.max()),'timing_complete_each':[i['timing_complete'] for i in identities],'raw_frames_each':[i['expected_raw_AT128_frames'] for i in identities],'output_rows_each':[i['output_rows'] for i in identities],'logs':logs,'root_cause':'UNRESOLVED; source/inputs/timestamps agree but recorded clock availability and execution termination differ; no evidence proves concurrency as cause','new_frontend_runs':0,'selection':'keep both predetermined caches, pair every method within each; no choose-better-cache promotion','unflagged_reset_detection':'not implemented; old synthetic reset test preserves large incorrect propagated jump'}
(OUT/'frontend_diagnosis.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='logs'}))
