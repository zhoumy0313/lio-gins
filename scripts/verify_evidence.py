#!/usr/bin/env python3
"""Verify sealed run contents and original workspace files; never modifies them."""
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

root=Path(__file__).resolve().parents[1]
failures=[];verified=0
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
initial=json.loads((root/'artifacts/initial_workspace.json').read_text())
for name,expected in initial['existing_files_sha256'].items():
    p=root/name
    if not p.exists() or sha(p)!=expected:failures.append('initial file changed: '+name)
with (root/'docs/RUN_REGISTER.csv').open() as f:records=list(csv.DictReader(f))
for run in records:
    folder=Path(run['manifest_path']).parent
    manifest=json.loads((folder/'manifest.json').read_text())
    for line in (folder/'SHA256SUMS').read_text().splitlines():
        expected,name=line.split('  ',1);p=folder/name
        actual=hashlib.sha256(os.readlink(p).encode()).hexdigest() if p.is_symlink() and manifest.get('checksum_mode')=='regular_file_bytes_or_symlink_target_text_v1' else (sha(p) if p.exists() else None)
        if actual!=expected:failures.append('run checksum mismatch: '+str(p))
        verified+=1
    if manifest['status']!=run['status']:failures.append('register status mismatch: '+run['run_id'])
    receipt=root/'artifacts/run_receipts'/run['run_id']
    for name in ['manifest.json','commands.jsonl','config_resolved.json','SHA256SUMS']:
        if (receipt/name).read_bytes()!=(folder/name).read_bytes():failures.append('receipt mismatch: '+str(receipt/name))
for repo in ['KF-GINS','i2Nav-Robot','i2Nav-Robot-Baseline','FAST_LIO_original','livox_ros_driver']:
    r=subprocess.run(['git','-C',str(root/'third_party'/repo),'status','--porcelain'],capture_output=True,text=True)
    if r.returncode or r.stdout:failures.append('upstream dirty/missing: '+repo)
print(json.dumps({'registered_runs':len(records),'verified_files':verified,'initial_files_checked':len(initial['existing_files_sha256']),'failures':failures,'backup_verification':'local integrity only; remote/raw backup unverified; raw dataset separately identified in data manifest'},indent=2))
sys.exit(bool(failures))
