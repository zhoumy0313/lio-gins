#!/usr/bin/env python3
"""Fixed-parameter attribution and two-cache verification, with no heldout access."""
import argparse, copy, json, os
from pathlib import Path
import numpy as np
from replay_experiment_batch import ExperimentBatch, ROOT, PY, digest

p=argparse.ArgumentParser()
p.add_argument('candidate_screen')
a=p.parse_args()
source=Path(a.candidate_screen).resolve()
candidate=json.loads((source/'candidate_screen.json').read_text())
if not candidate['development_gate_on_primary_cache']:
    raise ValueError('no primary-cache gain: further verification is not authorized by this gate')
out=Path(os.environ['LIO_GINS_RUN_DIR'])
plan=candidate['revision_plan']
selected=candidate['selected']
baseline=json.loads(Path(plan['P3_selected_baselines']).read_text())
protocol=json.loads((ROOT/'configs/frontend_sensitivity_protocol.json').read_text())
cap=candidate['shared_natural_cap_m']
all_records=[]

class VerificationBatch(ExperimentBatch):
    def baseline(self,conf,name,case_id):
        key=name+'__'+case_id
        path=self.config_dir/(name+'.json')
        if not path.exists():path.write_text(json.dumps(conf,indent=2)+'\n')
        elif json.loads(path.read_text())!=conf:raise ValueError('configuration changed')
        data=Path(self.cases[case_id]['data_path'])
        backend_sources=[ROOT/'scripts/run_outer_baseline.py']+self.backend_sources[4:]
        b=self.recorded('fixed_frontend_sensitivity_'+key,'cached_backend',backend_sources+[path,data,data.with_suffix('.identity.json'),self.cache/'lio_cache.npz',self.cache/'cache_identity.json',self.initial/'initial_condition.json'],
            [PY,str(ROOT/'scripts/run_outer_baseline.py'),str(self.cache),str(self.initial),str(path),'--gnss-ned',str(data)])
        run=Path(b['output']);metric=None;evaluation=None
        if (run/'backend_identity.json').exists():
            e=self.recorded('evaluate_fixed_frontend_sensitivity_'+key,'engineering',self.eval_sources+[run/'manifest.json',run/'trajectory.csv',run/'per_update.jsonl',run/'backend_identity.json',self.stress/'event_manifest.json',ROOT/'configs/development_experiment_protocol.json',self.initial/'initial_condition.json',ROOT/'data/i2nav-dataset/building00/building00_groundtruth.nav'],
                [PY,str(ROOT/'scripts/evaluate_outer.py'),str(run),str(self.stress/'event_manifest.json'),case_id])
            evaluation=e['output'];mp=Path(evaluation)/'metrics.json'
            if mp.exists():metric=json.loads(mp.read_text())
        result={'name':name,'config':conf,'case':case_id,'backend':b,'evaluation':evaluation,'metrics':metric}
        with (self.out/'progress.jsonl').open('a') as f:f.write(json.dumps(result)+'\n')
        print(json.dumps({'control':name,'case':case_id,'backend_exit':b['exit_code']}),flush=True)
        return result

def summarize(name,records):
    indexed={r['case']:r for r in records}
    valid=all(r['backend']['exit_code']==0 and r['metrics'] and r['metrics']['metrics']['coverage']>=.99 for r in records)
    natural=indexed['natural']['metrics']['metrics']['horizontal_rmse_m'] if indexed['natural']['metrics'] else None
    primary=float(np.mean([indexed[c]['metrics']['event_macro_RMSE_m'] for c in ['cluster_jump10','loss30_normal','loss30_bias10']])) if valid else None
    return {'name':name,'natural_RMSE_m':natural,'primary_macro_RMSE_m':primary,'valid':bool(valid),'eligible':bool(valid and natural<=cap)}

tables={};records_by_cache={};parity={}
for label,cache in [('primary',plan['cache_run']),('sensitivity',str(ROOT/'outputs'/protocol['sensitivity_cache_run']))]:
    folder=out/label;folder.mkdir()
    batch=VerificationBatch(folder,cache,plan['initialization_run'],plan['stress_run'])
    # Guard the established-baseline wrapper as well as all inherited sources.
    batch.source_identity[str(ROOT/'scripts/run_outer_baseline.py')]=digest(ROOT/'scripts/run_outer_baseline.py')
    (folder/'source_identity.json').write_text(json.dumps(batch.source_identity,indent=2)+'\n')
    groups={}
    for method in ['B3','B4','B5','B6']:
        if label=='primary':groups[method]=baseline['complete_selected'][method]
        else:
            conf=baseline['complete_selected'][method][0]['config']
            groups[method]=[batch.baseline(conf,method,c) for c in batch.cases]
    groups['P']=candidate['complete_selected'] if label=='primary' else [batch.run(selected['config'],'P',c) for c in batch.cases]
    for method in ['P_without_motion','P_time_only','P_without_decay','P_without_anchor']:
        conf=copy.deepcopy(selected['config']);conf['method']=method
        groups[method]=[batch.run(conf,method,c) for c in batch.cases]
    for r,s in zip(groups['B6'],groups['P_without_motion']):
        x=np.loadtxt(Path(r['backend']['output'])/'trajectory.csv',delimiter=',',skiprows=1)
        y=np.loadtxt(Path(s['backend']['output'])/'trajectory.csv',delimiter=',',skiprows=1)
        parity[label+'_B6_without_motion_'+r['case']]=bool(np.array_equal(x,y,equal_nan=True))
    if label=='primary':
        prior=json.loads((ROOT/'outputs'/plan['parent_candidate_run']/'candidate_screen.json').read_text())
        for r,s in zip(prior['complete_selected'],groups['P_without_anchor']):
            if r['case']!=s['case']:raise ValueError('ablation pairing differs')
            x=np.loadtxt(Path(r['backend']['output'])/'trajectory.csv',delimiter=',',skiprows=1)
            y=np.loadtxt(Path(s['backend']['output'])/'trajectory.csv',delimiter=',',skiprows=1)
            parity[label+'_r02_without_anchor_'+r['case']]=bool(np.array_equal(x,y,equal_nan=True))
    tables[label]=[summarize(n,r) for n,r in groups.items()]
    records_by_cache[label]=groups
    (folder/'verification_table.json').write_text(json.dumps(tables[label],indent=2)+'\n')

checks={};gains=[]
for label,table in tables.items():
    rows={r['name']:r for r in table};proposed=rows['P']
    controls=[rows[m] for m in ['B4','B5','B6'] if rows[m]['eligible']]
    best=min(controls,key=lambda r:r['primary_macro_RMSE_m']) if controls else None
    gain=best['primary_macro_RMSE_m']-proposed['primary_macro_RMSE_m'] if best and proposed['valid'] else None
    relative=gain/best['primary_macro_RMSE_m'] if gain is not None else None
    checks[label]={'strongest_eligible_fixed_control':best,'absolute_gain_m':gain,'relative_gain':relative,
        'gain_normal_coverage_gate':bool(proposed['eligible'] and gain is not None and gain>=.1 and relative>=.03),
        'time_only_advantage_m':rows['P_time_only']['primary_macro_RMSE_m']-proposed['primary_macro_RMSE_m'] if rows['P_time_only']['valid'] and proposed['valid'] else None,
        'anchor_advantage_m':rows['P_without_anchor']['primary_macro_RMSE_m']-proposed['primary_macro_RMSE_m'] if rows['P_without_anchor']['valid'] and proposed['valid'] else None}
    if gain is not None:gains.append(gain)
stable=bool(len(gains)==2 and min(gains)>abs(gains[0]-gains[1]))
attributed=all(c['time_only_advantage_m'] is not None and c['time_only_advantage_m']>1e-9 and c['anchor_advantage_m'] is not None and c['anchor_advantage_m']>1e-9 for c in checks.values())
result={'candidate_source':str(source),'candidate_SHA':digest(source/'candidate_screen.json'),'protocol':protocol,'shared_normal_cap_m':cap,
    'fixed_parameters_no_retuning':True,'heldout_opened':False,'tables':tables,'records':records_by_cache,'checks':checks,
    'numerical_effect_exceeds_two_cache_variation':stable,'incremental_attribution_gate':attributed,'exact_ablation_parity_checks':parity,
    'quantitative_development_gate':bool(stable and attributed and all(parity.values()) and all(c['gain_normal_coverage_gate'] for c in checks.values())),
    'scientific_freeze_allowed':False,'remaining_review':'inspect exact parity, per-event failures and literature distinction; no automatic freeze'}
(out/'final_verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['records','protocol']}),flush=True)
