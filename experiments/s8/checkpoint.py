"""Retained stage state, local checkpoint, authorized R2 branch push and readback."""
import datetime,json,os,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];stage=sys.argv[1];next_stage=sys.argv[2]
def git(*args,env=None):return subprocess.check_output(['git',*args],cwd=ROOT,text=True,env=env).strip()
assert git('branch','--show-current')=='research/lio-gins-s8-building01'
assert git('rev-parse','research/lio-gins-r1')=='c12a42a3484458e1737e63201792e1122fc99c0d'
protected=[p for p in git('ls-tree','-r','--name-only','8ef95ce').splitlines() if p not in ['AGENTS.md','.gitignore','docs/USER_ACTION_REQUIRED.md']]
assert not git('diff','8ef95ce','--',*protected), 'R1/R2 tracked evidence changed'
assert git('rev-parse','research/lio-gins-s8-building01')=='8ef95ce597433a8b45c90ec1d13eb57ec4355555'
statepath=ROOT/'docs/research_s8/STATE.json';state=json.loads(statepath.read_text());state.update(stage=next_stage,execution_status=stage+'_checkpoint_complete',updated_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat());state.setdefault('completed_stages',[]).append(stage)
statepath.write_text(json.dumps(state,indent=2)+'\n')
with (ROOT/'docs/research_s8/STATE_HISTORY.jsonl').open('a') as f:f.write(json.dumps({'stage_completed':stage,'next_stage':next_stage,'UTC':state['updated_UTC'],'flags':state})+'\n')
paths=['.gitignore','AGENTS.md','docs/GOAL_LIO_GINS_S8_BUILDING01_SUBMISSION.md','docs/USER_ACTION_REQUIRED.md','docs/research_s8','configs/s8','experiments/s8','paper/versions/s8_r01','paper/versions/s8_r02','paper/versions/s8_r03','paper/submission_candidate/s8','artifacts/s8','freezes/s8']
subprocess.run(['git','add','--',*[p for p in paths if (ROOT/p).exists()]],cwd=ROOT,check=True)
for path in git('diff','--cached','--name-only').splitlines():
    assert (ROOT/path).stat().st_size<10000000,path
staged=git('diff','--cached','--binary')
for pattern in [r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',r'gh[pousr]_[A-Za-z0-9]{30,}',r'github_pat_[A-Za-z0-9_]{40,}',r'AKIA[A-Z0-9]{16}']:
    assert re.search(pattern,staged) is None,'sensitive content detected'
subprocess.run(['git','-c','user.name=Codex checkpoint','-c','user.email=codex@localhost','commit','-q','-m',f'S8 {stage}: research evidence and manuscript checkpoint'],cwd=ROOT,check=True)
head=git('rev-parse','HEAD')
env=os.environ.copy();env['GIT_SSH_COMMAND']='ssh -o HostName=ssh.github.com -p 443 -o HostKeyAlias=github.com -o ProxyCommand="python3 /home/aaron/lio_gins/experiments/r2/proxy_tunnel.py ssh.github.com 443" -o UserKnownHostsFile=/home/aaron/lio_gins/cache/push_github/known_hosts -o StrictHostKeyChecking=yes -o HostKeyAlgorithms=ssh-ed25519 -o UpdateHostKeys=no -o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=15 -o ServerAliveCountMax=2'
push=subprocess.run(['git','push','-u','origin','research/lio-gins-s8-building01'],cwd=ROOT,env=env,check=False,capture_output=True,text=True)
remote=git('ls-remote','--heads','origin','research/lio-gins-s8-building01','research/lio-gins-r1',env=env) if push.returncode==0 else ''
receipt={'stage':stage,'local_commit':head,'push_exit_code':push.returncode,'push_stdout':push.stdout,'push_stderr':push.stderr,'remote_advertisement':remote,'R1_preserved':True,'staged_secret_scan_passed':True,'file_size_scan_passed':True,'verified_S8_HEAD':head+'\trefs/heads/research/lio-gins-s8-building01' in remote}
dest=ROOT/'artifacts/s8/checkpoints';dest.mkdir(parents=True,exist_ok=True);(dest/(stage+'.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt));assert receipt['verified_S8_HEAD']
