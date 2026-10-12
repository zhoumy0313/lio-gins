"""Single predeclared matrix. All strategies unchanged from R2; no truth access."""
import argparse,concurrent.futures,json,os,subprocess,sys
from pathlib import Path
from gate import verify_access,sha
ROOT=Path(__file__).resolve().parents[3];OUT=Path(os.environ['LIO_GINS_RUN_DIR'])
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--resume-progress');args=parser.parse_args()
 context=json.loads((ROOT/'artifacts/s9/playground00/technical_context.json').read_text());freeze=ROOT/context['freeze_relative_path'];cache=Path(context['cache']);init=Path(context['initialization']);stress=Path(context['stress']);cases=json.loads((stress/'event_manifest.json').read_text())['cases'];methods=json.loads((ROOT/'configs/s9/protocol.json').read_text())['methods']
 verify_access('playground00','s9_prospective_heldout',freeze,ROOT/'configs/s9/P.json')
 opening=ROOT/'artifacts/s9/playground00/FIRST_MATRIX_OPENING.json'
 inherited=[]
 if args.resume_progress:
  first=json.loads(opening.read_text());assert first['freeze_SHA']==sha(freeze)
  previous=Path(args.resume_progress).resolve();assert str(previous.parent)==first['controller_run'],'resume only original controller, not selected successful runs'
  progress=json.loads(previous.read_text());inherited=progress['rows']
  for row in inherited:
   backend=Path(row['backend']);assert json.loads((backend/'manifest.json').read_text())['status']=='PASSED';assert sha(backend/'backend_resolved.json')==sha(ROOT/'configs/s9'/f"{row['method']}.json")
 else:
  with opening.open('x') as f:json.dump({'controller_run':str(OUT),'freeze_SHA':sha(freeze),'remote_receipt_SHA':sha(ROOT/'docs/research_s9/playground00/FREEZE_PUSH_RECEIPT.json'),'pairs':len(methods)*len(cases),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'no_parameter_revision':True},f,indent=2)
 present={(r['method'],r['case']) for r in inherited};jobs=[(m,c['id']) for m in methods for c in cases if (m,c['id']) not in present];(OUT/'plan.json').write_text(json.dumps({'jobs':jobs,'workers':4,'truth_access':False,'first_matrix':not bool(args.resume_progress),'resume_source':args.resume_progress,'inherited':len(inherited),'resume_rule':'finish every missing pair under identical freeze, never select by performance'},indent=2)+'\n');rows=list(inherited);failures=[]
 def task(method,case):
  cp=ROOT/'configs/s9'/f'{method}.json';conf=json.loads(cp.read_text());wrapper=ROOT/'experiments/s9/playground00'/('run_baseline.py' if conf['method'].startswith('B') else 'run_candidate.py');data=stress/(case+'.csv')
  inputs=[wrapper,ROOT/'experiments/s9/playground00/gate.py',cp,cache/'lio_cache.npz',cache/'cache_identity.json',init/'initial_condition.json',data,data.with_suffix('.identity.json'),*list((ROOT/'src').rglob('*.py'))]
  argv=[sys.executable,str(ROOT/'experiments/s9/playground00/record_run.py'),'--stage','C','--purpose',method+'_'+case,'--kind','cached_backend','--timeout','180']
  for p in inputs:argv+=['--input',str(p)]
  argv+=['--',sys.executable,str(wrapper),str(cache),str(init),str(cp),'--gnss-ned',str(data),'--freeze',str(freeze)];env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1');done=subprocess.run(argv,cwd=ROOT,env=env,capture_output=True,text=True)
  if done.returncode:raise RuntimeError({'rc':done.returncode,'stdout':done.stdout,'stderr':done.stderr,'method':method,'case':case})
  receipt=json.loads(done.stdout.splitlines()[-1]);return {'cache':'playground00','method':method,'case':case,'backend':receipt['output'],'evaluation':None,'config':conf,'inherited':False}
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  futures={pool.submit(task,*job):job for job in jobs}
  for f in concurrent.futures.as_completed(futures):
   try:rows.append(f.result())
   except Exception as e:failures.append({'key':futures[f],'error':str(e)})
   (OUT/'progress.json').write_text(json.dumps({'rows':rows,'failures':failures},indent=2)+'\n');print(json.dumps({'finished':len(rows)+len(failures),'of':len(jobs),'failures':len(failures)}),flush=True)
 rows.sort(key=lambda r:(r['method'],r['case']));(OUT/'complete_index.json').write_text(json.dumps(rows,indent=2)+'\n');(OUT/'failures.json').write_text(json.dumps(failures,indent=2)+'\n');assert not failures and len(rows)==152
if __name__=='__main__':main()
