"""All original tests unchanged; isolate just the recorder's output-root side effect."""
import hashlib,json,os,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=Path(os.environ['LIO_GINS_RUN_DIR']);sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'experiments/r2'))
register=ROOT/'docs/RUN_REGISTER.csv';before=hashlib.sha256(register.read_bytes()).hexdigest()
shadow=OUT/'recorder_isolated_project';(shadow/'scripts').mkdir(parents=True);(shadow/'outputs').mkdir();(shadow/'docs').mkdir();(shadow/'scripts/record_run.py').write_bytes((ROOT/'scripts/record_run.py').read_bytes());(shadow/'docs/RUN_REGISTER.csv').write_text(register.read_text().splitlines()[0]+'\n')
suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_*.py');count=suite.countTestCases()
module=sys.modules['test_run_recorder'];module.ROOT=shadow
result=unittest.TextTestRunner(verbosity=2).run(suite)
after=hashlib.sha256(register.read_bytes()).hexdigest();assert before==after,'R1 register mutated'
additional=unittest.TestLoader().loadTestsFromName('test_reacquisition_metrics');r2count=additional.countTestCases();r2result=unittest.TextTestRunner(verbosity=2).run(additional)
audit={'original_tests':count,'original_passed':result.wasSuccessful(),'R2_tests':r2count,'R2_passed':r2result.wasSuccessful(),'R1_register_SHA_before_after':before,'R1_register_unchanged':before==after,'isolation':'Only test_run_recorder.ROOT redirected to retained project-local shadow; copied original recorder bytes identical; no test assertions modified'}
(OUT/'regression_audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit));raise SystemExit(0 if result.wasSuccessful() and r2result.wasSuccessful() and count==64 else 1)
