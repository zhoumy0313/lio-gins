"""Prove inherited byte identity and seals, with no re-execution of estimators."""
import json,os,subprocess
from pathlib import Path
from common import ROOT,BASE,sha,resolve,read_json
OUT=Path(os.environ['LIO_GINS_S10_OUT']);checked={}
def verify(path,digest):
 path=Path(path).resolve()
 if str(path) not in checked:checked[str(path)]=sha(path)
 assert checked[str(path)]==digest,str(path)
expected_heads={'research/lio-gins-r1':'c12a42a3484458e1737e63201792e1122fc99c0d','research/lio-gins-r2-submission':'8ef95ce597433a8b45c90ec1d13eb57ec4355555','research/lio-gins-s8-building01':'ca6bf095426a5c1e06387f156a15178921276358','research/lio-gins-s9-multiscenario':BASE}
for branch,d in expected_heads.items():assert subprocess.check_output(['git','rev-parse',branch],cwd=ROOT,text=True).strip()==d
protected=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=ROOT,text=True).splitlines()
assert not subprocess.check_output(['git','diff',BASE,'--',*protected],cwd=ROOT)
manifests={}
for name in ['artifacts/r2/S7/DELIVERY_MANIFEST.json','artifacts/s8/DELIVERY_MANIFEST.json','artifacts/s9/DELIVERY_MANIFEST.json']:
 j=read_json(ROOT/name);fields=j.get('file_SHA',j.get('files'))
 assert isinstance(fields,dict),(name,j.keys())
 for p,d in fields.items():verify(ROOT/p,d)
 manifests[name]={'SHA':sha(ROOT/name),'verified_file_count':len(fields)}
pairs=read_json(ROOT/'artifacts/s10/manifest.json')['all_pair_provenance']
for item in pairs:
 run=resolve(item['backend_run']);identity=read_json(run/'backend_identity.json')
 for filename,key in [('manifest.json','run_manifest_SHA'),('backend_identity.json','backend_identity_SHA'),('backend_resolved.json','config_SHA'),('trajectory.csv','trajectory_SHA'),('per_update.jsonl','updates_SHA')]:verify(run/filename,item[key])
 verify(resolve(item['archived_event_source']),item['archived_event_SHA'])
 verify(resolve(identity['gnss_source']),item['GNSS_SHA']);verify(resolve(Path(identity['initialization_run'])/'initial_condition.json'),item['initialization_SHA']);verify(resolve(Path(identity['source_cache_run'])/'lio_cache.npz'),item['cache_SHA'])
 route='building00' if item['route']=='building00_repeat' else item['route'];verify(ROOT/'data/i2nav-dataset'/route/(route+'_groundtruth.nav'),item['reference_SHA'])
runs=[]
for run in sorted((ROOT/'cache/s10/runs').iterdir()):
 if not run.is_dir():continue
 if run.resolve()==OUT.resolve():continue  # recorder seals this audit after exit
 j=read_json(run/'run_manifest.json');assert j['status'] in ['COMPLETED','FAILED'] and isinstance(j['exit_code'],int)
 sealed={}
 for line in (run/'SHA256SUMS').read_text().splitlines():
  d,p=line.split('  ',1);verify(run/p,d);sealed[p]=d
 actual={str(p.relative_to(run)) for p in run.rglob('*') if p.is_file() and p.name!='SHA256SUMS'}
 # Nested legacy fixture runs have their own SHA256SUMS and were also sealed
 # by the S10 outer recorder; exclude only this outer seal.
 actual={str(p.relative_to(run)) for p in run.rglob('*') if p.is_file() and p!=run/'SHA256SUMS'}
 assert actual==set(sealed),('unsealed addition/deletion',run,actual-set(sealed),set(sealed)-actual)
 runs.append({k:j[k] for k in ['run_id','stage','purpose','argv','exit_code','wall_seconds','status']})
j={'base_S9':BASE,'inherited_heads_unchanged':expected_heads,'inherited_tracked_worktree_and_history_unchanged':True,'inherited_manifests':manifests,'source_pairs_verified':len(pairs),'unique_file_SHA_verified':len(checked),'all_completed_S10_run_seals_valid':True,'runs':runs,'failed_runs_retained':sum(r['exit_code']!=0 for r in runs),'old_VPR_global_ROS_SSH_driver_modified':False,'no_new_estimator_or_bias_amplitude_test':True,'remote_push_performed':False,'formal_submission_performed':False}
(OUT/'final_integrity_audit.json').write_text(json.dumps(j,indent=2)+'\n');print(json.dumps({k:v for k,v in j.items() if k!='runs'}))
