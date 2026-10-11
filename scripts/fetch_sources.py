#!/usr/bin/env python3
"""Fetch the project's locked public sources without changing upstream code."""
import json
import subprocess
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[1]
lock = json.loads((ROOT / 'configs/sources.lock.json').read_text())
parser = argparse.ArgumentParser()
parser.add_argument('--proxy', default=None, help='per-process public proxy URL; no credentials')
args = parser.parse_args()
records = []
def run(argv, cwd=ROOT):
    if args.proxy and argv[0]=='git':
        argv = ['git','-c','http.proxy='+args.proxy,*argv[1:]]
    print(json.dumps({'argv': argv, 'cwd': str(cwd)}), flush=True)
    r = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=180)
    print(r.stdout, end=''); print(r.stderr, end='')
    print(f'exit_code={r.returncode}', flush=True)
    r.check_returncode()
    return r.stdout.strip()
for source in lock['sources']:
    target = ROOT / 'third_party' / source['name']
    if not target.exists():
        run(['git','init',str(target)])
        run(['git','remote','add','origin',source['url']],target)
    try:
        run(['git','cat-file','-e',source['commit']+'^{commit}'],target)
    except subprocess.CalledProcessError:
        run(['git','fetch','--depth','1','origin',source['commit']],target)
    empty_checkout = {p.name for p in target.iterdir()} == {'.git'}
    actual_dirty = run(['git','status','--porcelain'], target)
    if actual_dirty and not empty_checkout:
        raise RuntimeError(f'refuse checkout of dirty source {target}')
    run(['git','checkout','--detach',source['commit']], target)
    head = run(['git','rev-parse','HEAD'], target)
    assert head == source['commit']
    run(['git','submodule','update','--init','--recursive'], target)
    submodules = run(['git','submodule','status','--recursive'], target)
    licenses = [str(p.relative_to(target)) for p in target.rglob('*') if p.is_file() and p.name.lower() in ['license','license.txt','license.md','copying']]
    records.append({**source,'actual_commit':head,'submodules':submodules,'license_files':licenses,'dirty':False})
(ROOT/'configs/sources.local.json').write_text(json.dumps({'sources':records},indent=2)+'\n')
