#!/usr/bin/env python3
"""Run one preregistered finite revision, retain all configs and apply shared gate."""
import argparse,json,os,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from replay_experiment_batch import ExperimentBatch,ROOT,digest
p=argparse.ArgumentParser();p.add_argument('revision_plan');a=p.parse_args();plan_path=Path(a.revision_plan).resolve();plan=json.loads(plan_path.read_text());out=Path(os.environ['LIO_GINS_RUN_DIR']);protocol=json.loads((ROOT/'configs/method_search_protocol.json').read_text());baseline=json.loads(Path(plan['P3_selected_baselines']).read_text())
if plan['revision'] not in ['r01','r02','r03'] or not 1<=len(plan['configs'])<=protocol['max_main_configs_per_revision']:raise ValueError('bounded revision budget violated')
cap=protocol['shared_normal_cost_cap_m'];valid_controls=[c for c in baseline['selection_table'] if c['valid'] and c['natural_RMSE_m']<=cap];control=min(valid_controls,key=lambda r:r['primary_macro_RMSE_m'])
batch=ExperimentBatch(out,plan['cache_run'],plan['initialization_run'],plan['stress_run'])
(out/'plan_identity.json').write_text(json.dumps({'plan':plan,'plan_SHA':digest(plan_path),'control':control,'shared_natural_cap_m':cap,'protocol_SHA':digest(ROOT/'configs/method_search_protocol.json'),'heldout_opened':False},indent=2)+'\n')
screen=[]
for i,conf in enumerate(plan['configs']):
    name=plan['revision']+'_C'+str(i);runs=[batch.run(conf,name,c) for c in protocol['screen_cases']]
    valid=all(r['metrics'] and r['metrics']['metrics']['coverage']>=.99 and r['backend']['exit_code']==0 for r in runs)
    natural=runs[0]['metrics']['metrics']['horizontal_rmse_m'] if runs[0]['metrics'] else None
    target=float(np.mean([r['metrics']['event_macro_RMSE_m'] for r in runs[1:]])) if valid else None
    screen.append({'name':name,'config':conf,'natural_RMSE_m':natural,'primary_macro_RMSE_m':target,'valid':bool(valid),'eligible':bool(valid and natural<=cap),
        'absolute_gain_m':control['primary_macro_RMSE_m']-target if target is not None else None,'relative_gain':1-target/control['primary_macro_RMSE_m'] if target is not None else None})
eligible=[r for r in screen if r['eligible']]
best=min(eligible,key=lambda r:(r['primary_macro_RMSE_m'],r['natural_RMSE_m'])) if eligible else None
diagnostic_best=min([r for r in screen if r['valid']],key=lambda r:r['primary_macro_RMSE_m']) if any(r['valid'] for r in screen) else None
selected=best or diagnostic_best;full=[]
if selected:full=[batch.run(selected['config'],selected['name'],c) for c in batch.cases]
gate=bool(best and best['absolute_gain_m']>=.1 and best['relative_gain']>=.03)
result={'revision':plan['revision'],'revision_plan':plan,'screen_table':screen,'control':control,'shared_natural_cap_m':cap,'selected':selected,'selected_is_eligible':best is not None,'complete_selected':full,'development_gate_on_primary_cache':gate,'scientific_freeze_allowed':False,'requires_ablations_and_second_cache':True,'main_configs_used':len(plan['configs']),'candidate_revisions_used':int(plan['revision'][-1]),'heldout_opened':False}
(out/'candidate_screen.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'revision':plan['revision'],'best':selected,'eligible':best is not None,'gate_on_one_cache':gate,'main_configs':len(plan['configs'])}),flush=True)
