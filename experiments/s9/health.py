"""Read-only S9 technical liveness; never reads reference position payload."""
import json,os,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
for p in sorted((ROOT/'outputs_s9').glob('*/manifest.json')):
 m=json.loads(p.read_text())
 if m['status']!='RUNNING':continue
 proc=json.loads((p.parent/'process.json').read_text());result={'run':m['run_id'],'purpose':m['purpose'],'pid':proc['pid'],'alive':Path('/proc/'+str(proc['pid'])).exists()}
 t=p.parent/'trajectory.csv'
 if t.exists():
  with t.open('rb') as f:
   count=sum(1 for _ in f)
  result['output_rows']=count
  with t.open('rb') as f:
   f.seek(max(0,t.stat().st_size-1024));lines=f.read().splitlines()
  result['last_output_timestamp']=float(lines[-1].replace(b',',b' ').split()[0]) if lines else None
 result['stderr_tail_bytes']=(p.parent/'stderr.log').stat().st_size
 print(json.dumps(result))
