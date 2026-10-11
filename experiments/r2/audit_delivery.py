"""Read-only final archive audit, including actual raw hashes and preserved run seals."""
import argparse,csv,datetime,gzip,hashlib,json,os,re,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=Path(os.environ['LIO_GINS_RUN_DIR'])
BASE='c12a42a3484458e1737e63201792e1122fc99c0d'
parser=argparse.ArgumentParser();parser.add_argument('--reuse-raw-phase');args=parser.parse_args()
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(2**20),b''):h.update(chunk)
    return h.hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
result={'R1_base_SHA':BASE,'audit_source_commit':git('rev-parse','HEAD'),'failures':[]}
assert git('rev-parse','research/lio-gins-r1')==BASE
basefiles=set(git('ls-tree','-r','--name-only',BASE).splitlines());changes=git('diff','--name-only',BASE).splitlines()
allowed={'.gitignore','AGENTS.md','docs/USER_ACTION_REQUIRED.md','docs/GOAL_LIO_GINS_R2_SUBMISSION.md'}
unexpected=[p for p in changes if p in basefiles and p not in allowed]
result['R1_tracked_files']=len(basefiles);result['R1_original_tracked_changes_except_authorized']=unexpected
result['authorized_root_changes']=[p for p in changes if p in allowed];assert not unexpected
inherit=json.loads((ROOT/'artifacts/r2/S0/inheritance_audit.json').read_text())
result['inherited_file_checks']={p:sha(ROOT/p)==expected for p,expected in inherit['inherited_file_SHA'].items()};assert all(result['inherited_file_checks'].values())
if args.reuse_raw_phase:
    previous=Path(args.reuse_raw_phase).resolve();phase=previous/'raw_cache_recheck.json'
    seals={line.split('  ',1)[1]:line.split('  ',1)[0] for line in (previous/'SHA256SUMS').read_text().splitlines()}
    assert sha(phase)==seals['raw_cache_recheck.json']
    started=datetime.datetime.fromisoformat(json.loads((previous/'manifest.json').read_text())['started_UTC']).timestamp()
    saved=json.loads(phase.read_text());assert len(saved['raw_files'])==len(inherit['raw_files']) and len(saved['cache_checks'])==3
    result.update(saved);expected={str(Path(r['path']).relative_to(ROOT)):r['expected_SHA'] for r in inherit['raw_files']}
    expected.update({str((Path(r['run'])/'lio_cache.npz').relative_to(ROOT)):r['expected_SHA'] for r in inherit['caches']})
    for row in result['raw_files']+result['cache_checks']:
        p=ROOT/row['path'];s=p.stat();assert row['SHA']==expected[row['path']];assert s.st_ctime<=started and s.st_mtime<=started,'input changed after retained raw hash phase'
        if 'bytes' in row:assert row['bytes']==s.st_size
    result['raw_hash_evidence_reused_from']=str(previous.relative_to(ROOT));result['reuse_reason']='successful sealed raw/cache phase; all current ctime/mtime predate its start, no later writes; later legacy-link audit failure remains retained'
else:
    result['raw_files']=[]
    for old in inherit['raw_files']:
        p=Path(old['path']);actual=sha(p);row={'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'SHA':actual,'matches_S0_R1_SHA':actual==old['actual_SHA']==old['expected_SHA']};result['raw_files'].append(row);print('raw_rehashed '+p.name,flush=True);assert row['matches_S0_R1_SHA']
    result['cache_checks']=[]
    for old in inherit['caches']:
        p=Path(old['run'])/'lio_cache.npz';actual=sha(p);result['cache_checks'].append({'path':str(p.relative_to(ROOT)),'SHA':actual,'passed':actual==old['actual_SHA']==old['expected_SHA']});assert result['cache_checks'][-1]['passed']
(OUT/'raw_cache_recheck.json').write_text(json.dumps({'raw_files':result['raw_files'],'cache_checks':result['cache_checks']},indent=2)+'\n')
seal_counts={};seal_checks=[]
for family in ['outputs','outputs_r2']:
    runs=files=links=0;fail=[];excluded=[];modes={}
    for folder in sorted((ROOT/family).iterdir()):
        if not folder.is_dir() or folder==OUT:continue
        sums=folder/'SHA256SUMS'
        if not sums.exists():continue
        runs+=1
        meta=json.loads((folder/'manifest.json').read_text());mode=meta.get('checksum_mode','legacy_regular_bytes_unmarked');modes[mode]=modes.get(mode,0)+1
        for line in sums.read_text().splitlines():
            if not line:continue
            expected,name=line.split('  ',1);p=folder/name
            assert not Path(name).is_absolute() and '..' not in Path(name).parts,'literal seal path escape'
            if mode=='regular_file_bytes_or_symlink_target_text_v1' and p.is_symlink():
                passed=hashlib.sha256(os.readlink(p).encode()).hexdigest()==expected;files+=1;links+=1
                if not passed:fail.append(str(p.relative_to(ROOT)))
                continue
            if not p.resolve().is_relative_to(folder.resolve()):
                # Legacy rootfs records contain absolute container links. Do not
                # follow them into host /usr or pretend to validate their target.
                if name.startswith(('bundle/rootfs/','rootfs/','ros/log/')):
                    excluded.append({'path':str(p.relative_to(ROOT)),'reason':'legacy absolute container/runtime-log link; no host target read'});continue
                assert p.resolve().is_relative_to(ROOT),'unexpected out-of-project scientific seal target'
            passed=p.is_file() and sha(p)==expected;files+=1
            if not passed:fail.append(str(p.relative_to(ROOT)))
        if runs%25==0:print(f'seals_checked {family} {runs}',flush=True)
    seal_counts[family]={'sealed_runs':runs,'hashed_files_or_declared_link_texts':files,'declared_symlink_texts_checked':links,'checksum_modes':modes,'mismatches':fail,'excluded_absolute_container_links':excluded}
    result['failures']+=fail
result['sealed_archive_checks']=seal_counts
(OUT/'run_seals_audit.json').write_text(json.dumps(seal_counts,indent=2)+'\n')
results=json.loads(gzip.decompress((ROOT/'artifacts/r2/S3/event_results.json.gz').read_bytes()));inputs={}
for row in results:
    for p,h in row['provenance']['input_SHA'].items():
        assert p not in inputs or inputs[p]==h;inputs[p]=h
bad=[p for p,h in inputs.items() if sha(ROOT/p)!=h];result['numeric_provenance_unique_inputs']=len(inputs);result['numeric_provenance_mismatches']=bad;result['failures']+=bad
register=list(csv.DictReader((ROOT/'docs/research_r2/RUN_REGISTER.csv').open()));ids=[r['run_id'] for r in register];assert len(ids)==len(set(ids))
expected={p.name for p in (ROOT/'outputs_r2').iterdir() if p.is_dir() and p!=OUT};actual=set(ids)-{OUT.name};assert actual==expected
for r in register:
    if r['run_id']==OUT.name:continue
    m=json.loads((Path(r['output'])/'manifest.json').read_text());assert int(r['exit_code'])==m['exit_code'];assert m['status']!='RUNNING'
result['run_register_completed_entries']=len(expected);result['failed_completed_runs']=[r['run_id'] for r in register if r['run_id']!=OUT.name and int(r['exit_code'])!=0]
v=ROOT/'paper/versions/r2_r03';build=json.loads((v/'build_audit.json').read_text());result['paper_source_checks']={p:sha(v/p)==h for p,h in build['sources'].items()};assert all(result['paper_source_checks'].values())
result['PDF_SHA']=sha(v/'main.pdf');assert result['PDF_SHA']==build['PDF_SHA256']==json.loads((ROOT/'artifacts/r2/S6/manuscript_audit.json').read_text())['PDF_SHA'];assert build['pages']==6
candidate=ROOT/'paper/submission_candidate/r2';result['review_copy_matches']={str(p.relative_to(v)):sha(p)==sha(candidate/p.relative_to(v)) for p in v.rglob('*') if p.is_file()};assert all(result['review_copy_matches'].values())
freeze=ROOT/'freezes/r2/analysis_20261011T182648484931Z/analysis_freeze.json';result['analysis_freeze_SHA']=sha(freeze);assert result['analysis_freeze_SHA']==freeze.with_suffix('.sha256').read_text().split()[0]
assert json.loads(freeze.read_text())['new_heldout_opening_authorized'] is False
result['free_disk_GiB']=shutil.disk_usage(ROOT).free/2**30;assert result['free_disk_GiB']>=80
tracked=git('ls-files').splitlines();pattern=re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|AKIA[A-Z0-9]{16}')
secret=[];large=[]
for p in tracked:
    f=ROOT/p
    if f.stat().st_size>100*2**20:large.append(p)
    if pattern.search(f.read_bytes()):secret.append(p)
result['tracked_push_scan']={'files':len(tracked),'secret_pattern_matches':secret,'files_above100MiB':large};assert not secret and not large
result['new_heldout_performance_opened']=False;result['backup']={'remote_source_lightweight_partial':True,'full_outputs_offsite_verified':False,'raw_data_offsite_verified':False,'SHA_is_not_backup':True}
result['passed']=not result['failures'];(OUT/'delivery_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':result['passed'],'seals':seal_counts,'raw_files':len(result['raw_files']),'numeric_inputs':len(inputs),'free_disk_GiB':result['free_disk_GiB']}));assert result['passed']
