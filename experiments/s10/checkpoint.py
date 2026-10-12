"""Local S10 checkpoint only. No remote branch authorization inferred."""
import datetime,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE='4f7a4b4c5b87040d7d7307f25a06cd785b1ff7b9';stage=sys.argv[1]
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT,text=True).strip()
assert git('branch','--show-current')=='research/lio-gins-s10-moderate-bias-paper'
protected=git('ls-tree','-r','--name-only',BASE).splitlines();assert not git('diff',BASE,'--',*protected),'inherited file modified'
subprocess.run(['git','add','--','docs/research_s10','experiments/s10','artifacts/s10',*[p for p in ['paper/versions/s10_r01','paper/versions/s10_r02','paper/versions/s10_r03','paper/submission_candidate/s10'] if (ROOT/p).exists()]],cwd=ROOT,check=True)
for p in git('diff','--cached','--name-only').splitlines():assert (ROOT/p).stat().st_size<10000000
subprocess.run(['git','-c','user.name=Codex checkpoint','-c','user.email=codex@localhost','commit','-m',f'S10 {stage}: moderate-bias evidence checkpoint'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
print(json.dumps({'stage':stage,'local_commit':git('rev-parse','HEAD'),'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'push_performed':False,'reason':'new remote branch requires separate user authorization'}))
