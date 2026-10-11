#!/usr/bin/env python3
"""Build prepared context with an existing usable Docker daemon; never invokes sudo."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

p=argparse.ArgumentParser();p.add_argument('prepared_run');a=p.parse_args()
context=Path(a.prepared_run).resolve()/'container_context'
if not (context/'Dockerfile').exists():p.error('prepared context missing')
if not shutil.which('docker'):
    print('BLOCKED: Docker is absent. No host installation attempted.',file=sys.stderr);sys.exit(127)
subprocess.run(['docker','version'],check=True)
identity=Path(a.prepared_run).resolve()/'context_sha256.json'
tag='lio-gins-r1-noetic:'+hashlib.sha256(identity.read_bytes()).hexdigest()[:12]
argv=['docker','build','--platform','linux/amd64','-t',tag,str(context)]
subprocess.run(argv,check=True)
info=json.loads(subprocess.check_output(['docker','image','inspect',tag],text=True))[0]
root=Path(__file__).resolve().parents[1]
(root/'containers/derived_image.local.json').write_text(json.dumps({'tag':tag,'image_id':info['Id'],'prepared_context_manifest_sha256':hashlib.sha256(identity.read_bytes()).hexdigest(),'container_build_verified':True,'frontend_run_verified':False},indent=2)+'\n')
