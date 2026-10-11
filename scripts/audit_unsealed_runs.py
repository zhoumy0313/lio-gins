#!/usr/bin/env python3
"""Account for unsealed exclusive run directories, without rewriting old evidence."""
import hashlib,json,os,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];out=Path(os.environ['LIO_GINS_RUN_DIR']);records=[]
for folder in sorted((ROOT/'outputs').iterdir()):
    if not folder.is_dir() or not re.match(r'^\d{8}T\d{12}Z_P\d_',folder.name) or (folder/'manifest.json').exists():continue
    process=json.loads((folder/'process.json').read_text()) if (folder/'process.json').exists() else None
    active=bool(process and (Path('/proc')/str(process['runner_pid'])).exists())
    conf=json.loads((folder/'config_resolved.json').read_text()) if (folder/'config_resolved.json').exists() else None
    records.append({'directory':str(folder),'classification':'active_unsealed' if active else 'unsealed_without_exit_receipt',
        'process':process,'configuration':conf,'original_exit_code':None,
        'original_child_executed':'unknown' if not process else 'PID record present',
        'currently_missing_declared_inputs':[v for v in conf.get('input',[]) if not Path(v).exists()] if conf else [],
        'preserved_files_SHA':{str(f.relative_to(folder)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(folder.rglob('*')) if f.is_file() and f.stat().st_size<2*1024*1024},
        'limitation':'No original exit receipt; do not reconstruct or invent an original command exit code.'})
(out/'unsealed_directory_audit.json').write_text(json.dumps({'records':records,'action':'read-only audit; existing unsealed dirs kept; missing-input preflight fixed for future runs'},indent=2)+'\n')
print(json.dumps({'unsealed':len(records),'unsealed_without_exit_receipt':sum(r['classification']=='unsealed_without_exit_receipt' for r in records)},indent=2))
