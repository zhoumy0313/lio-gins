"""All nineteen fixed policies across every registered route; exact numeric binding."""
import hashlib,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=Path(os.environ['LIO_GINS_RUN_DIR']);version=Path(sys.argv[1]);state=json.loads((ROOT/'docs/research_s9/STATE.json').read_text())
order=['B2','B3','B4','B5','B6','NIS0','NIS1','NIS2','Clock2','Clock5','Clock10','Clock15','Clock30','Clock60','Clock90','P','P_without_motion','P_without_anchor','P_without_decay']
names={'B2':'LIO only','B3':'Direct fusion','B4':'NIS100','B5':'Huber2.5','B6':'Availability B6','NIS0':'NIS11.3449','NIS1':'NIS16.2662','NIS2':'NIS30','P':'P-r03','P_without_motion':'P-no-motion','P_without_anchor':'P-no-anchor','P_without_decay':'P-no-decay'}
old=ROOT/'artifacts/r2/S3/summary_table.json';s8=ROOT/'artifacts/s8/C/summary_table.json';sources={'primary':old,'parking':old,'building01':s8};sources.update({r:Path(state['routes'][r]['analysis_run'])/'summary_table.json' for r in state['included_routes']});rows={k:[r for r in json.loads(p.read_text()) if r['cache']==k] for k,p in sources.items()};cells=[]
def fmt(v):return 'C180' if v is None else f'{v:.3f}'
def value(table,cache,m,field):
 row=next(r for r in rows[cache] if r['method']==m);v=row[field];render=('yes' if v else 'no') if field=='service_qualified' else str(v)+'/'+str(row['bias_exposed_rows']) if field=='bias_accepted_rows' else fmt(v);p=sources[cache];cells.append({'table':table,'cache':cache,'method':m,'field':field,'raw_value':v,'rendered':render,'summary_source':str(p),'summary_SHA':hashlib.sha256(p.read_bytes()).hexdigest()});return render
tex=[r'\begin{table*}[t]\centering\small',r'\caption{All nineteen frozen policies: biased-return 90-s horizontal RMSE (m), equal-weight mean over all three fixed events. Building00/parking00 are seen; building01 was prospective in S8 and already seen before S9. The other columns are S9 prospective routes. No policy or unfavorable route is removed. Full natural, latency, exposure and extended-window records accompany the paper.}\label{tab:allroutes}',r'\begin{tabular}{l'+'r'*len(sources)+r'}\toprule','Policy & '+' & '.join({'primary':'Building00','parking':'Parking00','building01':'Building01'}.get(k,k.capitalize()) for k in sources)+r' \\\midrule']
for m in order:tex.append(names.get(m,m)+' & '+' & '.join(value('cross_route_bias90',k,m,'bias_RMSE_90_m') for k in sources)+r' \\')
tex+=[r'\bottomrule\end{tabular}\end{table*}']
tex+=[r'\begin{table*}[t]\centering\small',r'\caption{Prespecified S9 mechanism contrasts, strong simple controls and strongest jointly qualified control per route. Natural is whole-route horizontal RMSE; Clean is maximum actual clean GNSS measurement-time admission delay (s). Bias90/180 are matched macro RMSE (m). Exposure is accepted/exposed injected rows. Q requires clean delay at most15 s, frozen natural-cost cap and full coverage. Qualification durations are not unconditional waiting times; all nineteen complete results are retained.}\label{tab:primary}',r'\begin{tabular}{llrrrrrc}\toprule',r'Route & Policy & Natural & Clean & Bias90 & Bias180 & Exposure & Q\\\midrule']
for cache in state['included_routes']:
 selected=['P','Clock2','P_without_anchor','NIS2','B5','Clock90']
 eligible=[row for row in rows[cache] if row['method']!='P' and row['service_qualified']]
 if eligible:
  best=min(eligible,key=lambda row:row['bias_RMSE_90_m'])['method']
  if best not in selected:selected.append(best)
 for m in selected:
  vals=[value('S9_cost_clock_and_ablation',cache,m,f) for f in ['natural_RMSE_m','clean_latency_max_s','bias_RMSE_90_m','bias_RMSE_180_m','bias_accepted_rows','service_qualified']]
  tex.append(cache+' & '+names.get(m,m)+' & '+' & '.join(vals)+r' \\')
tex+=[r'\bottomrule\end{tabular}\end{table*}'];(version/'generated_tables.tex').write_text('\n'.join(tex)+'\n');(version/'table_cell_bindings.json').write_text(json.dumps(cells,indent=2)+'\n');(OUT/'table_audit.json').write_text(json.dumps({'cells':len(cells),'all19_in_cross_route_table':True,'sources':{k:{'path':str(p),'SHA':hashlib.sha256(p.read_bytes()).hexdigest()} for k,p in sources.items()}},indent=2)+'\n');print(json.dumps({'cells':len(cells)}))
