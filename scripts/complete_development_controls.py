#!/usr/bin/env python3
"""Resume-aware P2→P3 sequencing; wait for real frontend, validate, then controls."""
import argparse,json,os,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];PY=str(ROOT/'.venv/bin/python')
p=argparse.ArgumentParser();p.add_argument('frontend_run');p.add_argument('first_frontend_run');p.add_argument('initialization_run');p.add_argument('stress_run');a=p.parse_args();out=Path(os.environ['LIO_GINS_RUN_DIR'])
frontend=Path(a.frontend_run).resolve();first=Path(a.first_frontend_run).resolve();initial=Path(a.initialization_run).resolve();stress=Path(a.stress_run).resolve()
while not (frontend/'manifest.json').exists():
    print('Awaiting sealed frontend '+frontend.name,flush=True);time.sleep(30)
if json.loads((frontend/'manifest.json').read_text())['status']!='PASSED':raise RuntimeError('frontend failed: preserve outputs; inspect before continuing')

def recorded(phase,purpose,kind,inputs,argv,timeout=180):
    command=[PY,str(ROOT/'scripts/record_run.py'),'--phase',phase,'--purpose',purpose,'--kind',kind,'--timeout',str(timeout)]
    for source in inputs:command+=['--input',str(source)]
    command+=['--']+argv
    result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
    with (out/'commands_executed.jsonl').open('a') as f:f.write(json.dumps({'argv':command,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr})+'\n')
    if not result.stdout:raise RuntimeError('missing receipt '+result.stderr)
    receipt=json.loads(result.stdout.splitlines()[-1]);print(json.dumps(receipt),flush=True)
    with (out/'completed_steps.jsonl').open('a') as f:f.write(json.dumps({'step':purpose,**receipt})+'\n')
    if result.returncode:raise RuntimeError('step failed: '+purpose+' at '+receipt['output'])
    return Path(receipt['output'])

cache=recorded('P2','validate_graceful_full_frontend_cache_and_native_timing','engineering',
    [ROOT/'scripts/build_lio_cache.py',ROOT/'src/adapters/sensor_text.py']+[frontend/n for n in ['manifest.json','trajectory.csv','interface_events.csv','fast_lio_time_log.csv','frontend_input_identity.json']],
    [PY,str(ROOT/'scripts/build_lio_cache.py'),str(frontend)])
repeat=recorded('P2','same_bag_binary_frontend_repeat_consistency','engineering',
    [ROOT/'scripts/compare_frontend_repeats.py']+[f/n for f in [first,frontend] for n in ['trajectory.csv','frontend_input_identity.json']]+[frontend/'fast_lio_time_log.csv'],
    [PY,str(ROOT/'scripts/compare_frontend_repeats.py'),str(first),str(frontend)])
tests=recorded('P2','full_interface_causality_filter_and_offline_evaluation_checks','synthetic',
    sorted((ROOT/'tests').glob('test_*.py'))+[ROOT/'scripts/evaluate_outer.py',ROOT/'scripts/run_outer_baseline.py',ROOT/'scripts/record_run.py',ROOT/'src/evaluation/reference.py',ROOT/'src/adapters/causal_lio.py',ROOT/'src/fusion/position_kf.py',ROOT/'src/fusion/fixed_recovery.py'],
    [PY,'-m','unittest','discover','-s','tests','-v'])
screen=recorded('P3','finite_matched_Q_NIS_Huber_fixed_recovery_development_screen','engineering',
    [ROOT/'scripts/screen_baselines.py',ROOT/'configs/baseline_screen_protocol.json',ROOT/'configs/development_experiment_protocol.json',cache/'cache_identity.json',initial/'initial_condition.json',stress/'event_manifest.json'],
    [PY,str(ROOT/'scripts/screen_baselines.py'),str(cache),str(initial),str(stress)],timeout=1800)
plots=recorded('P3','strong_baseline_figures_with_exact_point_and_run_SHA_bindings','engineering',
    [ROOT/'scripts/plot_baselines.py',screen/'selected_baselines.json'],[PY,str(ROOT/'scripts/plot_baselines.py'),str(screen)])
(out/'control_pipeline_result.json').write_text(json.dumps({'frontend':str(frontend),'cache':str(cache),'repeat':str(repeat),'tests':str(tests),'screen':str(screen),'plots':str(plots),'candidate_budget_used':0,'heldout_opened':False},indent=2)+'\n')
