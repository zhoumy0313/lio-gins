#!/usr/bin/env python3
"""Offline frozen-matrix report: complete rows, failures and declared cost gate."""
import argparse,csv,json,os,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.adapters.research_access import sha,verify_access
p=argparse.ArgumentParser();p.add_argument('heldout_run');a=p.parse_args()
folder=Path(a.heldout_run).resolve();matrixpath=folder/'heldout_matrix.json';m=json.loads(matrixpath.read_text());freeze=verify_access('parking00','heldout',m['freeze_directory']);out=Path(os.environ['LIO_GINS_RUN_DIR'])
methods=m['complete_methods'];table=[];allcases=[];events=[];sources={str(matrixpath):sha(matrixpath)}
primary_cases=['cluster_jump10','loss30_normal','loss30_bias10']
for name,records in methods.items():
    indexed={r['case']:r for r in records}
    valid=len(records)==8 and all(r['backend']['exit_code']==0 and r['metrics'] and r['metrics']['metrics']['coverage']>=.99 for r in records)
    natural=indexed['natural']['metrics']['metrics']['horizontal_rmse_m'] if indexed['natural']['metrics'] else None
    target=float(np.mean([indexed[c]['metrics']['event_macro_RMSE_m'] for c in primary_cases])) if valid else None
    table.append({'method':name,'natural_RMSE_m':natural,'primary_macro_RMSE_m':target,'all_cases_valid':bool(valid)})
    for r in records:
        metric=r['metrics'];allcases.append({'method':name,'case':r['case'],'backend_exit':r['backend']['exit_code'],'evaluation_run':r['evaluation'],'coverage':metric['metrics']['coverage'] if metric else None,'whole_route_horizontal_RMSE_m':metric['metrics']['horizontal_rmse_m'] if metric else None,'event_macro_RMSE_m':metric['event_macro_RMSE_m'] if metric else None,'P95_m':metric['metrics']['horizontal_p95_m'] if metric else None,'maximum_m':metric['metrics']['horizontal_max_m'] if metric else None,'rejection_fraction':metric['GNSS_rejection_fraction'] if metric else None,'max_update_correction_m':metric['update_correction_max_m'] if metric else None,'backend_run':r['backend']['output']})
        if metric:
            sources[str(Path(r['evaluation'])/'metrics.json')]=sha(Path(r['evaluation'])/'metrics.json')
            for i,e in enumerate(metric['events']):events.append({'method':name,'case':r['case'],'event_index':i,'fault_start_sow':e['event']['fault_start_sow'],'recovery_start_sow':e['event']['recovery_start_sow'],'horizontal_RMSE_m':e['metrics']['horizontal_rmse_m'],'P95_m':e['metrics']['horizontal_p95_m'],'maximum_m':e['metrics']['horizontal_max_m'],'coverage':e['metrics']['coverage'],'MAE_integral_m_s':e['metrics']['horizontal_MAE_integral_m_s'],'recovery_time_s':e['metrics']['recovery_time_s'],'recovered_within_timeout':e['metrics']['recovered_within_timeout'],'evaluation_run':r['evaluation']})

rows={r['method']:r for r in table};robust=[rows[n] for n in ['B4','B5','B6'] if rows[n]['all_cases_valid']]
best_normal=min((r['natural_RMSE_m'] for r in robust),default=None)
cap=best_normal+max(.02*best_normal,.05) if best_normal is not None else None
eligible=[r for r in robust if r['natural_RMSE_m']<=cap]
control=min(eligible,key=lambda r:r['primary_macro_RMSE_m']) if eligible else None
proposed=rows['P'];gain=control['primary_macro_RMSE_m']-proposed['primary_macro_RMSE_m'] if control and proposed['all_cases_valid'] else None
relative=gain/control['primary_macro_RMSE_m'] if gain is not None else None
normal_ok=bool(cap is not None and proposed['all_cases_valid'] and proposed['natural_RMSE_m']<=cap)
positive=bool(normal_ok and gain is not None and gain>0)
conservative=bool(positive and gain>=.1 and relative>=.03)
attribution={n:rows[n]['primary_macro_RMSE_m']-proposed['primary_macro_RMSE_m'] if proposed['all_cases_valid'] and rows[n]['all_cases_valid'] else None for n in ['P_without_motion','P_time_only','P_without_decay','P_without_anchor']}
nativepath=Path(m['native_evaluation'])/'metrics.json';native=json.loads(nativepath.read_text());sources[str(nativepath)]=sha(nativepath)
cachepath=Path(m['cache'])/'cache_identity.json';cache=json.loads(cachepath.read_text());sources[str(cachepath)]=sha(cachepath)
timing=[]
for name,records in methods.items():
    r=next(r for r in records if r['case']=='natural');path=Path(r['backend']['output'])/'backend_identity.json'
    if path.exists():
        identity=json.loads(path.read_text());sources[str(path)]=sha(path)
        timing.append({'method':name,'cached_replay_wall_s':identity['replay_wall_seconds'],'expected_grid_rows':identity['outputs_expected'],'timing_scope':identity['timing_scope'],'backend_run':r['backend']['output']})

def csvfile(name,records):
    if not records:return
    with (out/name).open('w') as f:w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
for name,records in [('all_method_summary.csv',table),('all_80_cases.csv',allcases),('all_210_events.csv',events),('separate_cached_timing.csv',timing)]:csvfile(name,records)
result={'sequence':'parking00','role':'heldout','freeze_id':freeze['freeze_id'],'retuned':False,'parent_run':str(folder),'table':table,'shared_normal_cap_m':cap,'strongest_eligible_fixed_control':control,'candidate_absolute_gain_m':gain,'candidate_relative_gain':relative,'candidate_normal_cost_passed':normal_ok,'positive_paired_target_gain_with_normal_cost':positive,'same_conservative_3percent_0p1m_gate':conservative,'ablation_target_advantages_m':attribution,'all_cases':allcases,'all_events':events,'B0_B1_natural':native,'frontend_identity_and_timing':cache,'cached_backend_timing':timing,'input_SHA256':sources,'limits':['one heldout route; three within-route events are not independent routes','same-input frontend numerical variation remains unresolved','MM/INS reference shares AT128','controlled first reference epoch and common initial-position condition, not no-prior or absolute WGS84 accuracy','artificial errors may cancel real F9P errors; all categories and directions retained','cached timings exclude frontend and are not field online latency'],'novelty_supported':False,'formal_submission_ready':False}
(out/'heldout_summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['all_cases','all_events','B0_B1_natural','frontend_identity_and_timing','cached_backend_timing','input_SHA256','limits']}))
