"""Complete the predeclared three R1 NIS thresholds on every seen pair."""
import concurrent.futures,json,os,sys
from pathlib import Path
from complete_clocks import ROOT,ROUTES,recorded
OUT=Path(os.environ['LIO_GINS_RUN_DIR'])
def task(cachelabel,name,case):
    cache,init,stress=[ROOT/'outputs'/v for v in ROUTES[cachelabel]];cp=OUT/'configs'/(name+'.json');wrapper=ROOT/'experiments/r2/run_seen_baseline.py';data=stress/(case+'.csv')
    inputs=[wrapper,cp,cache/'lio_cache.npz',cache/'cache_identity.json',init/'initial_condition.json',data,data.with_suffix('.identity.json'),*list((ROOT/'src').rglob('*.py'))]
    r=recorded('existing_NIS_'+cachelabel+'_'+name+'_'+case,[sys.executable,wrapper,cache,init,cp,'--gnss-ned',data],inputs)
    return {'cache':cachelabel,'method':name,'case':case,'backend':r['output'],'evaluation':None,'config':json.loads(cp.read_text()),'inherited':False}
def main():
    (OUT/'configs').mkdir();jobs=[];names=[]
    source=ROOT/'outputs/20261011T141054205503Z_P3_e03a0b15/configs'
    for i in range(3):
        old=source/('B4_C'+str(i)+'.json');name='NIS'+str(i);names.append(name);(OUT/'configs'/(name+'.json')).write_bytes(old.read_bytes())
    for cache in ROUTES:
        manifest=json.loads((ROOT/'outputs'/ROUTES[cache][2]/'event_manifest.json').read_text())
        for name in names:
            for c in manifest['cases']:jobs.append((cache,name,c['id']))
    (OUT/'plan.json').write_text(json.dumps({'fixed_jobs':jobs,'protocol':'configs/r2/protocol_v1.yaml','threshold_selection_from_parking':False,'new_candidate':False},indent=2)+'\n');rows=[];failures=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures={pool.submit(task,*key):key for key in jobs}
        for future in concurrent.futures.as_completed(futures):
            try:rows.append(future.result())
            except Exception as e:failures.append({'key':futures[future],'error':str(e)})
            (OUT/'progress.json').write_text(json.dumps({'rows':rows,'failures':failures},indent=2)+'\n')
    prior=json.loads(Path(sys.argv[1]).read_text());(OUT/'complete_index.json').write_text(json.dumps(prior+rows,indent=2)+'\n');print(json.dumps({'pairs':len(rows),'failures':failures}));return int(bool(failures))
if __name__=='__main__':raise SystemExit(main())
