#!/usr/bin/env python3
"""One frozen parking00 evaluation matrix; native frontend precedes cached jobs."""
import argparse,json,os,sys
from pathlib import Path
from replay_experiment_batch import ExperimentBatch,ROOT,PY
sys.path.insert(0,str(ROOT))
from src.adapters.research_access import verify_access

p=argparse.ArgumentParser();p.add_argument('freeze');a=p.parse_args()
freeze=Path(a.freeze).resolve();record=verify_access('parking00','heldout',freeze)
out=Path(os.environ['LIO_GINS_RUN_DIR']);data=ROOT/'data/i2nav-dataset/parking00'

# The small driver below delegates every actual step to the exclusive recorder.
import subprocess
def recorded(purpose,kind,inputs,argv,timeout=180):
    cmd=[PY,str(ROOT/'scripts/record_run.py'),'--phase','P5','--purpose',purpose,'--kind',kind,'--timeout',str(timeout)]
    for n in inputs:cmd+=['--input',str(n)]
    cmd+=['--']+argv
    r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
    with (out/'pipeline_commands.jsonl').open('a') as f:f.write(json.dumps({'argv':cmd,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr})+'\n')
    if not r.stdout:raise RuntimeError('missing recorder receipt '+r.stderr)
    receipt=json.loads(r.stdout.splitlines()[-1]);print(json.dumps(receipt),flush=True)
    if r.returncode:raise RuntimeError('retained failure '+receipt['output'])
    return Path(receipt['output'])

init=recorded('frozen_parking00_first_epoch_initialization','engineering',
    [ROOT/'scripts/export_initial_condition.py',ROOT/'configs/initialization_protocol.json',freeze/'scientific_freeze.json']+[data/n for n in ['parking00_groundtruth.nav','parking00_F9P_GNSS.pos','parking00_ADIS16465_IMU.txt']],
    [PY,str(ROOT/'scripts/export_initial_condition.py'),'--sequence','parking00','--freeze',str(freeze)])
front=recorded('frozen_parking00_full_1x_frontend_native_timing','real_frontend',
    [ROOT/'scripts/run_lio.py',ROOT/'containers/run_inside.sh',ROOT/'containers/shutdown_clock.py',ROOT/'containers/derived_rootfs.local.json',freeze/'scientific_freeze.json'],
    [PY,str(ROOT/'scripts/run_lio.py'),str(data/'parking00.bag'),'--freeze',str(freeze)],3600)
cache=recorded('frozen_parking00_complete_frontend_cache','engineering',
    [ROOT/'scripts/build_lio_cache.py',freeze/'scientific_freeze.json']+[front/n for n in ['manifest.json','trajectory.csv','interface_events.csv','frontend_input_identity.json','bag_info.yaml','fast_lio_time_log.csv']],
    [PY,str(ROOT/'scripts/build_lio_cache.py'),str(front),'--freeze',str(freeze)])
stress=recorded('frozen_parking00_fixed_21_events','engineering',
    [ROOT/'scripts/prepare_development_stress.py',ROOT/'configs/development_experiment_protocol.json',init/'initial_condition.json',data/'parking00_F9P_GNSS.pos',freeze/'scientific_freeze.json'],
    [PY,str(ROOT/'scripts/prepare_development_stress.py'),str(init),'--freeze',str(freeze)])
native=recorded('frozen_parking00_native_KF_GINS_noise2','real_gnss_ins',
    [ROOT/'scripts/run_kf_robot.py',init/'initial_condition.json',data/'parking00_F9P_GNSS.pos',data/'parking00_ADIS16465_IMU.txt',ROOT/'third_party/KF-GINS/bin/KF-GINS',freeze/'scientific_freeze.json'],
    [PY,str(ROOT/'scripts/run_kf_robot.py'),str(init),'--noise-scale','2','--freeze',str(freeze)])
native_eval=recorded('frozen_parking00_B0_B1_evaluation','engineering',
    [ROOT/'scripts/evaluate_kf_robot.py',native/'KF_GINS_Navresult.nav',init/'initial_condition.json',data/'parking00_groundtruth.nav',freeze/'scientific_freeze.json'],
    [PY,str(ROOT/'scripts/evaluate_kf_robot.py'),str(native),str(init),'--freeze',str(freeze)])

batch=ExperimentBatch(out/'outer',cache,init,stress,phase='P5',freeze=freeze)
methods=json.loads((ROOT/'configs/final_evaluation_methods.json').read_text());groups={}
for name,conf in methods.items():
    groups[name]=[batch.run(conf,name,case) for case in batch.cases]
(out/'heldout_matrix.json').write_text(json.dumps({'freeze_directory':str(freeze),'freeze_id':record['freeze_id'],'initialization':str(init),'frontend':str(front),'cache':str(cache),'stress':str(stress),'native_B1':str(native),'native_evaluation':str(native_eval),'complete_methods':groups,'retuned':False,'heldout_opened':True},indent=2)+'\n')
