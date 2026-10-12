#!/usr/bin/env python3
"""Exclusive S9 evidence recorder; never writes R1 register or outputs."""
import argparse,csv,datetime,hashlib,json,os,resource,signal,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(2**20),b''):h.update(b)
    return h.hexdigest()
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',required=True);p.add_argument('--purpose',required=True);p.add_argument('--kind',default='engineering');p.add_argument('--input',action='append',default=[]);p.add_argument('--timeout',type=float,default=1800);p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args();argv=a.command[1:] if a.command[:1]==['--'] else a.command
    if not argv:p.error('real command required')
    rid=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'_'+a.stage+'_'+hashlib.sha256(json.dumps(vars(a),sort_keys=True).encode()).hexdigest()[:8];out=ROOT/'outputs_s9'/rid;out.mkdir(parents=True,exist_ok=False)
    conf={**vars(a),'command':argv};(out/'config_resolved.json').write_text(json.dumps(conf,indent=2)+'\n');snapshot=out/'source_inputs';snapshot.mkdir();inputs={};error=None
    try:
        for name in a.input:
            path=Path(name).resolve();inputs[str(path)]=sha(path)
            if path.is_relative_to(ROOT) and not path.is_relative_to(ROOT/'data') and path.stat().st_size<=2**21:
                dest=snapshot/path.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(path.read_bytes())
    except OSError as e:error=str(e)
    (snapshot/'s9_recorder.py').write_bytes(Path(__file__).read_bytes());diff=subprocess.check_output(['git','diff','--binary','HEAD'],cwd=ROOT);(out/'tracked_source_diff.patch').write_bytes(diff)
    manifest={'goal_id':'LIO-GINS-S9-MULTISCENARIO','run_id':rid,'stage':a.stage,'purpose':a.purpose,'kind':a.kind,'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'dirty_diff_SHA':hashlib.sha256(diff).hexdigest(),'input_SHA':inputs,'started_UTC':utc(),'status':'RUNNING','environment_registry_SHA':sha(ROOT/'containers/derived_rootfs.local.json'),'environment_python':sys.version,'raw_data_role':'S9_role_must_be_declared_by_entry','backup':{'local_preserved':True,'full_remote_numeric':False,'raw_backup':False}}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');env=os.environ.copy();env['LIO_GINS_RUN_DIR']=str(out);env['LIO_GINS_S9_RUN_DIR']=str(out);env['MPLCONFIGDIR']=str(ROOT/'cache/s9/matplotlib');started=time.monotonic()
    with (out/'stdout.log').open('wb') as stdout,(out/'stderr.log').open('wb') as stderr:
        try:
            if error:raise OSError(error)
            proc=subprocess.Popen(argv,cwd=ROOT,env=env,stdout=stdout,stderr=stderr,start_new_session=True);(out/'process.json').write_text(json.dumps({'pid':proc.pid,'recorder_pid':os.getpid()})+'\n')
            try:rc=proc.wait(timeout=a.timeout)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid,signal.SIGTERM)
                try:rc=proc.wait(timeout=10)
                except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);rc=proc.wait()
                manifest['timed_out']=True
        except OSError as e:stderr.write(str(e).encode());rc=127
    usage=resource.getrusage(resource.RUSAGE_CHILDREN);command={'argv':argv,'cwd':str(ROOT),'started_UTC':manifest['started_UTC'],'ended_UTC':utc(),'exit_code':rc,'wall_seconds':time.monotonic()-started,'CPU_user_s':usage.ru_utime,'CPU_system_s':usage.ru_stime,'max_RSS_KiB':usage.ru_maxrss,'executed':error is None}
    (out/'commands.jsonl').write_text(json.dumps(command)+'\n');manifest.update(status='PASSED' if rc==0 else 'FAILED',exit_code=rc,ended_UTC=command['ended_UTC']);(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (out/'SHA256SUMS').write_text(''.join(sha(f)+'  '+str(f.relative_to(out))+'\n' for f in sorted(out.rglob('*')) if f.is_file() and f.name!='SHA256SUMS'))
    receipt=ROOT/'artifacts/s9/street00/run_receipts'/rid;receipt.mkdir(parents=True,exist_ok=False)
    for name in ['manifest.json','commands.jsonl','config_resolved.json','SHA256SUMS']: (receipt/name).write_bytes((out/name).read_bytes())
    with (ROOT/'docs/research_s9/street00/RUN_REGISTER.csv').open('a') as stream:csv.writer(stream).writerow([rid,a.stage,a.purpose,a.kind,rc,str(out),manifest['source_commit']])
    print(json.dumps({'run_id':rid,'output':str(out),'exit_code':rc,'wall_seconds':command['wall_seconds']}));return rc
if __name__=='__main__':raise SystemExit(main())
