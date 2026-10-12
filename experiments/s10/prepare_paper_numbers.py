"""Bind manuscript macros/tables to independently audited CSV rows, never inverse data."""
import csv,json,sys
from pathlib import Path
from common import ROOT,sha,METHODS
version=Path(sys.argv[1]).resolve();assert version.is_relative_to(ROOT/'paper/versions')
bindings={}
def select(file,where):
 rows=list(csv.DictReader((ROOT/file).open()));selected=[x for x in rows if all(x[k]==str(v) for k,v in where.items())];assert len(selected)==1
 return selected[0]
def bind(key,file,where,field,fmt='.3f',operation='number'):
 row=select(file,where);raw=row[field]
 if operation=='max_json':
  xs=json.loads(raw);value=None if any(x is None for x in xs) else max(xs)
 elif operation=='percent':value=float(raw)*100
 elif operation=='bool':value='Y' if raw=='True' else 'N'
 else:value=None if raw=='' else float(raw)
 shown='C180' if value is None else value if isinstance(value,str) else format(value,fmt)
 assert key not in bindings
 bindings[key]={'source':file,'source_SHA':sha(ROOT/file),'row':where,'field':field,'operation':operation,'raw':raw,'display':shown,'format':fmt}
 return r'\val{'+key+'}'
matrix='artifacts/s10/evidence_matrix.csv';events='artifacts/s10/independent_event_table.csv';attrs='artifacts/s10/event_attribution.csv'
def M(key,route,method,field,case='loss30_bias3',**kw):return bind(key,matrix,dict(route=route,method=method,case=case),field,**kw)
def E(key,event,method,field,**kw):return bind(key,events,dict(route='street00',method=method,case='loss30_bias3',event=event),field,**kw)
def A(key,route,event,field,case='loss30_bias3',**kw):return bind(key,attrs,dict(route=route,case=case,event=event),field,**kw)
labels={'B2':'LIO only','B3':'Direct KF','B4':'NIS100','B5':'Huber2.5','B6':'Fixed2','P':'P-r03','P_without_anchor':'No anchor','P_without_motion':'No motion','P_without_decay':'No decay','NIS0':'NIS11.3449','NIS1':'NIS16.2662','NIS2':'NIS30'}
rows=[]
for m in METHODS:
 k=m.replace('_','')
 cells=[labels.get(m,m),M(k+'street90','street00',m,'RMSE_90_macro_m'),M(k+'street180','street00',m,'RMSE_180_macro_m'),M(k+'clean','street00',m,'clean_admit_each_s',fmt='.0f',operation='max_json'),M(k+'accepted','street00',m,'injected_accepted',fmt='.0f'),M(k+'qualified','street00',m,'service_cost_qualified',operation='bool')]
 rows.append(' & '.join(cells)+r'\\')
(version/'street_table.tex').write_text(r'\begin{tabular}{lrrrrc}\toprule'+'\n'+r'Policy & $R_{90}$ & $R_{180}$ & $T_c$ & $n_b$ & Q\\\midrule'+'\n'+'\n'.join(rows)+'\n'+r'\bottomrule\end{tabular}'+'\n')
routes=['building00','parking00','building01','street00','playground00','building02'];rows=[]
for route in routes:
 cells=[route,M(route+'P90',route,'P','RMSE_90_macro_m'),M(route+'N90',route,'P_without_anchor','RMSE_90_macro_m'),M(route+'NIS90',route,'NIS0','RMSE_90_macro_m'),M(route+'Clock90',route,'Clock90','RMSE_90_macro_m'),M(route+'natural',route,'P','natural_RMSE_m')+'/'+M(route+'cap',route,'P','natural_cap_m'),M(route+'clean',route,'P','clean_admit_each_s',fmt='.0f',operation='max_json'),M(route+'qualified',route,'P','service_cost_qualified',operation='bool')]
 rows.append(' & '.join(cells)+r'\\')
(version/'routes_table.tex').write_text(r'\begin{tabular}{lrrrrrcc}\toprule'+'\n'+r'Route & P & No anchor & Strict NIS0 & Clock90 & P natural / cap & $T_c$ & Q\\\midrule'+'\n'+'\n'.join(rows)+'\n'+r'\bottomrule\end{tabular}'+'\n')
rows=[]
for e in range(3):
 cells=[f'{e} ({["N","E","NE"][e]})',E(f'event{e}P',e,'P','RMSE_90_m'),E(f'event{e}N',e,'P_without_anchor','RMSE_90_m'),E(f'event{e}NIS',e,'NIS0','RMSE_90_m'),E(f'event{e}delay',e,'P','T_admit_s',fmt='.0f'),E(f'event{e}accept',e,'P','injected_accepted',fmt='.0f'),A(f'event{e}extra','street00',e,'extra_rejected_vs_no_anchor',fmt='.0f'),A(f'event{e}nisextra','street00',e,'extra_rejected_and_NIS0_accepted',fmt='.0f')]
 rows.append(' & '.join(cells)+r'\\')
(version/'event_table.tex').write_text(r'\begin{tabular}{lrrrrrrr}\toprule'+'\n'+r'Event & $R_P$ & $R_{\rm no\ anchor}$ & $R_{\rm NIS0}$ & $T_b$ & $n_P$ & Extra & NIS-extra\\\midrule'+'\n'+'\n'.join(rows)+'\n'+r'\bottomrule\end{tabular}'+'\n')
M('streetImprovement','street00','P','P_vs_no_anchor_fraction',fmt='.2f',operation='percent')
M('streetPNatural','street00','P','natural_RMSE_m');M('streetPCap','street00','P','natural_cap_m')
M('street10P','street00','P','RMSE_90_macro_m',case='loss30_bias10',fmt='.6f');M('street10NIS','street00','NIS0','RMSE_90_macro_m',case='loss30_bias10',fmt='.6f')
A('streetPrior0','street00',0,'before_fault_P_no_anchor_position_difference_h_m',fmt='.0f');A('streetPrior1','street00',1,'before_fault_P_no_anchor_position_difference_h_m',fmt='.6f');A('streetNeutralDelta','street00',2,'P_minus_no_anchor_RMSE_90_m',fmt='.6f')
A('streetVeto0','street00',0,'direct_anchor_veto_rows',fmt='.0f');A('streetShort0','street00',0,'veto_with_short_window_good_rows',fmt='.0f');A('streetVeto1','street00',1,'direct_anchor_veto_rows',fmt='.0f')
A('building02Prior','building02',1,'before_fault_P_no_anchor_position_difference_h_m',fmt='.3f');A('building02Motion','building02',1,'offline_relative_LIO_error_max_m',fmt='.3f')
A('playCleanPrior','playground00',1,'before_fault_P_no_anchor_position_difference_h_m',case='loss30_normal',fmt='.0f');A('playCleanMotion','playground00',1,'offline_relative_LIO_error_max_m',case='loss30_normal',fmt='.3f');A('playCleanPenalty','playground00',1,'P_minus_no_anchor_RMSE_90_m',case='loss30_normal',fmt='.3f')
A('buildCleanPrior','building02',2,'before_fault_P_no_anchor_position_difference_h_m',case='loss30_normal',fmt='.0f');A('buildCleanMotion','building02',2,'offline_relative_LIO_error_max_m',case='loss30_normal',fmt='.3f');A('buildCleanPenalty','building02',2,'P_minus_no_anchor_RMSE_90_m',case='loss30_normal',fmt='.3f')
for method in ['P','P_without_anchor']:M('repeat'+method.replace('_',''),'building00_repeat',method,'RMSE_90_macro_m')
for route in routes+['building00_repeat']:
 file='artifacts/s10/injection_bias3_audit.csv';where=dict(route=route,case='loss30_bias3');rows=[x for x in csv.DictReader((ROOT/file).open()) if all(x[k]==v for k,v in where.items())];assert len(rows)==3
 raw=sum(int(x['cancellation_rows']) for x in rows)
 bindings[route+'cancel']={'source':file,'source_SHA':sha(ROOT/file),'row':where,'field':'cancellation_rows','operation':'sum_three','raw':raw,'display':str(raw),'format':'.0f'}
for route in ['street00','playground00','building02']:
 file=f'artifacts/s9/{route}/C/native_KF_metrics.json';j=json.loads((ROOT/file).read_text())
 for field,fmt in [('horizontal_rmse_m','.3f'),('coverage','.6f')]:
  raw=j['metrics_10Hz'][field];bindings[route+'native'+field]={'source':file,'source_SHA':sha(ROOT/file),'pointer':['metrics_10Hz',field],'operation':'json_number','raw':raw,'display':format(raw,fmt),'format':fmt}
file='docs/research_r2/S3_report.md';assert '3.60128849' in (ROOT/file).read_text()
bindings['frontendRepeat']={'source':file,'source_SHA':sha(ROOT/file),'text_number':'3.60128849','operation':'text_number','raw':3.60128849,'display':'3.6013','format':'.4f'}
(version/'numbers.tex').write_text(r'\newcommand{\val}[1]{\csname S#1\endcsname}'+'\n'+''.join(r'\expandafter\def\csname S'+k+r'\endcsname{'+v['display']+'}\n' for k,v in bindings.items()))
(version/'numeric_bindings.json').write_text(json.dumps(bindings,indent=2)+'\n')
(version/'figure_sources.json').write_text(json.dumps({'manifest_path':'artifacts/s10/figures/figure_manifest.json','manifest_SHA':sha(ROOT/'artifacts/s10/figures/figure_manifest.json'),'copied_vector_SHA':{str(p.relative_to(version)):sha(p) for p in (version/'figures').glob('*')}},indent=2)+'\n')
print(json.dumps({'bound_cells':len(bindings),'all19_street':len(METHODS),'all6routes':True,'same_bag_repeat_separate':True}))
