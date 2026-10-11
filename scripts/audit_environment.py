#!/usr/bin/env python3
"""Read-only host audit; never prints environment variables or proxy credentials."""
import json
import os
from pathlib import Path
import shutil
import subprocess

commands = [['uname', '-a'], ['lscpu'], ['free', '-h'], ['df', '-h', '.'],
            ['python3', '--version'], ['cmake', '--version'], ['g++', '--version'],
            ['git', '--version'], ['python3', '-m', 'pip', '--version'],
            ['nvidia-smi'], ['docker', 'version'], ['podman', 'version'],
            ['git', 'status', '--short'], ['git', 'remote', '-v']]
results = []
for argv in commands:
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=20)
        item = {'argv': argv, 'exit_code': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr}
    except FileNotFoundError:
        item = {'argv': argv, 'exit_code': 127, 'stderr': 'executable not found'}
    results.append(item)
print(json.dumps({'cwd': str(Path.cwd()), 'commands': results, 'available': {x: shutil.which(x) for x in ['docker','podman','python3','cmake','g++','git','curl']}, 'disk_bytes': dict(zip(['total','used','free'], shutil.disk_usage('.')))}, indent=2))
if os.environ.get('LIO_GINS_RUN_DIR'):
    Path(os.environ['LIO_GINS_RUN_DIR'], 'environment.json').write_text(json.dumps(results, indent=2)+'\n')
