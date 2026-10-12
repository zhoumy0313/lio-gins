"""Only authorized S9 branch checkpoint; protects all inherited science."""
import datetime,json,os,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];stage=sys.argv[1];next_stage=sys.argv[2]
BASE='ca6bf095426a5c1e06387f156a15178921276358';BRANCH='research/lio-gins-s9-multiscenario'
def git(*args,env=None):return subprocess.check_output(['git',*args],cwd=ROOT,text=True,env=env).strip()
assert git('branch','--show-current')==BRANCH
protected=[p for p in git('ls-tree','-r','--name-only',BASE).splitlines() if p not in ['AGENTS.md','.gitignore','docs/USER_ACTION_REQUIRED.md']]
assert not git('diff',BASE,'--',*protected),'inherited science modified'
p=ROOT/'docs/research_s9/STATE.json';s=json.loads(p.read_text());s.update(stage=next_stage,status=stage+'_CHECKPOINT_COMPLETE',updated_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat());s['completed_stages'].append(stage);p.write_text(json.dumps(s,indent=2)+'\n')
with (ROOT/'docs/research_s9/STATE_HISTORY.jsonl').open('a') as f:f.write(json.dumps(s)+'\n')
paths=['AGENTS.md','.gitignore','docs/USER_ACTION_REQUIRED.md','docs/GOAL_LIO_GINS_S9_MULTISCENARIO.md','docs/research_s9','configs/s9','configs/s9_initialization_protocol.json','experiments/s9','artifacts/s9','freezes/s9','paper/versions/s9_r01','paper/versions/s9_r02','paper/versions/s9_r03','paper/submission_candidate/s9']
subprocess.run(['git','add','--',*[p for p in paths if (ROOT/p).exists()]],check=True)
for p in git('diff','--cached','--name-only').splitlines():assert (ROOT/p).stat().st_size<10000000,p
staged=git('diff','--cached','--binary')
for pattern in [r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',r'gh[pousr]_[A-Za-z0-9]{30,}',r'github_pat_[A-Za-z0-9_]{40,}',r'AKIA[A-Z0-9]{16}']:assert not re.search(pattern,staged),'secret found'
subprocess.run(['git','-c','user.name=Codex checkpoint','-c','user.email=codex@localhost','commit','-q','-m',f'S9 {stage}: fixed multiscenario study checkpoint'],check=True);head=git('rev-parse','HEAD')
env=os.environ.copy();env['GIT_SSH_COMMAND']='ssh -o HostName=ssh.github.com -p 443 -o HostKeyAlias=github.com -o ProxyCommand="python3 /home/aaron/lio_gins/experiments/r2/proxy_tunnel.py ssh.github.com 443" -o UserKnownHostsFile=/home/aaron/lio_gins/cache/push_github/known_hosts -o StrictHostKeyChecking=yes -o HostKeyAlgorithms=ssh-ed25519 -o UpdateHostKeys=no -o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=15 -o ServerAliveCountMax=2'
push=subprocess.run(['git','push','-u','origin',BRANCH],env=env,text=True,capture_output=True)
adv=git('ls-remote','--heads','origin',BRANCH,'research/lio-gins-r1','research/lio-gins-r2-submission','research/lio-gins-s8-building01',env=env) if push.returncode==0 else ''
refs={r.split()[1]:r.split()[0] for r in adv.splitlines()};expected={'refs/heads/'+BRANCH:head,'refs/heads/research/lio-gins-r1':'c12a42a3484458e1737e63201792e1122fc99c0d','refs/heads/research/lio-gins-r2-submission':'8ef95ce597433a8b45c90ec1d13eb57ec4355555','refs/heads/research/lio-gins-s8-building01':BASE}
r={'stage':stage,'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'local_commit':head,'push_exit_code':push.returncode,'push_stdout':push.stdout,'push_stderr':push.stderr,'remote_advertisement':adv,'verified_S9_HEAD':refs.get('refs/heads/'+BRANCH)==head,'all_inherited_remote_heads_unchanged':all(refs.get(k)==v for k,v in expected.items()),'size_secret_checks_passed':True}
dest=ROOT/'artifacts/s9/checkpoints';dest.mkdir(parents=True,exist_ok=True);(dest/(stage+'.json')).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r));assert push.returncode==0 and refs==expected
