#!/usr/bin/env python3
"""One-command archive recovery using existing frozen cache, never a new blind test."""
import argparse,json,os,subprocess,sys
from pathlib import Path
from replay_experiment_batch import ExperimentBatch,ROOT,PY
p=argparse.ArgumentParser();p.add_argument('--matrix',default='outputs/20261011T154446522435Z_P5_ae13844a');p.add_argument('--method',choices=['B6','P'],default='B6');p.add_argument('--case',choices=['natural','all'],default='natural');a=p.parse_args()
source=Path(a.matrix).resolve();matrixpath=source/'heldout_matrix.json';m=json.loads(matrixpath.read_text())
if json.loads((source/'manifest.json').read_text())['status']!='PASSED':raise ValueError('source matrix is not sealed successful execution')
if 'LIO_GINS_RUN_DIR' not in os.environ:
    command=[PY,str(ROOT/'scripts/record_run.py'),'--phase','P7','--purpose','archive_recovery_'+a.method+'_'+a.case,'--timeout','1200','--input',str(Path(__file__)),'--input',str(matrixpath),'--',PY,str(Path(__file__)),*sys.argv[1:]]
    raise SystemExit(subprocess.run(command,cwd=ROOT).returncode)
out=Path(os.environ['LIO_GINS_RUN_DIR']);batch=ExperimentBatch(out/'matrix',m['cache'],m['initialization'],m['stress'],phase='P7',freeze=m['freeze_directory']);conf=json.loads((ROOT/'configs/final_evaluation_methods.json').read_text())[a.method];old={r['case']:r for r in m['complete_methods'][a.method]};checks=[]
for case in batch.cases:
    if a.case=='natural' and case!='natural':continue
    r=batch.run(conf,a.method,case);x=Path(old[case]['backend']['output']);y=Path(r['backend']['output'])
    checks.append({'case':case,'original_backend':str(x),'restored_backend':str(y),'restored_evaluation':r['evaluation'],'trajectory_bytes_exact':(x/'trajectory.csv').read_bytes()==(y/'trajectory.csv').read_bytes(),'update_log_bytes_exact':(x/'per_update.jsonl').read_bytes()==(y/'per_update.jsonl').read_bytes(),'metrics_exact':r['metrics']['metrics']==old[case]['metrics']['metrics'],'backend_exit':r['backend']['exit_code']})
passed=all(c['trajectory_bytes_exact'] and c['update_log_bytes_exact'] and c['metrics_exact'] and c['backend_exit']==0 for c in checks)
(out/'archive_recovery.json').write_text(json.dumps({'source_matrix':str(source),'freeze_id':m['freeze_id'],'method':a.method,'checks':checks,'all_outputs_exact':passed,'new_blind_test':False,'new_parameters':False,'scope':'recovery on this machine from immutable original cache and inputs; not a clean-machine rebuild or off-site backup'},indent=2)+'\n')
if not passed:raise SystemExit(2)
