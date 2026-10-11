#!/usr/bin/env python3
"""Read-only exact source, original data and existing-cache inheritance audit."""
import hashlib,json,os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];out=Path(os.environ['LIO_GINS_RUN_DIR'])
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
freeze=ROOT/'freezes/LIO_GINS_R1_20261011T154403129394Z';record=json.loads((freeze/'scientific_freeze.json').read_text());checks={p:sha(ROOT/p)==h for group in ['source_SHA','config_SHA'] for p,h in record[group].items()};checks['freeze_JSON']=sha(freeze/'scientific_freeze.json')==(freeze/'scientific_freeze.sha256').read_text().strip()
raw=[]
for r in json.loads((ROOT/'data/manifests/DATA_MANIFEST.json').read_text())['files']:
 p=Path(r['path']);actual=sha(p);raw.append({'path':str(p),'bytes':p.stat().st_size,'expected_SHA':r['sha256'],'actual_SHA':actual,'passed':actual==r['sha256']});print('raw verified '+p.name,flush=True)
caches=[]
for name in ['20261011T141044340351Z_P2_9dd3f300','20261011T134125698776Z_P2_0de7714e','20261011T160558488156Z_P5_3b1dbc60']:
 folder=ROOT/'outputs'/name;identity=json.loads((folder/'cache_identity.json').read_text());actual=sha(folder/'lio_cache.npz');caches.append({'run':str(folder),'actual_SHA':actual,'expected_SHA':identity['cache_sha256'],'passed':actual==identity['cache_sha256'],'R2_role':'seen_retrospective'})
base='c12a42a3484458e1737e63201792e1122fc99c0d';old=subprocess.check_output(['git','rev-parse','research/lio-gins-r1'],cwd=ROOT,text=True).strip();checks['R1_branch_unchanged']=old==base
sources={}
for folder in ['src','configs/baselines','configs/methods','paper/working','paper/versions','freezes/LIO_GINS_R1_20261011T154403129394Z']:
 for p in (ROOT/folder).rglob('*'):
  if p.is_file() and '__pycache__' not in str(p):sources[str(p.relative_to(ROOT))]=sha(p)
result={'R1_base_SHA':base,'R1_branch_SHA':old,'checks':checks,'raw_files':raw,'caches':caches,'inherited_file_SHA':sources,'R1_conclusion_preserved':'NO_ADDITIONAL_GAIN','new_route_performance_accessed':False,'all_passed':all(checks.values()) and all(r['passed'] for r in raw+caches)}
(out/'inheritance_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'all_passed':result['all_passed'],'raw_count':len(raw),'caches':len(caches)}))
if not result['all_passed']:raise SystemExit(2)
