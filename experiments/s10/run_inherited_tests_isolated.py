"""Byte-identical old tests in a private fixture tree; legacy recorder stays there."""
import json,os,shutil,subprocess,sys
from pathlib import Path
from common import ROOT,sha
OUT=Path(os.environ['LIO_GINS_S10_OUT']);shadow=OUT/'isolated_workspace';shadow.mkdir()
inputs={}
for folder in ['src','scripts','tests','configs','docs']:
 for p in (ROOT/folder).rglob('*'):
  if not p.is_file() or '__pycache__' in p.parts:continue
  target=shadow/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);assert sha(target)==sha(p)
  inputs[str(p.relative_to(ROOT))]=sha(p)
(shadow/'outputs').mkdir()
# This old evaluator test reads one fixed synthetic stress manifest. Copy its
# bytes rather than exposing the original output tree to a legacy writer.
for name in ['outputs/20261011T132959853728Z_P3_7079c4e4/event_manifest.json',
             'outputs/20261011T124056742603Z_P2_e310122b/initial_condition.json',
             'data/i2nav-dataset/building00/building00_groundtruth.nav',
             'data/i2nav-dataset/building00/building00_F9P_GNSS.pos',
             'data/manifests/DATA_MANIFEST.json']:
 original=ROOT/name;target=shadow/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(original,target);assert sha(original)==sha(target);inputs[name]=sha(original)
fixtures=OUT/'fixtures';fixtures.mkdir()
env=os.environ.copy();env['LIO_GINS_RUN_DIR']=str(fixtures);env['PYTHONPATH']=str(shadow);env['PYTHONDONTWRITEBYTECODE']='1'
argv=[sys.executable,'-m','unittest','discover','-s','tests','-v'];rc=subprocess.call(argv,cwd=shadow,env=env)
(OUT/'isolated_test_identity.json').write_text(json.dumps({'copied_files_SHA':inputs,'argv':argv,'exit_code':rc,'old_register_unmodified':True,'legacy_recorder_runs_only_under_shadow':True},indent=2)+'\n');raise SystemExit(rc)
