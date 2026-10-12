"""New exclusive S10 offline run, actual exits, immutable source snapshots."""
import argparse,datetime,hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--stage',required=True);p.add_argument('--purpose',required=True);p.add_argument('--timeout',type=int,default=600);p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args();argv=a.command[1:] if a.command[:1]==['--'] else a.command
runid=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'_'+a.stage+'_'+hashlib.sha256(json.dumps(argv).encode()).hexdigest()[:8];out=ROOT/'cache/s10/runs'/runid;out.mkdir(parents=True,exist_ok=False)
sha=lambda q:hashlib.sha256(Path(q).read_bytes()).hexdigest()
source={str(q.relative_to(ROOT)):sha(q) for q in (ROOT/'experiments/s10').rglob('*.py')}
for name in source:
 target=out/'source'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
manifest={'run_id':runid,'stage':a.stage,'purpose':a.purpose,'argv':argv,'started_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'source_SHA':source,'status':'RUNNING','analysis_role':'post-hoc read-only, no independent confirmation'}
(out/'run_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');env=os.environ.copy();env.update(LIO_GINS_S10_OUT=str(out),PYTHONDONTWRITEBYTECODE='1',MPLCONFIGDIR=str(ROOT/'cache/s10/matplotlib'));start=time.monotonic()
try:
 with (out/'stdout.log').open('w') as stdout,(out/'stderr.log').open('w') as stderr:
  child=subprocess.Popen(argv,cwd=ROOT,env=env,stdout=stdout,stderr=stderr);(out/'process.json').write_text(json.dumps({'pid':child.pid}));rc=child.wait(timeout=a.timeout)
except subprocess.TimeoutExpired:
 child.terminate();child.wait();rc=124
manifest.update(exit_code=rc,wall_seconds=time.monotonic()-start,status='COMPLETED' if rc==0 else 'FAILED',finished_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat());(out/'run_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
checks={str(q.relative_to(out)):sha(q) for q in out.rglob('*') if q.is_file()};(out/'SHA256SUMS').write_text(''.join(d+'  '+n+'\n' for n,d in sorted(checks.items())))
receipt=ROOT/'artifacts/s10/run_receipts'/runid;receipt.mkdir(parents=True,exist_ok=False)
for name in ['run_manifest.json','SHA256SUMS','stdout.log','stderr.log']:shutil.copy2(out/name,receipt/name)
print(json.dumps({'run_id':runid,'output':str(out),'exit_code':rc,'wall_seconds':manifest['wall_seconds']}));sys.exit(rc)
