"""Retained stage state, local checkpoint, authorized R2 branch push and readback."""
import datetime,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];stage=sys.argv[1];next_stage=sys.argv[2]
def git(*args,env=None):return subprocess.check_output(['git',*args],cwd=ROOT,text=True,env=env).strip()
assert git('branch','--show-current')=='research/lio-gins-r2-submission'
assert git('rev-parse','research/lio-gins-r1')=='c12a42a3484458e1737e63201792e1122fc99c0d'
assert not git('diff','c12a42a','--','src','scripts','configs/baselines','configs/methods','freezes','paper/working')
statepath=ROOT/'docs/research_r2/STATE.json';state=json.loads(statepath.read_text());state.update(stage=next_stage,execution_status=stage+'_checkpoint_complete',updated_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat());state.setdefault('completed_stages',[]).append(stage)
statepath.write_text(json.dumps(state,indent=2)+'\n')
with (ROOT/'docs/research_r2/STATE_HISTORY.jsonl').open('a') as f:f.write(json.dumps({'stage_completed':stage,'next_stage':next_stage,'UTC':state['updated_UTC'],'flags':state})+'\n')
paths=['.gitignore','AGENTS.md','docs/GOAL_LIO_GINS_R2_SUBMISSION.md','docs/USER_ACTION_REQUIRED.md','docs/research_r2','configs/r2','experiments/r2','paper/versions','artifacts/r2','freezes/r2']
subprocess.run(['git','add','--',*[p for p in paths if (ROOT/p).exists()]],cwd=ROOT,check=True)
for path in git('diff','--cached','--name-only').splitlines():
    assert (ROOT/path).stat().st_size<10000000,path
subprocess.run(['git','-c','user.name=Codex checkpoint','-c','user.email=codex@localhost','commit','-m',f'R2 {stage}: research evidence and manuscript checkpoint'],cwd=ROOT,check=True)
env=os.environ.copy();env['GIT_SSH_COMMAND']='ssh -o UserKnownHostsFile=/home/aaron/lio_gins/cache/push_github/known_hosts -o StrictHostKeyChecking=yes -o HostKeyAlgorithms=ssh-ed25519 -o UpdateHostKeys=no -o BatchMode=yes -o ConnectTimeout=15'
push=subprocess.run(['git','push','-u','origin','research/lio-gins-r2-submission'],cwd=ROOT,env=env,check=False,capture_output=True,text=True)
head=git('rev-parse','HEAD');remote=git('ls-remote','--heads','origin','research/lio-gins-r2-submission','research/lio-gins-r1',env=env) if push.returncode==0 else ''
receipt={'stage':stage,'local_commit':head,'push_exit_code':push.returncode,'push_stdout':push.stdout,'push_stderr':push.stderr,'remote_advertisement':remote,'R1_preserved':True,'verified_R2_HEAD':head+'\trefs/heads/research/lio-gins-r2-submission' in remote}
dest=ROOT/'artifacts/r2/checkpoints';dest.mkdir(parents=True,exist_ok=True);(dest/(stage+'.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt));assert receipt['verified_R2_HEAD']
