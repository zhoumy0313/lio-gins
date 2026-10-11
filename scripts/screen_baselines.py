#!/usr/bin/env python3
"""Finite, serial, fully recorded development controls; never accesses heldout."""
import argparse, csv, hashlib, json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = str(ROOT / '.venv/bin/python')

def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('cache_run'); parser.add_argument('initialization_run')
    parser.add_argument('stress_run')
    a = parser.parse_args()
    out = Path(os.environ['LIO_GINS_RUN_DIR'])
    cache, initial, stress = [Path(v).resolve() for v in [a.cache_run,a.initialization_run,a.stress_run]]
    events = json.loads((stress/'event_manifest.json').read_text())
    protocol = json.loads((ROOT/'configs/development_experiment_protocol.json').read_text())
    screen = json.loads((ROOT/'configs/baseline_screen_protocol.json').read_text())
    if events['role'] != 'development' or events['sequence'] != 'building00':
        raise ValueError('heldout screen forbidden')
    if events['protocol_sha256'] != digest(ROOT/'configs/development_experiment_protocol.json'):
        raise ValueError('stress protocol identity changed')
    cases = {c['id']: c for c in events['cases']}
    config_dir = out/'configs'; config_dir.mkdir()
    records = {}; history = []
    base = {'method':'B3','max_LIO_span_s':.15,'max_LIO_availability_delay_s':screen['LIO_availability_deadline_s'],'q_axis_scale':protocol['q_axis_scale'],
            'nis_limit':16.266236,'huber_limit':2.5,
            'recovery':{'wait_s':2,'recovery_s':5,'protection':15,'onset_nis':screen['B6_onset_nis'],'gap_s':screen['B6_gap_s']}}
    backend_sources = [ROOT/p for p in ['scripts/run_outer_baseline.py','src/adapters/geodesy.py',
        'src/adapters/sensor_text.py','src/adapters/causal_lio.py','src/fusion/position_kf.py','src/fusion/fixed_recovery.py']]
    eval_sources = [ROOT/p for p in ['scripts/evaluate_outer.py','src/evaluation/reference.py']]
    (out/'experiment_identity.json').write_text(json.dumps({'cache':str(cache),'initialization':str(initial),
        'stress':str(stress),'protocol_sha256':digest(ROOT/'configs/development_experiment_protocol.json'),
        'screen_sha256':digest(ROOT/'configs/baseline_screen_protocol.json'),
        'source_sha256':{str(p):digest(p) for p in backend_sources+eval_sources},
        'candidate_budget_consumed':0,'heldout_opened':False},indent=2)+'\n')

    def recorded(purpose, kind, sources, argv):
        command = [PY,str(ROOT/'scripts/record_run.py'),'--phase','P3','--purpose',purpose,
                   '--kind',kind,'--timeout','180']
        for source in sources: command += ['--input',str(source)]
        command += ['--']+argv
        result = subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
        with (out/'driver_commands.jsonl').open('a') as f:
            f.write(json.dumps({'argv':command,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr})+'\n')
        lines=result.stdout.splitlines()
        if not lines: raise RuntimeError('recorder produced no receipt: '+result.stderr)
        return json.loads(lines[-1])

    def run(conf, name, case_id):
        key=name+'__'+case_id
        if key in records:return records[key]
        path=config_dir/(name+'.json')
        if not path.exists():path.write_text(json.dumps(conf,indent=2)+'\n')
        elif json.loads(path.read_text()) != conf:raise ValueError('config reuse collision')
        data=Path(cases[case_id]['data_path'])
        inputs=backend_sources+[path,data,data.with_suffix('.identity.json'),cache/'cache_identity.json',cache/'lio_cache.npz',initial/'initial_condition.json']
        b=recorded('strong_baseline_'+key,'cached_backend',inputs,[PY,str(ROOT/'scripts/run_outer_baseline.py'),str(cache),str(initial),str(path),'--gnss-ned',str(data)])
        backend=Path(b['output']); metric=None; evaluation=None
        if (backend/'backend_identity.json').exists():
            e=recorded('offline_evaluate_'+key,'engineering',eval_sources+[backend/'manifest.json',backend/'trajectory.csv',backend/'per_update.jsonl',backend/'backend_identity.json',stress/'event_manifest.json',ROOT/'configs/development_experiment_protocol.json',initial/'initial_condition.json',ROOT/'data/i2nav-dataset/building00/building00_groundtruth.nav'],
                [PY,str(ROOT/'scripts/evaluate_outer.py'),str(backend),str(stress/'event_manifest.json'),case_id])
            evaluation=e['output']; mp=Path(evaluation)/'metrics.json'
            if mp.exists():metric=json.loads(mp.read_text())
        record={'name':name,'config':conf,'case':case_id,'backend':b,'evaluation':evaluation,'metrics':metric}
        records[key]=record; history.append(record)
        with (out/'progress.jsonl').open('a') as f:f.write(json.dumps(record)+'\n')
        h=metric['metrics']['horizontal_rmse_m'] if metric else None
        print(json.dumps({'config':name,'case':case_id,'horizontal_rmse_m':h,'backend_exit':b['exit_code']}),flush=True)
        return record

    def natural_score(record):
        m=record['metrics']
        return m['metrics']['horizontal_rmse_m'] if m and m['metrics']['coverage']>=.99 and record['backend']['exit_code']==0 else float('inf')

    qs=[]
    for i,q in enumerate(protocol['shared_Q_calibration_candidates']):
        conf={**base,**q}; r=run(conf,'B3_Q'+str(i),'natural'); qs.append(r)
    bestq=min(qs,key=natural_score)
    if not natural_score(bestq)<float('inf'):raise RuntimeError('no physically available baseline Q candidate')
    shared={k:bestq['config'][k] for k in ['q_time_m2ps','q_distance_m2pm']}
    base.update(shared)
    selections={'shared_Q':shared,'Q_calibration_records':[{'name':r['name'],'natural_RMSE_m':natural_score(r)} for r in qs]}
    chosen={}
    for method in ['B2','B3']:
        conf={**base,'method':method}; chosen[method]=(method,conf)
    policies={
        'B4':[{**base,'method':'B4','nis_limit':v} for v in protocol['B4_NIS_limits']],
        'B5':[{**base,'method':'B5','huber_limit':v} for v in protocol['B5_Huber_limits']],
        'B6':[{**base,'method':'B6','huber_limit':v['huber_limit'],'recovery':{**base['recovery'],**{k:v[k] for k in ['wait_s','recovery_s','protection']}}} for v in screen['B6_configs']]}
    selection_table=[]
    for method, configs in policies.items():
        screened=[]
        for i,conf in enumerate(configs):
            name=method+'_C'+str(i)
            runs=[run(conf,name,c) for c in screen['screen_cases']]
            normal=natural_score(runs[0]); primary=runs[1:]
            valid=all(r['metrics'] and r['metrics']['metrics']['coverage']>=.99 and r['backend']['exit_code']==0 for r in primary)
            target=float(__import__('numpy').mean([r['metrics']['event_macro_RMSE_m'] for r in primary])) if valid else float('inf')
            screened.append({'name':name,'config':conf,'natural_RMSE_m':normal,'primary_macro_RMSE_m':target,'valid':valid})
        bestnormal=min(r['natural_RMSE_m'] for r in screened)
        allowed=bestnormal+max(.02*bestnormal,.05)
        for r in screened:r['eligible']=r['valid'] and r['natural_RMSE_m']<=allowed
        eligible=[r for r in screened if r['eligible']]
        if not eligible:raise RuntimeError('no eligible '+method+' control; retain failure evidence')
        selected=min(eligible,key=lambda r:(r['primary_macro_RMSE_m'],r['natural_RMSE_m']))
        chosen[method]=(selected['name'],selected['config'])
        selections[method]=selected;selection_table.extend(screened)
    all_selected={}
    for method,(name,conf) in chosen.items():
        all_selected[method]=[run(conf,name,c) for c in cases]
    strongest=min([selections[k] for k in ['B4','B5','B6']],key=lambda r:r['primary_macro_RMSE_m'])
    selections.update({'strongest_eligible_control':strongest,'complete_selected':all_selected,
        'selection_table':selection_table,'candidate_configs_consumed':0,'heldout_opened':False})
    (out/'selected_baselines.json').write_text(json.dumps(selections,indent=2)+'\n')
    with (out/'selected_table.csv').open('w') as f:
        writer=csv.writer(f);writer.writerow(['method','config','case','RMSE_m','P95_m','max_m','coverage','event_macro_RMSE_m','backend_run','evaluation_run'])
        for method,runs in all_selected.items():
            for r in runs:
                m=r['metrics'];v=m['metrics'] if m else {}
                writer.writerow([method,r['name'],r['case'],v.get('horizontal_rmse_m'),v.get('horizontal_p95_m'),v.get('horizontal_max_m'),v.get('coverage'),m.get('event_macro_RMSE_m') if m else None,r['backend']['output'],r['evaluation']])
    print(json.dumps({'selected_Q':shared,'strongest_control':strongest,'completed_pairs':len(history),'candidate_budget_used':0}),flush=True)

if __name__=='__main__':main()
