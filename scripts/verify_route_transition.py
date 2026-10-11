#!/usr/bin/env python3
"""Replay all frozen development methods after role plumbing; require exact parity."""
import argparse,json,os
from pathlib import Path
import numpy as np
from replay_experiment_batch import ExperimentBatch,ROOT,PY,digest
p=argparse.ArgumentParser();p.add_argument('verification_run');p.add_argument('--resume-matrix');a=p.parse_args();source=Path(a.verification_run).resolve();v=json.loads((source/'final_verification.json').read_text())
if not v['quantitative_development_gate']:raise ValueError('development review has not passed')
out=Path(os.environ['LIO_GINS_RUN_DIR']);candidate=json.loads((Path(v['candidate_source'])/'candidate_screen.json').read_text());plan=candidate['revision_plan'];b=json.loads(Path(plan['P3_selected_baselines']).read_text())
methods=json.loads((ROOT/'configs/final_evaluation_methods.json').read_text());previous={**v['records']['primary'],'B2':b['complete_selected']['B2']}
batch=ExperimentBatch(out/'matrix',plan['cache_run'],plan['initialization_run'],plan['stress_run'])
if a.resume_matrix:
    old_matrix=Path(a.resume_matrix).resolve()/'matrix'
    identities=json.loads((old_matrix/'source_identity.json').read_text())
    if identities!=batch.source_identity:raise ValueError('cannot reuse a matrix after its estimator/evaluator sources changed')
    saved=[json.loads(line) for line in (old_matrix/'progress.jsonl').read_text().splitlines()]
    if len(saved)!=len(methods)*len(batch.cases):raise ValueError('only a complete retained matrix may be reused')
    for r in saved:
        if r['config']!=methods[r['name']]:raise ValueError('retained matrix parameters changed')
        for folder in [Path(r['backend']['output']),Path(r['evaluation'])]:
            if json.loads((folder/'manifest.json').read_text())['status']!='PASSED':raise ValueError('retained child failed')
        batch.records[r['name']+'__'+r['case']]=r
comparisons=[];records={}
for name,conf in methods.items():
    old={r['case']:r for r in previous[name]};records[name]=[]
    for case in batch.cases:
        if conf!=old[case]['config']:raise ValueError('transition changed scientific parameters '+name)
        r=batch.run(conf,name,case);records[name].append(r)
        x=Path(old[case]['backend']['output']);y=Path(r['backend']['output'])
        nav_exact=(x/'trajectory.csv').read_bytes()==(y/'trajectory.csv').read_bytes()
        updates_exact=(x/'per_update.jsonl').read_bytes()==(y/'per_update.jsonl').read_bytes()
        metric_exact=r['metrics'] is not None and r['metrics']['metrics']==old[case]['metrics']['metrics'] and r['metrics']['events']==old[case]['metrics']['events']
        comparisons.append({'method':name,'case':case,'old_run':str(x),'new_run':str(y),'trajectory_bytes_exact':nav_exact,'update_log_bytes_exact':updates_exact,'numeric_metrics_exact':metric_exact,'backend_exit':r['backend']['exit_code']})

init=batch.recorded('transition_initializer_identity','engineering',
    [ROOT/'scripts/export_initial_condition.py',ROOT/'configs/initialization_protocol.json']+[ROOT/'data/i2nav-dataset/building00'/n for n in ['building00_groundtruth.nav','building00_F9P_GNSS.pos','building00_ADIS16465_IMU.txt']],
    [PY,str(ROOT/'scripts/export_initial_condition.py')])
initial_exact=(Path(init['output'])/'initial_condition.json').read_bytes()==(Path(plan['initialization_run'])/'initial_condition.json').read_bytes()
native=batch.recorded('transition_native_KF_GINS_fixed_noise2','real_gnss_ins',
    [ROOT/'scripts/run_kf_robot.py',Path(plan['initialization_run'])/'initial_condition.json',ROOT/'third_party/KF-GINS/bin/KF-GINS'],
    [PY,str(ROOT/'scripts/run_kf_robot.py'),plan['initialization_run'],'--noise-scale','2'])
native_old=ROOT/'outputs/20261011T125141177973Z_P2_c04aae55/KF_GINS_Navresult.nav'
native_exact=native_old.read_bytes()==(Path(native['output'])/'KF_GINS_Navresult.nav').read_bytes()
frontend=ROOT/'outputs/20261011T134909303110Z_P2_626b9771'
cache=batch.recorded('transition_bag_count_cache_validation','engineering',
    [ROOT/'scripts/build_lio_cache.py']+[frontend/n for n in ['manifest.json','trajectory.csv','interface_events.csv','frontend_input_identity.json','bag_info.yaml','fast_lio_time_log.csv']],
    [PY,str(ROOT/'scripts/build_lio_cache.py'),str(frontend)])
oldcache=np.load(Path(plan['cache_run'])/'lio_cache.npz');newcache=np.load(Path(cache['output'])/'lio_cache.npz');cache_exact=oldcache.files==newcache.files and all(np.array_equal(oldcache[k],newcache[k],equal_nan=True) for k in oldcache.files)
old_sources=json.loads((source/'primary/source_identity.json').read_text())
mechanism_names=['src/observation_manager/motion_recovery.py','src/observation_manager/availability_recovery.py','src/observation_manager/anchored_recovery.py','src/adapters/geodesy.py','src/adapters/sensor_text.py','src/adapters/causal_lio.py','src/fusion/position_kf.py','src/fusion/fixed_recovery.py','src/evaluation/reference.py']
unchanged=all(digest(ROOT/n)==old_sources[str(ROOT/n)] for n in mechanism_names)
all_exact=bool(initial_exact and native_exact and cache_exact and all(c['trajectory_bytes_exact'] and c['update_log_bytes_exact'] and c['numeric_metrics_exact'] and c['backend_exit']==0 for c in comparisons))
paths=sorted((ROOT/'src').rglob('*.py'))+[ROOT/'scripts'/n for n in ['run_candidate.py','run_outer_baseline.py','run_lio.py','build_lio_cache.py','run_kf_robot.py','evaluate_kf_robot.py','evaluate_outer.py','export_initial_condition.py','prepare_development_stress.py','run_heldout.py','replay_experiment_batch.py']]
result={'all_trajectories_exact':all_exact,'unchanged_mechanism_sources':unchanged,'reused_matrix_from':a.resume_matrix,'comparisons':comparisons,'records':records,'initializer_bytes_exact':initial_exact,'native_B1_bytes_exact':native_exact,'cache_arrays_exact':cache_exact,'additional_runs':{'initializer':init,'native':native,'cache_validation':cache},'source_SHA':{str(p.relative_to(ROOT)):digest(p) for p in paths},'heldout_opened':False,'mechanism_tuning':False}
(out/'transition_parity.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:r for k,r in result.items() if k not in ['records','comparisons','source_SHA']}))
if not all_exact or not unchanged:raise SystemExit(2)
