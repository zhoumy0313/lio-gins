"""Integrity/order audit of actual S8 evidence and unchanged R1/R2 inheritance."""
import datetime,hashlib,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=Path(os.environ['LIO_GINS_RUN_DIR']);sys.path.insert(0,str(ROOT))
from gate import verify_freeze,sha
def main():
 state=json.loads((ROOT/'docs/research_s8/STATE.json').read_text());context=json.loads((ROOT/'artifacts/s8/technical_context.json').read_text());receipt=json.loads((ROOT/'docs/research_s8/FREEZE_PUSH_RECEIPT.json').read_text());freeze=verify_freeze(ROOT/context['freeze_relative_path'],ROOT/'docs/research_s8/FREEZE_PUSH_RECEIPT.json');bad=[]
 for p,d in freeze['input_SHA'].items():
  if sha(p)!=d:bad.append(p)
 for f in freeze['raw_inputs']:
  st=Path(f['path']).stat();assert (st.st_size,st.st_mtime_ns,st.st_ctime_ns)==(f['size_bytes'],f['mtime_ns'],f['ctime_ns'])
 old=json.loads((ROOT/'artifacts/r2/S7/DELIVERY_MANIFEST.json').read_text());old_bad=[p for p,d in old['file_SHA'].items() if sha(ROOT/p)!=d];assert not old_bad
 protected=subprocess.check_output(['git','ls-tree','-r','--name-only','8ef95ce'],cwd=ROOT,text=True).splitlines();protected=[p for p in protected if p not in ['AGENTS.md','.gitignore','docs/USER_ACTION_REQUIRED.md']];assert not subprocess.check_output(['git','diff','8ef95ce','--',*protected],cwd=ROOT)
 assert subprocess.check_output(['git','rev-parse','research/lio-gins-r1'],cwd=ROOT,text=True).strip()=='c12a42a3484458e1737e63201792e1122fc99c0d'
 assert subprocess.check_output(['git','rev-parse','research/lio-gins-r2-submission'],cwd=ROOT,text=True).strip()=='8ef95ce597433a8b45c90ec1d13eb57ec4355555'
 seals=0;seal_entries=0;sealed_bad=[];failed=[];method_times=[];running=[]
 for p in sorted((ROOT/'outputs_s8').glob('*/manifest.json')):
  m=json.loads(p.read_text())
  if p.parent==OUT:continue
  if m['status']=='RUNNING':running.append(str(p));continue
  if m['status']=='FAILED':failed.append({'run':str(p.parent),'purpose':m['purpose'],'exit_code':m['exit_code']})
  sums=p.parent/'SHA256SUMS';assert sums.exists();seals+=1
  for line in sums.read_text().splitlines():
   digest,name=line.split('  ',1);f=p.parent/name;seal_entries+=1
   if not f.is_file() or sha(f)!=digest:sealed_bad.append(str(f))
  if m['stage']=='C':method_times.append(datetime.datetime.fromisoformat(m['started_UTC']))
 verified_time=datetime.datetime.fromisoformat(receipt['UTC']);assert method_times and min(method_times)>verified_time
 index=json.loads((Path(state['matrix_run'])/'complete_index.json').read_text());assert len(index)==152 and len({(r['method'],r['case']) for r in index})==152
 analysis=Path(state['analysis_run']);results=json.loads((analysis/'event_results.json').read_text());assert len(results)==152 and sum(len(r['events']) for r in results)==399
 independent=json.loads((ROOT/'artifacts/s8/independent_check.json').read_text());assert independent['passed'] and independent['pairs']==152 and independent['accepted_clocks_checked']==399
 pdf=ROOT/'paper/submission_candidate/s8/main.pdf';paper=json.loads((ROOT/'artifacts/s8/manuscript_audit.json').read_text());assert paper['pages']<=6 and sha(pdf)==paper['PDF_SHA'] and paper['NOT_SUBMISSION_READY_retained']
 assert not bad and not sealed_bad and not running
 audit={'frozen_inputs_checked':len(freeze['input_SHA']),'frozen_source_config_checks':len(freeze['source_config_SHA']),'frozen_input_mismatches':bad,'raw_full_SHA_before_freeze':'five originals, official bag match, no raw changes detected since; final audit uses size/mtime/ctime rather than another42GiB read','sealed_runs_checked':seals,'sealed_file_entries_checked':seal_entries,'seal_mismatches':sealed_bad,'retained_failed_runs':failed,'manual_checkpoint_failure_retained':'artifacts/s8/checkpoints/B_ENGINEERING_attempt1_failed.json','R2_delivery_files_checked':len(old['file_SHA']),'R2_delivery_mismatches':old_bad,'all_legacy_tracked_source_evidence_unchanged':True,'R1_R2_local_branch_heads_unchanged':True,'remote_freeze_verified_UTC':receipt['UTC'],'earliest_C_run_UTC':min(method_times).isoformat(),'freeze_verified_before_all_C_runs':True,'matrix_pairs':152,'events':399,'independent_check_passed':True,'review_PDF_pages':paper['pages'],'PDF_SHA':sha(pdf),'human_author_approval':False,'formal_submission_performed':False,'backup':{'Git_lightweight_science_PDF':True,'full_numeric_runtime_cache':False,'raw_originals_offsite':False},'science_flags':state['flags']}
 (OUT/'delivery_audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit))
if __name__=='__main__':main()
