"""Local S10 checkpoint only. No remote branch authorization inferred."""
import datetime,json,subprocess,sys,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE='4f7a4b4c5b87040d7d7307f25a06cd785b1ff7b9';stage=sys.argv[1]
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT,text=True).strip()
assert git('branch','--show-current')=='research/lio-gins-s10-moderate-bias-paper'
protected=git('ls-tree','-r','--name-only',BASE).splitlines();assert not git('diff',BASE,'--',*protected),'inherited file modified'
subprocess.run(['git','add','--','docs/research_s10','experiments/s10','artifacts/s10',*[str(p.relative_to(ROOT)) for p in sorted((ROOT/'paper/versions').glob('s10_r[0-9][0-9]'))],*(['paper/submission_candidate/s10'] if (ROOT/'paper/submission_candidate/s10').exists() else [])],cwd=ROOT,check=True)
for p in git('diff','--cached','--name-only').splitlines():
 f=ROOT/p;assert f.stat().st_size<10000000
 if f.suffix in {'.py','.md','.json','.tex','.bib','.csv','.log','.txt'}:
  data=f.read_text(errors='ignore');assert not re.search(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}',data),'possible sensitive material'

subprocess.run(['git','-c','user.name=Codex checkpoint','-c','user.email=codex@localhost','commit','-m',f'S10 {stage}: moderate-bias evidence checkpoint'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
print(json.dumps({'stage':stage,'local_commit':git('rev-parse','HEAD'),'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'push_performed':False,'reason':'new remote branch requires separate user authorization'}))
