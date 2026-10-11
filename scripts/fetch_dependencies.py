#!/usr/bin/env python3
"""Restore previously observed dependency commits. No unpinned network selection."""
import argparse
import json
from pathlib import Path
import subprocess

root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--proxy',default=None);a=p.parse_args()
lock=json.loads((root/'configs/dependencies.lock.json').read_text())
for dep in lock['dependencies']:
    folder='FAST_LIO_original' if dep['name']=='FAST_LIO' else dep['name']
    repo=root/'third_party'/folder
    prefix=['git']+(['-c','http.proxy='+a.proxy] if a.proxy else [])
    def run(argv,cwd=root):
        cmd=prefix+argv;print(json.dumps({'argv':cmd,'cwd':str(cwd)}),flush=True)
        subprocess.run(cmd,cwd=cwd,check=True,timeout=180)
    if not repo.exists():
        run(['init',str(repo)]);run(['remote','add','origin',dep['url']],repo)
    if set(x.name for x in repo.iterdir())!={'.git'}:
        dirty=subprocess.check_output(['git','-C',str(repo),'status','--porcelain'],text=True)
        if dirty:raise RuntimeError('refuse modifying dirty dependency')
    present=subprocess.run(['git','-C',str(repo),'cat-file','-e',dep['commit']+'^{commit}'],capture_output=True)
    if present.returncode:run(['fetch','--depth','1','origin',dep['commit']],repo)
    run(['checkout','--detach',dep['commit']],repo)
