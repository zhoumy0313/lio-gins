"""Evidence, scientific-freeze ordering, sealed outputs and legacy preservation."""
import datetime,hashlib,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=Path(os.environ['LIO_GINS_RUN_DIR'])
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(2**20),b''):h.update(b)
    return h.hexdigest()
state=json.loads((ROOT/'docs/research_s9/STATE.json').read_text())
registry=json.loads((ROOT/'artifacts/s9/COLLECTIVE_FREEZE.json').read_text())
protected=subprocess.check_output(['git','ls-tree','-r','--name-only',state['base_S8_commit']],cwd=ROOT,text=True).splitlines()
protected=[p for p in protected if p not in ['AGENTS.md','.gitignore','docs/USER_ACTION_REQUIRED.md']]
assert not subprocess.check_output(['git','diff',state['base_S8_commit'],'--',*protected],cwd=ROOT)
legacy=[]
for p in ['artifacts/s8/DELIVERY_MANIFEST.json','artifacts/r2/S7/DELIVERY_MANIFEST.json']:
    m=json.loads((ROOT/p).read_text());bad=[f for f,d in m['file_SHA'].items() if sha(ROOT/f)!=d];assert not bad
    legacy.append({'manifest':p,'files':len(m['file_SHA']),'mismatches':bad})
sys.path.insert(0,str(ROOT/'experiments/s9'/state['included_routes'][0]));from gate import verify_freeze
freeze_sources=0;freeze_inputs=0;matrix_pairs=0;events=0;checks=[];readbacks=[]
for item in registry['included_routes']:
    route=item['sequence'];receipt=json.loads((ROOT/item['receipt_relative_path']).read_text());f=verify_freeze(ROOT/item['freeze_relative_path'],ROOT/item['receipt_relative_path']);readbacks.append(datetime.datetime.fromisoformat(receipt['UTC']))
    freeze_sources+=len(f['source_config_SHA']);freeze_inputs+=len(f['input_SHA'])
    assert all(sha(p)==d for p,d in f['input_SHA'].items())
    for raw in f['raw_inputs']:
        st=Path(raw['path']).stat();assert (st.st_size,st.st_mtime_ns,st.st_ctime_ns)==(raw['size_bytes'],raw['mtime_ns'],raw['ctime_ns'])
    matrix=Path(state['routes'][route]['matrix_run']);rows=json.loads((matrix/'complete_index.json').read_text());assert len(rows)==152 and len({(r['method'],r['case']) for r in rows})==152
    analysis=Path(state['routes'][route]['analysis_run']);ev=json.loads((analysis/'event_results.json').read_text());assert len(ev)==152 and sum(len(r['events']) for r in ev)==399
    check=json.loads((Path(state['routes'][route]['independent_check_run'])/'independent_check.json').read_text());assert check['passed'] and check['pairs']==152 and check['accepted_clocks_checked']==399
    checks.append({'route':route,**check});matrix_pairs+=len(rows);events+=sum(len(r['events']) for r in ev)
seals=0;entries=0;failures=[];running=[];precision_times=[]
for p in sorted((ROOT/'outputs_s9').glob('*/manifest.json')):
    if p.parent==OUT:continue
    m=json.loads(p.read_text())
    if m['status']=='RUNNING':running.append(str(p));continue
    if m['status']=='FAILED':failures.append({'run':str(p.parent),'purpose':m['purpose'],'exit_code':m['exit_code']})
    sums=p.parent/'SHA256SUMS';assert sums.exists();seals+=1
    for line in sums.read_text().splitlines():
        digest,name=line.split('  ',1);assert sha(p.parent/name)==digest,str(p.parent/name);entries+=1
    if m['stage']=='C':precision_times.append(datetime.datetime.fromisoformat(m['started_UTC']))
assert not running and min(precision_times)>max(readbacks),'every included route must have remote verification before any S9 precision'
pdf=ROOT/'paper/submission_candidate/s9/main.pdf';paper=json.loads((ROOT/'artifacts/s9/manuscript_audit.json').read_text());assert paper['pages']<=6 and sha(pdf)==paper['PDF_SHA'] and paper['NOT_SUBMISSION_READY_retained']
result={'matrix_pairs':matrix_pairs,'events':events,'windows':events*5,'frozen_source_config_checks':freeze_sources,'frozen_input_checks':freeze_inputs,'raw_immutable_stat_verified':True,'official_bag_full_SHA_verified_before_freeze':True,'legacy_delivery_checks':legacy,'all_protected_R1_R2_S8_git_files_unchanged':True,'sealed_runs_checked':seals,'sealed_entries_checked':entries,'mismatches':[],'retained_failed_runs':failures,'latest_remote_freeze_readback_UTC':max(readbacks).isoformat(),'earliest_C_started_UTC':min(precision_times).isoformat(),'collective_freeze_verified_before_every_precision_run':True,'independent_checks':checks,'paper':paper,'formal_submission_performed':False,'human_author_review_complete':False,'backup':'Git lightweight source/freezes/results/plots/paper; full raw/runtime/cache remain local only'}
(OUT/'delivery_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
