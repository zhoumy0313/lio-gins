"""No new-route precision: bounded technical audits and reused frontend."""
import concurrent.futures,datetime,json,os,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];ROUTES=['street00','playground00','building02']
def record(route,purpose,script,args=(),kind='engineering',timeout=300):
 folder=ROOT/'experiments/s9'/route;argv=[sys.executable,str(folder/'record_run.py'),'--stage','A','--purpose',route+'_'+purpose,'--kind',kind,'--input',str(folder/script),'--timeout',str(timeout),'--',sys.executable,str(folder/script),*map(str,args)]
 done=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True);print(json.dumps({'route':route,'purpose':purpose,'exit':done.returncode,'receipt':done.stdout.strip(),'stderr':done.stderr[-1000:]}),flush=True)
 if done.returncode:raise RuntimeError({'route':route,'purpose':purpose,'exit':done.returncode,'receipt':done.stdout.strip()})
 return Path(json.loads(done.stdout.splitlines()[-1])['output'])
def task(route):
 art=ROOT/'artifacts/s9'/route;steps={}
 def save(p,filename):shutil.copy2(p/filename,art/filename)
 try:
  audit=record(route,'five_originals_identity_time_interfaces','audit_data.py',timeout=600);steps['data_audit']=str(audit);save(audit,'data_manifest.json')
  extra=record(route,'bounded_F9P_and_trajectory_schema','extra_interfaces.py');steps['extra_interfaces']=str(extra);save(extra,'extra_interfaces.json')
  info=record(route,'isolated_rosbag_info','rosbag_info.py',[ROOT/'data/i2nav-dataset'/route/(route+'.bag')]);steps['rosbag_info']=str(info)
  init=record(route,'unique_first_state_initialization','initial_condition.py');steps['initialization']=str(init)
  stress=record(route,'unchanged_seven_GNSS_faults_plus_natural','prepare_stress.py',[init]);steps['stress']=str(stress)
  (art/'engineering_progress.json').write_text(json.dumps(steps,indent=2)+'\n')
  frontend=record(route,'single1x_reused_FASTLIO_no_accuracy','run_frontend.py',[ROOT/'data/i2nav-dataset'/route/(route+'.bag')],kind='real_frontend',timeout=4000);steps['frontend']=str(frontend)
  cache=record(route,'no_reference_complete_LIO_cache','build_cache.py',[frontend]);steps['cache']=str(cache);save(cache,'cache_identity.json')
  (art/'technical_context.json').write_text(json.dumps({'goal_id':'LIO-GINS-S9-MULTISCENARIO',**{k:steps[k] for k in ['frontend','cache','initialization','stress']},'freeze_relative_path':'freezes/s9/'+route+'_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'/scientific_freeze.json','role':'s9_prospective_heldout','cache_selection':'one fixed full technical replay; no precision-based selection','performance_opened_at_context_creation':False},indent=2)+'\n')
  result={'route':route,'status':'TECHNICALLY_READY','steps':steps,'precision_opened':False}
 except Exception as e:result={'route':route,'status':'TECHNICAL_BLOCK','steps':steps,'error':str(e),'precision_opened':False}
 (art/'engineering_result.json').write_text(json.dumps(result,indent=2)+'\n');return result
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 futures={pool.submit(task,r):r for r in ROUTES}
 results=[]
 for f in concurrent.futures.as_completed(futures):results.append(f.result());print(json.dumps(results[-1]),flush=True)
(ROOT/'artifacts/s9/engineering_results.json').write_text(json.dumps(results,indent=2)+'\n')
