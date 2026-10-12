"""Read current evidence before resuming; never starts a duplicate blind matrix."""
import json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
state=json.loads((ROOT/'docs/research_s8/STATE.json').read_text());print(json.dumps(state,indent=2));print(subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True))
for p in sorted((ROOT/'outputs_s8').glob('*/manifest.json')):
 m=json.loads(p.read_text())
 if m['status']=='RUNNING':
  print(json.dumps({'active_manifest':str(p),'purpose':m['purpose'],'process':json.loads((p.parent/'process.json').read_text()) if (p.parent/'process.json').exists() else None}))
opening=ROOT/'artifacts/s8/FIRST_MATRIX_OPENING.json'
if opening.exists():print('Independent matrix already opened. Preserve all failures; finish only missing identical-frozen pairs using original progress, never retune or restart a blind test.');print(opening.read_text())
