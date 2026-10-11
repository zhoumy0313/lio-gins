#!/usr/bin/env python3
"""Run untouched upstream official demo, only resolving input/output paths."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import yaml

root = Path(__file__).resolve().parents[1]
out = Path(os.environ['LIO_GINS_RUN_DIR'])
upstream = root / 'third_party/KF-GINS'
source = upstream / 'dataset/kf-gins.yaml'
config = yaml.safe_load(source.read_text())
for key in ['imupath', 'gnsspath']:
    config[key] = str((upstream/config[key]).resolve())
config['outputpath'] = str(out)
resolved = out / 'kf-gins-resolved.yaml'
resolved.write_text(yaml.safe_dump(config, sort_keys=False))
exe = upstream/'bin/KF-GINS'
inputs = [source, exe, Path(config['imupath']), Path(config['gnsspath'])]
(out/'demo_input_identity.json').write_text(json.dumps({str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},indent=2)+'\n')
argv = [str(exe), str(resolved)]
t = time.monotonic()
r = subprocess.run(argv, cwd=upstream)
(out/'demo_command.json').write_text(json.dumps({'argv':argv,'cwd':str(upstream),'exit_code':r.returncode,'wall_seconds':time.monotonic()-t},indent=2)+'\n')
sys.exit(r.returncode)
