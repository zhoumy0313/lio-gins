"""Transparent descriptive judgment, not a significance test or parameter search."""
import json,os,sys,hashlib,csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=Path(os.environ['LIO_GINS_RUN_DIR'])
def main():
 analysis=Path(sys.argv[1]);summary=json.loads((analysis/'summary_table.json').read_text());events=json.loads((analysis/'event_results.json').read_text());p=next(r for r in summary if r['method']=='P');eligible=[r for r in summary if r['method']!='P' and r['service_qualified']];strongest=min(eligible,key=lambda r:r['bias_RMSE_90_m']) if eligible else None
 margin=(strongest['bias_RMSE_90_m']-p['bias_RMSE_90_m']) if strongest else None
 qualified=p['service_qualified'] and p['coverage_eligible'];numeric_direction=qualified and margin is not None and margin>1e-6
 primary=next(r for r in events if r['method']=='P' and r['case']=='loss30_bias10');per_event=[]
 for e in primary['events']:
  comparisons=[]
  for other in eligible:
   oe=next(r for r in events if r['method']==other['method'] and r['case']=='loss30_bias10')['events'][e['event_index']]
   comparisons.append({'method':other['method'],'bias90_m':oe['post_return']['90']['horizontal_RMSE_m'],'P_minus_control_m':e['post_return']['90']['horizontal_RMSE_m']-oe['post_return']['90']['horizontal_RMSE_m']})
  per_event.append({'index':e['event_index'],'P_bias90_m':e['post_return']['90']['horizontal_RMSE_m'],'P_T_admit_s':e['T_admit_s'],'P_injected_accepted':e['injected_rows_accepted'],'comparisons':comparisons})
 sensitivities=[]
 for budget in [5,10,15,30,60,90]:
  pool=[r for r in summary if r['method']!='P' and r['normal_cost_eligible'] and r['coverage_eligible'] and r['clean_latency_max_s'] is not None and r['clean_latency_max_s']<=budget+1e-8]
  best=min(pool,key=lambda r:r['bias_RMSE_90_m']) if pool else None;sensitivities.append({'budget_s':budget,'P_qualified':p['normal_cost_eligible'] and p['coverage_eligible'] and p['clean_latency_max_s'] is not None and p['clean_latency_max_s']<=budget+1e-8,'best_control':best})
 categories=[]
 for method in sorted({r['method'] for r in events}):
  for row in [r for r in events if r['method']==method]:
   categories.append({'method':method,'case':row['case'],'whole_RMSE_m':row['whole']['horizontal_RMSE_m'],'P95_m':row['whole']['horizontal_P95_m'],'Max_m':row['whole']['horizontal_Max_m'],'coverage':row['whole']['coverage'],'post90_macro_m':sum(e['post_return']['90']['horizontal_RMSE_m'] for e in row['events'])/len(row['events']) if row['events'] and all(e['post_return']['90']['horizontal_RMSE_m'] is not None for e in row['events']) else None,'censored_events':sum(e['status']=='CENSORED' for e in row['events']),'backend_run':row['backend'],'config_SHA':row['provenance']['config_SHA'],'cache_SHA':row['provenance']['cache_SHA']})
 result={'P':p,'strongest_eligible_control_including_ablations':strongest,'all_eligible_controls':[r['method'] for r in eligible],'P_bias90_absolute_margin_m':margin,'numeric_direction_supported_at_fixed_gate':numeric_direction,'numerical_non_rounding_floor_m':1e-6,'material_and_attribution_review_required':True,'independent_case_specific_effect_supported':False,'novelty_supported':False,'method_revision_used':0,'interpretation':'automatic comparison only; final evidence report must assess scale, ablations and all fixed events without retuning','per_event':per_event,'budget_sensitivity':sensitivities,'analysis_SHA':hashlib.sha256((analysis/'event_results.json').read_bytes()).hexdigest()}
 (OUT/'scientific_judgment.json').write_text(json.dumps(result,indent=2)+'\n');(OUT/'category_table.json').write_text(json.dumps(categories,indent=2)+'\n')
 with (OUT/'category_table.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(categories[0]));w.writeheader();w.writerows(categories)
 print(json.dumps({'P_qualified':qualified,'best_control':strongest['method'] if strongest else None,'P_minus_best_m':-margin if margin is not None else None,'numeric_direction_supported':numeric_direction,'no_tuning':True}))
if __name__=='__main__':main()
