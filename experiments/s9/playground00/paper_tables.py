"""All 19 independent controls plus explicitly labeled cross-route evidence."""
import json,sys,hashlib,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(os.environ['LIO_GINS_RUN_DIR']);version=Path(sys.argv[1]);source=Path(sys.argv[2])/'summary_table.json';old=ROOT/'artifacts/r2/S3/summary_table.json';rows=json.loads(source.read_text())+json.loads(old.read_text());order=['B2','B3','B4','B5','B6','NIS0','NIS1','NIS2','Clock2','Clock5','Clock10','Clock15','Clock30','Clock60','Clock90','P','P_without_motion','P_without_anchor','P_without_decay'];names={'B2':'LIO only','B3':'Direct fusion','B4':'NIS100','B5':'Huber2.5','B6':'Availability B6','NIS0':'NIS11.3449','NIS1':'NIS16.2662','NIS2':'NIS30','P':'P-r03','P_without_motion':'P-no-motion','P_without_anchor':'P-no-anchor','P_without_decay':'P-no-decay'};cells=[];tex=[]
def get(cache,method):return next(r for r in rows if r['cache']==cache and r['method']==method)
def fmt(x):return 'C180' if x is None else f'{x:.3f}'
def bind(table,cache,method,fields,values):
 s=source if cache=='playground00' else old
 for field,value in zip(fields,values):cells.append({'table':table,'cache':cache,'method':method,'field':field,'raw_value':get(cache,method)[field],'rendered':value,'summary_source':str(s),'summary_SHA':hashlib.sha256(s.read_bytes()).hexdigest()})
tex+=['\\begin{table*}[t]\\centering\\small','\\caption{Complete prospective playground00 matrix: all19 fixed named policies. Horizontal RMSE is meters; clean delay is the maximum of three actual-update measurement delays, seconds. Exposure is accepted/exposed artificial10-m rows. Q requires the frozen15-s clean deadline, natural-cost cap and complete coverage. C180 is right-censored admission, not zero delay. No new-route tuning.}\\label{tab:primary}','\\begin{tabular}{lrrrrrrc}\\toprule','Policy & Natural & Clean delay & Clean90 & Bias90 & Bias180 & Exposure & Q\\\\\\midrule']
for m in order:
 r=get('playground00',m);fields=['natural_RMSE_m','clean_latency_max_s','clean_RMSE_90_m','bias_RMSE_90_m','bias_RMSE_180_m','bias_accepted_rows','service_qualified'];v=[fmt(r[k]) for k in fields[:5]]+[str(r['bias_accepted_rows'])+'/'+str(r['bias_exposed_rows']),'yes' if r['service_qualified'] else 'no'];tex.append(names.get(m,m)+' & '+' & '.join(v)+' \\\\');bind('independent','playground00',m,fields,v)
tex+=['\\bottomrule\\end{tabular}\\end{table*}']
tex+=['\\begin{table*}[t]\\centering\\small','\\caption{Cross-route comparison with explicit data roles. All19 policies remain visible. Columns give clean actual-update delay(s), biased post90 horizontal RMSE(m), and joint eligibility Q. building00 is seen development; parking00 is seen retrospective; playground00 is the new prospective test. The second building cache is retained sensitivity, not another route.}\\label{tab:other}','\\begin{tabular}{lrrrrrrrrr}\\toprule',' & \\multicolumn{3}{c}{Building00: seen development} & \\multicolumn{3}{c}{Parking00: seen retrospective} & \\multicolumn{3}{c}{Building01: prospective test}\\\\','Policy & Delay & Bias90 & Q & Delay & Bias90 & Q & Delay & Bias90 & Q\\\\\\midrule']
for m in order:
 v=[]
 for cache in ['primary','parking','playground00']:
  r=get(cache,m);fields=['clean_latency_max_s','bias_RMSE_90_m','service_qualified'];part=[fmt(r[fields[0]]),fmt(r[fields[1]]),'yes' if r['service_qualified'] else 'no'];v+=part;bind('cross_route',cache,m,fields,part)
 tex.append(names.get(m,m)+' & '+' & '.join(v)+' \\\\')
tex+=['\\bottomrule\\end{tabular}\\end{table*}'];(version/'generated_tables.tex').write_text('\n'.join(tex)+'\n');(version/'table_cell_bindings.json').write_text(json.dumps(cells,indent=2)+'\n');(OUT/'table_audit.json').write_text(json.dumps({'cells':len(cells),'policies_each_table':19,'prospective_pairs':152,'summary_SHA':hashlib.sha256(source.read_bytes()).hexdigest()},indent=2)+'\n');print(json.dumps({'cells':len(cells)}))
