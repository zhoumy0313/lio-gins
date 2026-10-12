"""Frozen descriptive cross-route comparisons; no fit, selection or retuning."""
import csv,gzip,hashlib,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=Path(os.environ['LIO_GINS_RUN_DIR'])
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 registry=json.loads((ROOT/'artifacts/s9/COLLECTIVE_FREEZE.json').read_text());state=json.loads((ROOT/'docs/research_s9/STATE.json').read_text());summary=[];sources={};events=[];comparisons=[];route_reports=[]
 for item in registry['included_routes']:
  route=item['sequence'];a=Path(state['routes'][route]['analysis_run']);s=a/'summary_table.json';sources[route]={'path':str(s),'SHA':sha(s)};rows=json.loads(s.read_text());all_events=json.loads((a/'event_results.json').read_text());assert len(rows)==19 and len(all_events)==152 and {r['cache'] for r in rows}=={route};summary.extend(rows);events.extend(all_events)
  by={r['method']:r for r in rows};p=by['P'];p_events=next(r for r in all_events if r['method']=='P' and r['case']=='loss30_bias10')['events']
  eligible=[r for r in rows if r['method']!='P' and r['service_qualified']];best=min(eligible,key=lambda r:r['bias_RMSE_90_m']) if eligible else None
  for method in by:
   control=by[method];ce=next(r for r in all_events if r['method']==method and r['case']=='loss30_bias10')['events'];delta=p['bias_RMSE_90_m']-control['bias_RMSE_90_m'] if p['bias_RMSE_90_m'] is not None and control['bias_RMSE_90_m'] is not None else None
   e_delta=[pe['post_return']['90']['horizontal_RMSE_m']-oe['post_return']['90']['horizontal_RMSE_m'] if pe['post_return']['90']['horizontal_RMSE_m'] is not None and oe['post_return']['90']['horizontal_RMSE_m'] is not None else None for pe,oe in zip(p_events,ce)]
   comparisons.append({'route':route,'control':method,'P_minus_control_bias90_m':delta,'P_minus_control_bias180_m':p['bias_RMSE_180_m']-control['bias_RMSE_180_m'] if p['bias_RMSE_180_m'] is not None and control['bias_RMSE_180_m'] is not None else None,'P_minus_control_natural_m':p['natural_RMSE_m']-control['natural_RMSE_m'] if p['natural_RMSE_m'] is not None and control['natural_RMSE_m'] is not None else None,'P_clean_max_s':p['clean_latency_max_s'],'control_clean_max_s':control['clean_latency_max_s'],'P_service_qualified':p['service_qualified'],'control_service_qualified':control['service_qualified'],'event_delta_bias90_m':e_delta,'improved_events':sum(v is not None and v<-1e-6 for v in e_delta),'worse_events':sum(v is not None and v>1e-6 for v in e_delta),'numerical_direction':'lower' if delta is not None and delta<-1e-6 else 'higher' if delta is not None and delta>1e-6 else 'equal_or_unavailable','control_summary_SHA':sha(s)})
  route_reports.append({'route':route,'P':p,'strongest_eligible_control':best,'joint_directional_error_reduction':bool(p['service_qualified'] and best and p['bias_RMSE_90_m']<best['bias_RMSE_90_m']-1e-6),'material_attribution_review_required':True,'all19_retained':True,'event_count':sum(len(r['events']) for r in all_events)})
 macro=[]
 for method in ['Clock2','P_without_anchor','NIS0','NIS1','NIS2','B4','B5','B6','Clock60','Clock90','P_without_decay']:
  r=[c for c in comparisons if c['control']==method];d=[c['P_minus_control_bias90_m'] for c in r];macro.append({'control':method,'all_registered_included_routes':len(r),'equal_weight_route_macro_P_minus_control_bias90_m':sum(d)/len(d) if d and all(v is not None for v in d) else None,'all_route_signs':[{'route':c['route'],'sign':c['numerical_direction'],'delta_m':c['P_minus_control_bias90_m']} for c in r],'no_successful_intersection':True})
 result={'route_reports':route_reports,'pairwise_comparisons':comparisons,'new_route_equal_weight_macro':macro,'summary_sources':sources,'prospective_routes':[i['sequence'] for i in registry['included_routes']],'technical_exclusions':registry['technical_exclusions'],'parameter_changes':0,'novelty_supported':False,'analysis_definition':'exact inherited S8 evaluator; new routes frozen jointly before all openings; descriptive signs, not significance or field fault probability'}
 (OUT/'cross_route_judgment.json').write_text(json.dumps(result,indent=2)+'\n');(OUT/'summary_table.json').write_text(json.dumps(summary,indent=2)+'\n')
 with (OUT/'summary_table.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
 with gzip.open(OUT/'all_event_results.json.gz','wt') as f:json.dump(events,f,indent=2)
 print(json.dumps({'routes':len(route_reports),'method_summaries':len(summary),'events':sum(len(r['events']) for r in events),'all19_retained':True}))
if __name__=='__main__':main()
