"""Ordered collective-freeze then complete first precision matrices; no tuning."""
import datetime,gzip,json,os,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];ROUTES=['street00','playground00','building02']
def stage(route,phase,purpose,script,args=(),timeout=300,kind='engineering',allow_failure=False):
 folder=ROOT/'experiments/s9'/route;argv=[sys.executable,str(folder/'record_run.py'),'--stage',phase,'--purpose',route+'_'+purpose,'--kind',kind,'--input',str(folder/script),'--timeout',str(timeout),'--',sys.executable,str(folder/script),*map(str,args)];p=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True);print(json.dumps({'route':route,'stage':phase,'purpose':purpose,'exit_code':p.returncode,'receipt':p.stdout.strip(),'stderr':p.stderr[-500:]}),flush=True);assert allow_failure or p.returncode==0,p.stdout;return Path(json.loads(p.stdout.splitlines()[-1])['output'])
def common_record(route,phase,purpose,script,args=(),timeout=300):
 folder=ROOT/'experiments/s9'/route;p=subprocess.run([sys.executable,str(folder/'record_run.py'),'--stage',phase,'--purpose',purpose,'--input',str(ROOT/'experiments/s9'/script),'--timeout',str(timeout),'--',sys.executable,str(ROOT/'experiments/s9'/script),*map(str,args)],cwd=ROOT,capture_output=True,text=True);print(p.stdout,flush=True);assert p.returncode==0;return Path(json.loads(p.stdout.splitlines()[-1])['output'])
def state():return json.loads((ROOT/'docs/research_s9/STATE.json').read_text())
def save(s):s['updated_UTC']=datetime.datetime.now(datetime.timezone.utc).isoformat();(ROOT/'docs/research_s9/STATE.json').write_text(json.dumps(s,indent=2)+'\n')
def checkpoint(phase,next_phase):subprocess.run([sys.executable,str(ROOT/'experiments/s9/checkpoint.py'),phase,next_phase],cwd=ROOT,check=True)
def main():
 results=json.loads((ROOT/'artifacts/s9/engineering_results.json').read_text());by={r['route']:r for r in results};assert all(by[r]['status']=='TECHNICALLY_READY' for r in ROUTES[:2]);included=[r for r in ROUTES if by[r]['status']=='TECHNICALLY_READY'];excluded=[by[r] for r in ROUTES if r not in included];s=state()
 for route in included:
  common_record(route,'A',route+'_final_time_only_common_support','finalize_engineering.py',[route]);s['routes'][route].update(status='TECHNICALLY_READY',engineering_result=by[route]);save(s)
 for route in included:
  t=stage(route,'B','final_role_core_and_metric_parity','test_interfaces.py',timeout=120);shutil.copy2(t/'stderr.log',ROOT/'artifacts/s9'/route/'role_gate_test_report.txt')
 checkpoint('A','B');entries=[]
 for route in included:
  stage(route,'B','full_scientific_freeze','freeze_science.py',timeout=300);c=json.loads((ROOT/'artifacts/s9'/route/'technical_context.json').read_text());import hashlib
  entries.append({'sequence':route,'freeze_relative_path':c['freeze_relative_path'],'freeze_SHA':hashlib.sha256((ROOT/c['freeze_relative_path']).read_bytes()).hexdigest(),'receipt_relative_path':'docs/research_s9/'+route+'/FREEZE_PUSH_RECEIPT.json'})
 collective={'goal_id':'LIO-GINS-S9-MULTISCENARIO','type':'COLLECTIVE_PROSPECTIVE_ROUTE_REGISTRATION','UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'fixed_order':ROUTES,'included_routes':entries,'technical_exclusions':excluded,'any_precision_opened':False,'source_freeze_required_all_routes_before_first_precision':True,'no_parameter_or_metric_changes':True}
 (ROOT/'artifacts/s9/COLLECTIVE_FREEZE.json').write_text(json.dumps(collective,indent=2)+'\n');s=state();s['included_routes']=included;s['technical_exclusions']=excluded;save(s);checkpoint('B','C')
 for route in included:stage(route,'B','exact_remote_collective_freeze_readback','verify_remote_freeze.py',timeout=120)
 s=state();s['collective_freeze_push_verified']=True;save(s)
 for route in included:
  matrix=stage(route,'C','single_complete19x8_independent_matrix','run_matrix.py',timeout=900);s=state();s['routes'][route].update(precision_opened=True,matrix_run=str(matrix));save(s)
  analysis=stage(route,'C','all_grids_events_metrics','reanalyse.py',[matrix/'complete_index.json'],timeout=240);s=state();s['routes'][route]['analysis_run']=str(analysis);save(s)
  check=stage(route,'C','independent_RMSE_admission_availability_exposure','independent_check.py',[analysis],timeout=240)
  judgment=stage(route,'C','all_controls_categories_fixed_gates','judge_results.py',[analysis]);cancel=stage(route,'C','offline_receiver_injection_cancellation','injection_cancellation.py')
  art=ROOT/'artifacts/s9'/route/'C';art.mkdir()
  for name in ['summary_table.json','summary_table.csv','event_table.csv','analysis_audit.json']:shutil.copy2(analysis/name,art/name)
  for name in ['event_results.json']:
   with (analysis/name).open('rb') as src,gzip.open(art/(name+'.gz'),'wb') as dst:shutil.copyfileobj(src,dst)
  with (matrix/'complete_index.json').open('rb') as src,gzip.open(art/'complete_index.json.gz','wb') as dst:shutil.copyfileobj(src,dst)
  for name in ['scientific_judgment.json','category_table.json','category_table.csv']:shutil.copy2(judgment/name,art/name)
  shutil.copy2(check/'independent_check.json',art/'independent_check.json');shutil.copy2(cancel/'injection_cancellation.json',art/'injection_cancellation.json')
  context=json.loads((ROOT/'artifacts/s9'/route/'technical_context.json').read_text())
  native=stage(route,'C','independent_fixed_KF_GINS_natural_transfer','run_native_kf.py',[context['initialization'],'--noise-scale','2','--freeze',ROOT/context['freeze_relative_path']],timeout=180,allow_failure=True)
  native_evaluation=None
  if json.loads((native/'manifest.json').read_text())['status']=='PASSED':
   native_evaluation=stage(route,'C','offline_fixed_KF_GINS_transfer_evaluation','evaluate_native_kf.py',[native,context['initialization'],'--freeze',ROOT/context['freeze_relative_path']],timeout=240,allow_failure=True)
   if (native_evaluation/'metrics.json').exists():shutil.copy2(native_evaluation/'metrics.json',art/'native_KF_metrics.json')
  shutil.copy2(native/'manifest.json',art/'native_KF_run_manifest.json')
  s=state();s['routes'][route].update(native_KF_run=str(native),native_KF_evaluation=str(native_evaluation) if native_evaluation else None);save(s)

  s=state();s['routes'][route].update(status='MATRIX_ANALYSIS_VERIFIED',independent_check_run=str(check),judgment_run=str(judgment),cancellation_run=str(cancel));save(s)
 aggregate=common_record(included[0],'C','all_registered_route_comparisons','aggregate.py');s=state();s['aggregate_run']=str(aggregate);save(s)
 art=ROOT/'artifacts/s9/C';art.mkdir()
 for p in aggregate.iterdir():
  if p.name in ['cross_route_judgment.json','summary_table.json','summary_table.csv','all_event_results.json.gz']:shutil.copy2(p,art/p.name)
 checkpoint('C','D');print('All frozen route experiments complete; author-review paper and final audit remain.',flush=True)
if __name__=='__main__':main()
