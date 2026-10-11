"""Finite predeclared clock controls; no frontend replay or parameter selection."""
import concurrent.futures,json,os,subprocess,sys
from pathlib import Path
from collect_index import old_index
ROOT=Path(__file__).resolve().parents[2];OUT=Path(os.environ['LIO_GINS_RUN_DIR'])
ROUTES={
 'primary':('20261011T141044340351Z_P2_9dd3f300','20261011T124056742603Z_P2_e310122b','20261011T132959853728Z_P3_7079c4e4'),
 'sensitivity':('20261011T134125698776Z_P2_0de7714e','20261011T124056742603Z_P2_e310122b','20261011T132959853728Z_P3_7079c4e4'),
 'parking':('20261011T160558488156Z_P5_3b1dbc60','20261011T154446605564Z_P5_ce2e5936','20261011T160559020499Z_P5_7a20a16d')}
def recorded(purpose,argv,inputs):
    cmd=[sys.executable,str(ROOT/'experiments/r2/record_run.py'),'--stage','S1','--purpose',purpose,'--kind','cached_backend']
    for path in inputs:cmd+=['--input',str(path)]
    cmd+=['--',*map(str,argv)];env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    done=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,text=True)
    if done.returncode:raise RuntimeError({'argv':cmd,'rc':done.returncode,'stdout':done.stdout,'stderr':done.stderr})
    return json.loads(done.stdout.splitlines()[-1])
def task(cachelabel,method,case):
    cache,init,stress=[ROOT/'outputs'/name for name in ROUTES[cachelabel]]
    config=json.loads((ROOT/'configs/final_evaluation_methods.json').read_text())['P_time_only' if method.startswith('Clock') else method]
    if method.startswith('Clock'):config['motion']['good_duration_s']=int(method[5:])
    configpath=OUT/'configs'/f'{method}.json';data=stress/(case+'.csv')
    wrapper=ROOT/'experiments/r2'/('run_seen_candidate.py' if method!='B2' else 'run_seen_baseline.py')
    inputs=[wrapper,configpath,cache/'lio_cache.npz',cache/'cache_identity.json',init/'initial_condition.json',data,data.with_suffix('.identity.json')]
    inputs+=list((ROOT/'src').rglob('*.py'))
    receipt=recorded('_'.join([cachelabel,method,case]),[sys.executable,wrapper,cache,init,configpath,'--gnss-ned',data],inputs)
    row={'cache':cachelabel,'method':method,'case':case,'backend':receipt['output'],'evaluation':None,'config':config,'inherited':False}
    return row
def main():
    inherited=old_index();present={(r['cache'],r['method'],r['case']) for r in inherited};jobs=[]
    (OUT/'configs').mkdir()
    configs=json.loads((ROOT/'configs/final_evaluation_methods.json').read_text())
    for name in ['B2']+['Clock'+str(t) for t in [2,5,10,15,30,60,90]]:
        conf=configs['B2' if name=='B2' else 'P_time_only'].copy()
        if name!='B2':conf['motion']={**conf['motion'],'good_duration_s':int(name[5:])}
        (OUT/'configs'/(name+'.json')).write_text(json.dumps(conf,indent=2)+'\n')
    for cache in ROUTES:
        for method in ['B2']+['Clock'+str(t) for t in [2,5,10,15,30,60,90]]:
            stress=ROOT/'outputs'/ROUTES[cache][2];manifest=json.loads((stress/'event_manifest.json').read_text())
            for case in manifest['cases']:
                key=(cache,method,case['id'])
                if key not in present:jobs.append(key)
    (OUT/'plan.json').write_text(json.dumps({'jobs':jobs,'max_workers':4,'no_parameter_tuning':True,'new_route_opened':False},indent=2)+'\n')
    rows=[];failed=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures={pool.submit(task,*key):key for key in jobs}
        for future in concurrent.futures.as_completed(futures):
            key=futures[future]
            try:row=future.result();rows.append(row);print(json.dumps({'completed':key}),flush=True)
            except Exception as e:failed.append({'key':key,'error':str(e)});print(json.dumps({'failed':key,'error':str(e)}),flush=True)
            (OUT/'progress.json').write_text(json.dumps({'completed':rows,'failed':failed},indent=2)+'\n')
    index=inherited+rows;(OUT/'complete_index.json').write_text(json.dumps(index,indent=2)+'\n')
    print(json.dumps({'supplemented':len(rows),'inherited':len(inherited),'failed':len(failed)}));return int(bool(failed))
if __name__=='__main__':raise SystemExit(main())
