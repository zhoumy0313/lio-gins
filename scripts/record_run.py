#!/usr/bin/env python3
"""Run a real command once in an exclusive evidence directory. No shell evaluation."""
import argparse
import csv
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--phase', required=True)
    p.add_argument('--purpose', required=True)
    p.add_argument('--kind', default='engineering', choices=['engineering', 'synthetic', 'real_frontend', 'cached_backend'])
    p.add_argument('--input', action='append', default=[])
    p.add_argument('--cwd', default=str(ROOT))
    p.add_argument('--timeout', type=float, default=1800)
    p.add_argument('--blocked-exit', type=int, default=None)
    p.add_argument('command', nargs=argparse.REMAINDER)
    a = p.parse_args()
    argv = a.command[1:] if a.command[:1] == ['--'] else a.command
    if not argv:
        p.error('command required')
    config = {**vars(a), 'command': argv}
    digest = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:8]
    rid = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '_' + a.phase + '_' + digest
    out = ROOT / 'outputs' / rid
    out.mkdir(exist_ok=False)
    (out / 'config_resolved.json').write_text(json.dumps(config, indent=2) + '\n')
    head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True)
    diff = subprocess.run(['git', 'diff', '--binary', 'HEAD'], cwd=ROOT, capture_output=True).stdout
    inputs = {str(Path(x).resolve()): sha(x) for x in a.input}
    manifest = {'run_id': rid, 'phase': a.phase, 'purpose': a.purpose, 'kind': a.kind,
                'source_commit': head.stdout.strip() if head.returncode == 0 else None,
                'tracked_dirty_diff_sha256': hashlib.sha256(diff).hexdigest(),
                'runner_sha256': sha(__file__), 'input_sha256': inputs,
                'config_sha256': sha(out / 'config_resolved.json'), 'created_at': utc(),
                'backup': {'local_preserved': True, 'remote_numeric_backed_up': False, 'raw_data_backed_up': False}}
    env = os.environ.copy()
    env['LIO_GINS_RUN_DIR'] = str(out)
    started = utc()
    t = time.monotonic()
    with (out / 'stdout.log').open('wb') as stdout, (out / 'stderr.log').open('wb') as stderr:
        try:
            proc = subprocess.Popen(argv, cwd=a.cwd, env=env, stdout=stdout, stderr=stderr, start_new_session=True)
            (out / 'process.json').write_text(json.dumps({'pid': proc.pid, 'runner_pid': os.getpid(), 'started_at': started}) + '\n')
            try:
                rc = proc.wait(timeout=a.timeout)
            except subprocess.TimeoutExpired:
                import signal
                os.killpg(proc.pid, signal.SIGTERM)
                try:
                    rc = proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
                    rc = proc.wait()
                manifest['timed_out'] = True
        except OSError as e:
            stderr.write(str(e).encode())
            rc = 127
    command = {'argv': argv, 'cwd': a.cwd, 'started_at': started, 'ended_at': utc(),
               'exit_code': rc, 'wall_seconds': time.monotonic() - t}
    (out / 'commands.jsonl').write_text(json.dumps(command) + '\n')
    status = 'PASSED' if rc == 0 else ('BLOCKED' if rc == a.blocked_exit else 'FAILED')
    manifest.update({'status': status, 'exit_code': rc, 'ended_at': utc()})
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (out / 'SHA256SUMS').write_text(''.join(f'{sha(f)}  {f.relative_to(out)}\n' for f in sorted(out.rglob('*')) if f.is_file() and f.name != 'SHA256SUMS'))
    receipt = ROOT / 'artifacts' / 'run_receipts' / rid
    receipt.mkdir(parents=True, exist_ok=False)
    for name in ['manifest.json', 'commands.jsonl', 'config_resolved.json', 'SHA256SUMS']:
        (receipt / name).write_bytes((out / name).read_bytes())
    with (ROOT / 'docs/RUN_REGISTER.csv').open('a') as f:
        csv.writer(f, lineterminator='\n').writerow([rid, a.phase, a.purpose, manifest['status'], str(out / 'manifest.json')])
    print(json.dumps({'run_id': rid, 'exit_code': rc, 'output': str(out), 'wall_seconds': command['wall_seconds']}), flush=True)
    return rc if rc >= 0 else 128 - rc


if __name__ == '__main__':
    sys.exit(main())
