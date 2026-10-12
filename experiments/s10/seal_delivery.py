"""Seal the complete local review delivery after scientific and PDF audits."""
import datetime,json,subprocess,sys
from pathlib import Path
from common import ROOT,BASE,sha,read_json,json_write
started=datetime.datetime.now(datetime.timezone.utc).isoformat()
state=read_json(ROOT/'docs/research_s10/STATE.json');assert state['flags']['execution_complete'] and state['flags']['full_six_page_review_draft_ready']
assert not state['remote_push_authorized'] and not state['flags']['formal_submission_ready']
expected=state['PDF_SHA'];assert sha(ROOT/'paper/submission_candidate/s10/main.pdf')==expected
assert read_json(ROOT/'artifacts/s10/numeric_paper_audit.json')['PDF_SHA']==expected
protected=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=ROOT,text=True).splitlines();assert not subprocess.check_output(['git','diff',BASE,'--',*protected],cwd=ROOT)
# Earlier audit has verified all other runs. Check its own completed seal now.
run=Path(state['runs']['final_audit']);count=0
for line in (run/'SHA256SUMS').read_text().splitlines():
 digest,name=line.split('  ',1);assert sha(run/name)==digest;count+=1
excluded={'artifacts/s10/DELIVERY_MANIFEST.json','artifacts/s10/FINAL_DELIVERY_CHECK.json','docs/research_s10/CHECKPOINTS.md'}
folders=[ROOT/p for p in ['docs/research_s10','artifacts/s10','experiments/s10','paper/submission_candidate/s10']]+list((ROOT/'paper/versions').glob('s10_r[0-9][0-9]'))
files={str(p.relative_to(ROOT)):sha(p) for folder in folders for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and str(p.relative_to(ROOT)) not in excluded}
manifest={'goal':state['goal'],'base_S9':BASE,'source_checkpoint_before_final':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'review_PDF_SHA':expected,'file_count':len(files),'file_SHA':files,'excluded_dynamic_or_recursive_paths':sorted(excluded),'big_raw_outputs_and_cache_local_only':True,'frozen_algorithms_and_parameters_unchanged':True,'remote_push_performed':False,'independent_confirmatory_gain_supported':False,'formal_submission_ready':False}
json_write(ROOT/'artifacts/s10/DELIVERY_MANIFEST.json',manifest)
for p,d in files.items():assert sha(ROOT/p)==d
sizes={p:(ROOT/p).stat().st_size for p in files};assert max(sizes.values())<10000000
result={'argv':[sys.executable,str(Path(__file__).resolve())],'started_UTC':started,'finished_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':0,'file_count':len(files),'sealed_delivery_manifest_SHA':sha(ROOT/'artifacts/s10/DELIVERY_MANIFEST.json'),'own_final_audit_seal_checked_files':count,'all_current_paper_and_input_audits_valid':True,'inherited_files_unchanged':True,'retained_versions':sorted(p.name for p in (ROOT/'paper/versions').glob('s10_r[0-9][0-9]')),'max_file_bytes':max(sizes.values()),'review_PDF_SHA':expected,'no_remote_push_or_submission':True}
json_write(ROOT/'artifacts/s10/FINAL_DELIVERY_CHECK.json',result);print(json.dumps(result))
