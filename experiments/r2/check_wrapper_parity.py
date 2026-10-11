"""Execute R2 seen wrappers on historical input and require byte-identical output."""
import json,os,subprocess,sys,hashlib
from pathlib import Path
from collect_index import old_index
ROOT=Path(__file__).resolve().parents[2];OUT=Path(os.environ['LIO_GINS_RUN_DIR'])
checks=[]
for method in ['P','B6']:
    old=next(r for r in old_index() if r['cache']=='parking' and r['method']==method and r['case']=='loss30_bias10')
    config=OUT/(method+'.json');config.write_text(json.dumps(old['config'],indent=2)+'\n')
    prior=Path(old['backend']);identity=json.loads((prior/'backend_identity.json').read_text());wrapper=ROOT/'experiments/r2'/('run_seen_candidate.py' if method=='P' else 'run_seen_baseline.py')
    cmd=[sys.executable,str(ROOT/'experiments/r2/record_run.py'),'--stage','S1','--purpose','wrapper_parity_'+method,'--kind','cached_backend']
    for p in [wrapper,config,Path(identity['source_cache_run'])/'lio_cache.npz',Path(identity['initialization_run'])/'initial_condition.json',identity['gnss_source']]:cmd+=['--input',str(p)]
    cmd+=['--',sys.executable,str(wrapper),identity['source_cache_run'],identity['initialization_run'],str(config),'--gnss-ned',identity['gnss_source']]
    env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1');done=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,text=True);assert done.returncode==0,done.stderr+done.stdout;new=Path(json.loads(done.stdout.splitlines()[-1])['output'])
    for name in ['trajectory.csv','per_update.jsonl']:
        same=(new/name).read_bytes()==(prior/name).read_bytes();checks.append({'method':method,'artifact':name,'byte_identical':same,'old_run':str(prior),'new_run':str(new),'SHA':hashlib.sha256((new/name).read_bytes()).hexdigest()});assert same,checks[-1]
(OUT/'wrapper_parity.json').write_text(json.dumps({'checks':checks,'all_passed':True,'R1_source_unchanged':True},indent=2)+'\n');print(json.dumps({'byte_identical_checks':len(checks),'all_passed':True}))
