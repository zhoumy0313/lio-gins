#!/usr/bin/env python3
"""One-command building00 full replay or cached replay; never opens heldout."""
import argparse,json,os,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];PY=str(ROOT/'.venv/bin/python')
p=argparse.ArgumentParser();p.add_argument('--sequence',choices=['building00'],default='building00')
p.add_argument('--mode',choices=['cached','full'],default='cached')
p.add_argument('--method',choices=['B6','P'],default='B6')
p.add_argument('--case',choices=['natural','all'],default='natural')
p.add_argument('--cache-run',default='outputs/20261011T141044340351Z_P2_9dd3f300')
a=p.parse_args()

if 'LIO_GINS_RUN_DIR' not in os.environ:
    command=[PY,str(ROOT/'scripts/record_run.py'),'--phase','P7','--purpose','development_delivery_'+a.mode+'_'+a.method,'--timeout','5400',
        '--input',str(Path(__file__)),'--input',str(ROOT/('configs/baselines/final_B6.json' if a.method=='B6' else 'configs/methods/final_P.json')),
        '--',PY,str(Path(__file__)),*sys.argv[1:]]
    raise SystemExit(subprocess.run(command,cwd=ROOT).returncode)

out=Path(os.environ['LIO_GINS_RUN_DIR'])
def recorded(purpose,kind,sources,argv,timeout=180):
    command=[PY,str(ROOT/'scripts/record_run.py'),'--phase','P7','--purpose',purpose,'--kind',kind,'--timeout',str(timeout)]
    for source in sources:command+=['--input',str(source)]
    command+=['--']+argv
    r=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
    with (out/'pipeline_commands.jsonl').open('a') as f:f.write(json.dumps({'argv':command,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr})+'\n')
    if not r.stdout:raise RuntimeError('no run receipt: '+r.stderr)
    receipt=json.loads(r.stdout.splitlines()[-1]);print(json.dumps(receipt),flush=True)
    if r.returncode:raise RuntimeError('retained failed child at '+receipt['output'])
    return Path(receipt['output'])

initial=ROOT/'outputs/20261011T124056742603Z_P2_e310122b'
stress=ROOT/'outputs/20261011T132959853728Z_P3_7079c4e4'
cache=(ROOT/a.cache_run).resolve()
data=ROOT/'data/i2nav-dataset/building00'
full_runs={}
if a.mode=='full':
    initial=recorded('delivery_controlled_initialization','engineering',
        [ROOT/'scripts/export_initial_condition.py',ROOT/'configs/initialization_protocol.json']+[data/n for n in ['building00_groundtruth.nav','building00_F9P_GNSS.pos','building00_ADIS16465_IMU.txt']],
        [PY,str(ROOT/'scripts/export_initial_condition.py')])
    frontend=recorded('delivery_full_building00_frontend','real_frontend',
        [ROOT/'scripts/run_lio.py',ROOT/'containers/run_inside.sh',ROOT/'containers/shutdown_clock.py',ROOT/'containers/derived_rootfs.local.json'],
        [PY,str(ROOT/'scripts/run_lio.py'),str(data/'building00.bag')],3600)
    cache=recorded('delivery_validate_full_frontend_cache','engineering',
        [ROOT/'scripts/build_lio_cache.py']+[frontend/n for n in ['manifest.json','trajectory.csv','interface_events.csv','frontend_input_identity.json','fast_lio_time_log.csv']],
        [PY,str(ROOT/'scripts/build_lio_cache.py'),str(frontend)])
    stress=recorded('delivery_fixed_stress_inputs','engineering',
        [ROOT/'scripts/prepare_development_stress.py',ROOT/'configs/development_experiment_protocol.json',initial/'initial_condition.json',data/'building00_F9P_GNSS.pos'],
        [PY,str(ROOT/'scripts/prepare_development_stress.py'),str(initial)])
    native=recorded('delivery_native_KF_GINS_fixed_noise2','real_gnss_ins',
        [ROOT/'scripts/run_kf_robot.py',initial/'initial_condition.json',data/'building00_F9P_GNSS.pos',data/'building00_ADIS16465_IMU.txt',ROOT/'third_party/KF-GINS/bin/KF-GINS'],
        [PY,str(ROOT/'scripts/run_kf_robot.py'),str(initial),'--noise-scale','2'])
    native_eval=recorded('delivery_native_B0_B1_evaluation','engineering',
        [ROOT/'scripts/evaluate_kf_robot.py',native/'KF_GINS_Navresult.nav',initial/'initial_condition.json',data/'building00_groundtruth.nav'],
        [PY,str(ROOT/'scripts/evaluate_kf_robot.py'),str(native),str(initial)])
    full_runs={'frontend':str(frontend),'native_B1':str(native),'B0_B1_evaluation':str(native_eval)}

config=ROOT/('configs/baselines/final_B6.json' if a.method=='B6' else 'configs/methods/final_P.json')
script=ROOT/'scripts'/('run_outer_baseline.py' if a.method=='B6' else 'run_candidate.py')
events=json.loads((stress/'event_manifest.json').read_text())
if events['sequence']!='building00' or events['role']!='development':raise ValueError('closed heldout route')
records=[]
sources=[script]+sorted((ROOT/'src/adapters').glob('*.py'))+sorted((ROOT/'src/fusion').glob('*.py'))
if a.method=='P':sources+=sorted((ROOT/'src/observation_manager').glob('*.py'))
for case in events['cases']:
    if a.case=='natural' and case['id']!='natural':continue
    observed=Path(case['data_path'])
    backend=recorded('delivery_'+a.method+'_'+case['id'],'cached_backend',sources+[config,cache/'lio_cache.npz',cache/'cache_identity.json',initial/'initial_condition.json',observed,observed.with_suffix('.identity.json')],
        [PY,str(script),str(cache),str(initial),str(config),'--gnss-ned',str(observed)])
    evaluation=recorded('delivery_evaluate_'+a.method+'_'+case['id'],'engineering',
        [ROOT/'scripts/evaluate_outer.py',ROOT/'src/evaluation/reference.py',backend/'manifest.json',backend/'trajectory.csv',backend/'per_update.jsonl',backend/'backend_identity.json',stress/'event_manifest.json',initial/'initial_condition.json',data/'building00_groundtruth.nav'],
        [PY,str(ROOT/'scripts/evaluate_outer.py'),str(backend),str(stress/'event_manifest.json'),case['id']])
    records.append({'case':case['id'],'backend':str(backend),'evaluation':str(evaluation)})
(out/'delivery_replay.json').write_text(json.dumps({'sequence':'building00','mode':a.mode,'method':a.method,'cache':str(cache),'initialization':str(initial),'stress':str(stress),'records':records,'full_runs':full_runs,'heldout_opened':False,'timing_scope':'cached mode excludes frontend; full mode preserves separate native frontend and backend receipts'},indent=2)+'\n')
