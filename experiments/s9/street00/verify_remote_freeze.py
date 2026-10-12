"""After B push, actual three-branch readback binds freeze to Git blob before access."""
import datetime,json,os,subprocess
from pathlib import Path
from gate import sha
ROOT=Path(__file__).resolve().parents[3];OUT=Path(os.environ['LIO_GINS_RUN_DIR']);context=json.loads((ROOT/'artifacts/s9/street00/technical_context.json').read_text());freeze=ROOT/context['freeze_relative_path'];checkpoint=json.loads((ROOT/'artifacts/s9/checkpoints/B.json').read_text());branch='research/lio-gins-s9-multiscenario'
assert not (ROOT/'artifacts/s9/street00/FIRST_MATRIX_OPENING.json').exists(),'first opening already exists'
assert checkpoint['push_exit_code']==0 and checkpoint['verified_S9_HEAD']
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();assert head==checkpoint['local_commit'];blob=subprocess.check_output(['git','show',head+':'+context['freeze_relative_path']],cwd=ROOT);import hashlib
assert hashlib.sha256(blob).hexdigest()==sha(freeze)
env=os.environ.copy();env['GIT_SSH_COMMAND']='ssh -o HostName=ssh.github.com -p 443 -o HostKeyAlias=github.com -o ProxyCommand="python3 /home/aaron/lio_gins/experiments/r2/proxy_tunnel.py ssh.github.com 443" -o UserKnownHostsFile=/home/aaron/lio_gins/cache/push_github/known_hosts -o StrictHostKeyChecking=yes -o HostKeyAlgorithms=ssh-ed25519 -o UpdateHostKeys=no -o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=15 -o ServerAliveCountMax=2'
argv=['git','ls-remote','--heads','origin',branch,'research/lio-gins-r1','research/lio-gins-r2-submission','research/lio-gins-s8-building01'];done=subprocess.run(argv,cwd=ROOT,env=env,capture_output=True,text=True);refs={r.split()[1]:r.split()[0] for r in done.stdout.splitlines()}
assert done.returncode==0 and refs.get('refs/heads/'+branch)==head
assert refs['refs/heads/research/lio-gins-r1']=='c12a42a3484458e1737e63201792e1122fc99c0d'
assert refs['refs/heads/research/lio-gins-r2-submission']=='8ef95ce597433a8b45c90ec1d13eb57ec4355555'
assert refs['refs/heads/research/lio-gins-s8-building01']=='ca6bf095426a5c1e06387f156a15178921276358'
receipt={'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'branch':branch,'local_commit':head,'remote_S9_SHA':refs['refs/heads/'+branch],'freeze_relative_path':context['freeze_relative_path'],'freeze_SHA':sha(freeze),'push_exit_code':checkpoint['push_exit_code'],'push_evidence':'artifacts/s9/checkpoints/B.json','ls_remote_exit_code':done.returncode,'ls_remote_argv':argv,'ls_remote_stdout':done.stdout,'ls_remote_stderr':done.stderr,'verified_S9_HEAD':True,'committed_frozen_blob_exactly_matches':True,'R1_R2_remote_heads_unchanged':True,'performance_matrix_not_yet_opened':True,'readback_run':str(OUT)}
(ROOT/'docs/research_s9/street00/FREEZE_PUSH_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');(OUT/'FREEZE_PUSH_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
statepath=ROOT/'docs/research_s9/street00/STATE.json';state=json.loads(statepath.read_text());state['flags']['science_freeze_pushed_before_test']=True;state['freeze_commit']=head;state['freeze_SHA']=sha(freeze);state['freeze_path']=context['freeze_relative_path'];statepath.write_text(json.dumps(state,indent=2)+'\n');print(json.dumps(receipt))
