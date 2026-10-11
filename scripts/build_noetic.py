#!/usr/bin/env python3
"""Build prepared context with an existing usable Docker daemon; never invokes sudo."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
from context_integrity import verify_context

p=argparse.ArgumentParser();p.add_argument('prepared_run');a=p.parse_args()
context=Path(a.prepared_run).resolve()/'container_context'
if not (context/'Dockerfile').exists():p.error('prepared context missing')
verified=verify_context(a.prepared_run)
print(json.dumps({'verified_context':verified}),flush=True)
if not shutil.which('docker'):
    print('BLOCKED: Docker is absent. No host installation attempted.',file=sys.stderr);sys.exit(127)
subprocess.run(['docker','version'],check=True)
tag='lio-gins-r1-noetic:'+verified['manifest_sha256'][:12]
argv=['docker','build','--platform','linux/amd64','-t',tag,str(context)]
subprocess.run(argv,check=True)
info=json.loads(subprocess.check_output(['docker','image','inspect',tag],text=True))[0]
root=Path(__file__).resolve().parents[1]
(root/'containers/derived_image.local.json').write_text(json.dumps({'tag':tag,'image_id':info['Id'],'prepared_context_manifest_sha256':verified['manifest_sha256'],'prepared_run':str(Path(a.prepared_run).resolve()),'container_build_verified':True,'frontend_run_verified':False},indent=2)+'\n')
