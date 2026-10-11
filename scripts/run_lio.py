#!/usr/bin/env python3
"""Run one verified building00 bag in a restricted container and exclusive recorder output."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

p=argparse.ArgumentParser();p.add_argument('bag');a=p.parse_args()
root=Path(__file__).resolve().parents[1];bag=Path(a.bag).resolve()
if bag.name!='building00.bag':p.error('only development route allowed before verified freeze protocol')
if not bag.is_relative_to(root/'data/raw'):p.error('raw bag must be in this workspace data/raw')
h=hashlib.sha256()
with bag.open('rb') as f:
    for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
expected=json.loads((root/'third_party/i2Nav-Robot/sha256sum/sha256sum.json').read_text())[bag.name]
if h.hexdigest()!=expected:raise ValueError('raw bag SHA mismatch')
lock=root/'containers/derived_image.local.json'
if not lock.exists():print('BLOCKED: no verified derived container image',file=sys.stderr);sys.exit(2)
image=json.loads(lock.read_text())
out=Path(os.environ['LIO_GINS_RUN_DIR'])
argv=['docker','run','--rm','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges',
      '--user',f'{os.getuid()}:{os.getgid()}','--tmpfs','/tmp:rw,nosuid,nodev,size=1g',
      '--mount',f'type=bind,src={bag.parent},dst=/input,readonly',
      '--mount',f'type=bind,src={out},dst=/output',image['image_id'],'/input/'+bag.name]
(out/'frontend_input_identity.json').write_text(json.dumps({'bag':str(bag),'sha256':h.hexdigest(),'image':image,'sensors':['AT128','ADIS16465'],'timing_kind':'rosbag_replay_wall_and_logged_frontend_processing'},indent=2)+'\n')
print(json.dumps({'argv':argv}),flush=True)
sys.exit(subprocess.run(argv).returncode)
