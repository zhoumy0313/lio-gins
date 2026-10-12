"""Role/freeze safety and bit-identical old numeric-body regression."""
import hashlib,json,tempfile,unittest,ast
from pathlib import Path
from gate import metadata_access,technical_access,verify_freeze,sha
ROOT=Path(__file__).resolve().parents[3]
class Interfaces(unittest.TestCase):
 def test_old_roles_rejected(self):
  for seq in ['building00','parking00','building01']:
   with self.assertRaises(ValueError):metadata_access(seq)
 def test_role_required(self):
  with self.assertRaises(ValueError):technical_access('building02','heldout')
 def test_estimator_numeric_body_identical(self):
  for old,new in [('run_seen_baseline.py','run_baseline.py'),('run_seen_candidate.py','run_candidate.py')]:
   a=(ROOT/'experiments/r2'/old).read_text();b=(ROOT/'experiments/s9/building02'/new).read_text()
   self.assertEqual(a[a.index('method=conf'):a.index("(out/'backend_identity.json')")],b[b.index('method=conf'):b.index("(out/'backend_identity.json')")])
 def test_all19_configs_equal_old(self):
  rows=json.loads((ROOT/'outputs_r2/20261011T181051808417Z_S3_274770dc/complete_index.json').read_text());old={r['method']:r['config'] for r in rows if r['cache']=='primary'}
  self.assertEqual(len(old),19)
  for m,c in old.items():self.assertEqual(c,json.loads((ROOT/'configs/s9'/f'{m}.json').read_text()))
 def test_inherited_metric_functions_equal(self):
  old=ast.parse((ROOT/'experiments/r2/reanalyse.py').read_text());new=ast.parse((ROOT/'experiments/s9/building02/reanalyse.py').read_text())
  for name in ['accepted_clock','error_recovery']:
   a=next(n for n in old.body if isinstance(n,ast.FunctionDef) and n.name==name);b=next(n for n in new.body if isinstance(n,ast.FunctionDef) and n.name==name);self.assertEqual(ast.dump(a,include_attributes=False),ast.dump(b,include_attributes=False))
  a=next(n for n in old.body if isinstance(n,ast.FunctionDef) and n.name=='full_window');b=next(n for n in new.body if isinstance(n,ast.FunctionDef) and n.name=='full_window')
  output=b.body[-1].value;keep=[k.value!='horizontal_Max_m' for k in output.keys];output.keys=[k for k,v in zip(output.keys,keep) if v];output.values=[k for k,v in zip(output.values,keep) if v]
  self.assertEqual(ast.dump(a,include_attributes=False),ast.dump(b,include_attributes=False))
 def fixture(self,d):
  p=Path(d)/'f.json';q=Path(d)/'r.json';f={'type':'S9_FULL_SCIENTIFIC_FREEZE','new_heldout_opening_authorized':True,'source_config_SHA':{}};p.write_text(json.dumps(f));r={'freeze_SHA':sha(p),'push_exit_code':0,'ls_remote_exit_code':0,'verified_S9_HEAD':True,'remote_S9_SHA':'abc','local_commit':'abc','branch':'research/lio-gins-s9-multiscenario'};q.write_text(json.dumps(r));return p,q,f,r
 def test_analysis_freeze_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p,q,f,r=self.fixture(d);f['type']='ANALYSIS_FREEZE_ONLY';p.write_text(json.dumps(f));r['freeze_SHA']=sha(p);q.write_text(json.dumps(r))
   with self.assertRaises(ValueError):verify_freeze(p,q)
 def test_no_remote_receipt_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p,q,f,r=self.fixture(d);r['push_exit_code']=1;q.write_text(json.dumps(r))
   with self.assertRaises(ValueError):verify_freeze(p,q)
 def test_remote_sha_mismatch_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p,q,f,r=self.fixture(d);r['remote_S9_SHA']='different';q.write_text(json.dumps(r))
   with self.assertRaises(ValueError):verify_freeze(p,q)
 def test_changed_source_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p,q,f,r=self.fixture(d);source=Path(d)/'core.py';source.write_text('x=1');f['source_config_SHA']={'core.py':sha(source)};p.write_text(json.dumps(f));r['freeze_SHA']=sha(p);q.write_text(json.dumps(r));verify_freeze(p,q,root=Path(d));source.write_text('x=2')
   with self.assertRaises(ValueError):verify_freeze(p,q,root=Path(d))
if __name__=='__main__':unittest.main(verbosity=2)
