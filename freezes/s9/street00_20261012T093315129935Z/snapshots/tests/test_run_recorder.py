"""A missing declared input must preserve evidence and never launch the child."""
import json,os,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class PreflightEvidence(unittest.TestCase):
    def test_missing_input_is_recorded_before_child(self):
        marker=Path(os.environ['LIO_GINS_RUN_DIR'])/'must_not_exist'
        argv=[sys.executable,str(ROOT/'scripts/record_run.py'),'--phase','P2','--purpose','expected_missing_input_preflight_failure','--kind','synthetic','--input',str(marker.with_suffix('.missing')),'--',sys.executable,'-c','from pathlib import Path; Path('+repr(str(marker))+').touch()']
        result=subprocess.run(argv,capture_output=True,text=True,cwd=ROOT)
        self.assertEqual(result.returncode,127,result.stderr);self.assertFalse(marker.exists())
        receipt=json.loads(result.stdout.splitlines()[-1]);run=Path(receipt['output'])
        manifest=json.loads((run/'manifest.json').read_text());command=json.loads((run/'commands.jsonl').read_text())
        self.assertEqual(manifest['status'],'FAILED');self.assertFalse(command['executed'])
        self.assertIsNotNone(command['preflight_error']);self.assertTrue((run/'SHA256SUMS').exists())
