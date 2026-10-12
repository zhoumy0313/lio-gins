"""No experiment opening until all queued technical replay tasks end successfully."""
import datetime,json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];deadline=time.monotonic()+7200
while time.monotonic()<deadline:
 p=ROOT/'artifacts/s9/engineering_results.json'
 if p.exists():
  rows=json.loads(p.read_text())
  if len(rows)==3 and all(r['status']=='TECHNICALLY_READY' for r in rows):
   print('All three technical routes ready; begin complete collective freeze workflow.',flush=True)
   subprocess.run([sys.executable,str(ROOT/'experiments/s9/run_study.py')],cwd=ROOT,check=True);raise SystemExit(0)
 time.sleep(5)
raise SystemExit('Timed out waiting for technical replays. Preserve runs; no precision opened by this controller.')
