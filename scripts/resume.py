#!/usr/bin/env python3
"""Read state/Git/process/evidence, then audit newly supplied data without evaluating it."""
import argparse,json
from pathlib import Path
import subprocess
import sys

root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--audit-data',action='store_true');a=p.parse_args()
state=json.loads((root/'docs/GOAL_STATE.json').read_text())
print(json.dumps(state,indent=2),flush=True)
subprocess.run(['git','status','--short'],cwd=root,check=True)
active=[]
for proc in Path('/proc').iterdir():
    if not proc.name.isdigit():continue
    try:
        argv=(proc/'cmdline').read_bytes().decode().split('\0')
        cwd=(proc/'cwd').resolve()
        # Inspect command operands, not the contents of a parent shell's script.
        related=any(x.endswith('record_run.py') or x.endswith('/bin/KF-GINS') or x.endswith('/fastlio_mapping') for x in argv)
        related |= any(argv[i:i+2]==['rosbag','play'] for i in range(len(argv)-1))
        if related and (cwd==root or cwd.is_relative_to(root) or any(x.startswith(str(root)) for x in argv)):
            active.append(proc.name+' '+' '.join(argv).strip())
    except (OSError,UnicodeDecodeError):pass
if active:
    print('Existing project process detected; inspect its log instead of starting duplicate work:\n'+'\n'.join(active));sys.exit(3)
records=(root/'docs/RUN_REGISTER.csv').read_text().splitlines()
print('Latest registered run:',records[-1] if len(records)>1 else 'none',flush=True)
if not a.audit_data:
    print('Resume inspection complete. Read current phase/next_action and the latest manifests; no duplicate run or automatic raw-data reread. Optional --audit-data performs a new metadata/identity audit.')
    sys.exit(0)
argv=[sys.executable,str(root/'scripts/record_run.py'),'--phase','P1','--purpose','resume_readonly_dataset_audit','--blocked-exit','2',
      '--input',str(root/'scripts/audit_data.py'),'--input',str(root/'configs/data_locations.json'),'--input',str(root/'src/adapters/sensor_text.py'),'--input',str(root/'src/evaluation/reference.py'),
      '--',sys.executable,str(root/'scripts/audit_data.py')]
r=subprocess.run(argv,cwd=root)
if r.returncode==0:
    if state.get('test_performance_opened'):
        print('Development files present. Heldout was already opened; inspect the archived freeze and final conclusion. A replay is not another blind test.')
    else:
        print('Development files present. Continue from GOAL_STATE and validated run receipts; heldout remains closed until scientific freeze.')
else:
    print('See docs/USER_ACTION_REQUIRED.md. No performance evaluation or method search was started.')
sys.exit(r.returncode)
