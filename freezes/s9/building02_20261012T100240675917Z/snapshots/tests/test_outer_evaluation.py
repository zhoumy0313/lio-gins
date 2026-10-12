"""Known vector errors and missing output test the independent real-grid evaluator."""
import json,os,subprocess,sys,unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]

class OfflineGrid(unittest.TestCase):
    def test_known_error_and_missing_grid_remain_visible(self):
        from src.evaluation.reference import load_i2nav_local_ned,interpolate_with_gaps
        base=Path(os.environ['LIO_GINS_RUN_DIR'])/'offline_evaluation_fixtures';base.mkdir()
        initial=ROOT/'outputs/20261011T124056742603Z_P2_e310122b'
        stress=ROOT/'outputs/20261011T132959853728Z_P3_7079c4e4'
        event=json.loads((stress/'event_manifest.json').read_text())
        ic=json.loads((initial/'initial_condition.json').read_text())
        ref=load_i2nav_local_ned(ROOT/'data/i2nav-dataset/building00/building00_groundtruth.nav')
        grid=np.arange(int(np.ceil(ic['reference_epoch_sow']*10)),int(np.floor(ref[-1,0]*10))+1)/10
        positions,valid=interpolate_with_gaps(ref[:,0],ref[:,1:4],grid,.02)
        self.assertTrue(valid.all())
        for missing in [False,True]:
            run=base/('missing' if missing else 'complete');run.mkdir();ev=run/'evaluation';ev.mkdir()
            nav=np.column_stack([grid,positions+[3,4,2],grid+.1,np.full(len(grid),.1),np.ones(len(grid))])
            if missing:nav=np.delete(nav,np.arange(100,110),axis=0)
            np.savetxt(run/'trajectory.csv',nav,delimiter=',',header='sow,N,E,D,available_sow,delay_s,valid',comments='')
            (run/'per_update.jsonl').write_text('')
            (run/'manifest.json').write_text(json.dumps({'status':'PASSED','kind':'synthetic','fixture':True}))
            (run/'backend_identity.json').write_text(json.dumps({'method':'synthetic_known_error','gnss_sha256':event['cases'][0]['sha256'],'initialization_run':str(initial),'source_cache_run':'synthetic_fixture','source_cache_sha256':'synthetic_fixture'}))
            env=os.environ.copy();env['LIO_GINS_RUN_DIR']=str(ev)
            command=[sys.executable,str(ROOT/'scripts/evaluate_outer.py'),str(run),str(stress/'event_manifest.json'),'natural']
            result=subprocess.run(command,env=env,capture_output=True,text=True)
            (run/'command.json').write_text(json.dumps({'argv':command,'exit_code':result.returncode}));(run/'stdout.log').write_text(result.stdout);(run/'stderr.log').write_text(result.stderr)
            self.assertEqual(result.returncode,0,result.stderr)
            m=json.loads((ev/'metrics.json').read_text())['metrics']
            self.assertEqual(m['samples_expected'],len(grid));self.assertEqual(m['samples_valid'],len(grid)-(10 if missing else 0))
            self.assertAlmostEqual(m['horizontal_rmse_m'],5.,places=11)
            self.assertAlmostEqual(m['horizontal_p95_m'],5.,places=11)
            self.assertAlmostEqual(m['vertical_rmse_m'],2.,places=11)
            self.assertAlmostEqual(m['coverage'],(len(grid)-(10 if missing else 0))/len(grid))
