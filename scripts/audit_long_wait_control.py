#!/usr/bin/env python3
"""One supplemental fixed-clock development audit; no proposed or heldout retuning."""
import copy,json,os
from pathlib import Path
import numpy as np
from replay_experiment_batch import ExperimentBatch,ROOT,digest
out=Path(os.environ['LIO_GINS_RUN_DIR']);plan=json.loads((ROOT/'configs/long_wait_audit.json').read_text());conf=json.loads((ROOT/'configs/methods/final_P.json').read_text());rows=[];records={}
if plan['fixed_good_duration_s']!=[15,30,60,90] or plan['audit_rounds_max']!=1:raise ValueError('finite control audit changed')
for cache in plan['cache_runs']:
    folder=out/Path(cache).name;batch=ExperimentBatch(folder,ROOT/cache,ROOT/plan['initializer'],ROOT/plan['stress'])
    for duration in plan['fixed_good_duration_s']:
        c=copy.deepcopy(conf);c['method']='P_time_only';c['motion']['good_duration_s']=duration;name='clock_qualification_'+str(duration)
        r=[batch.run(c,name,case) for case in batch.cases];records[Path(cache).name+'_'+name]=r
        indexed={v['case']:v for v in r};valid=all(v['backend']['exit_code']==0 and v['metrics'] and v['metrics']['metrics']['coverage']>=.99 for v in r)
        natural=indexed['natural']['metrics']['metrics']['horizontal_rmse_m'] if indexed['natural']['metrics'] else None
        target=float(np.mean([indexed[k]['metrics']['event_macro_RMSE_m'] for k in ['cluster_jump10','loss30_normal','loss30_bias10']])) if valid else None
        rows.append({'cache':cache,'qualification_s':duration,'natural_RMSE_m':natural,'primary_macro_RMSE_m':target,'valid':bool(valid),'eligible':bool(valid and natural<=plan['baseline_cost_cap_m'])})
(out/'long_wait_audit.json').write_text(json.dumps({'plan':plan,'plan_SHA':digest(ROOT/'configs/long_wait_audit.json'),'table':rows,'records':records,'heldout_evaluated':False,'candidate_changed':False,'main_candidate_configs_added':0,'interpretation':'supplemental audit registered after opening parking00, development only; does not retroactively belong to the original blind matrix'},indent=2)+'\n');print(json.dumps(rows))
