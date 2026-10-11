"""Generate manuscript table cells and exact claim bindings from retained evidence."""
import argparse,hashlib,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];p=argparse.ArgumentParser();p.add_argument('version');a=p.parse_args();version=Path(a.version);source=ROOT/'artifacts/r2/S3/summary_table.json';rows=json.loads(source.read_text());order=['B2','B3','B4','B5','B6','NIS0','NIS1','NIS2','Clock2','Clock5','Clock10','Clock15','Clock30','Clock60','Clock90','P','P_without_motion','P_without_anchor','P_without_decay']
names={'B2':'LIO only','B3':'Direct fusion','B4':'NIS100','B5':'Huber2.5','B6':'Availability B6','NIS0':'NIS11.3449','NIS1':'NIS16.2662','NIS2':'NIS30','P':'P-r03','P_without_motion':'P-no-motion','P_without_anchor':'P-no-anchor','P_without_decay':'P-no-decay'}
def get(cache,method):return next(r for r in rows if r['cache']==cache and r['method']==method)
def fmt(x):return 'C180' if x is None else f'{x:.3f}'
def label(method):return names.get(method,method)
cells=[];tex=[]
tex+=['\\begin{table*}[t]\\centering\\small','\\caption{Complete primary building00 comparison, all 19 policies. RMSE is horizontal, meters; clean delay is maximum actual-update delay across three events, seconds. Exposure is accepted injected rows out of270. Q indicates both the declared natural-cost and inclusive15-s clean service gates. C180 is right-censored admission, not zero latency. All windows have complete expected-grid coverage.}\\label{tab:primary}','\\begin{tabular}{lrrrrrrc}\\toprule','Policy & Natural & Clean delay & Clean90 & Bias90 & Bias180 & Exposure & Q\\\\\\midrule']
for method in order:
    r=get('primary',method);fields=['natural_RMSE_m','clean_latency_max_s','clean_RMSE_90_m','bias_RMSE_90_m','bias_RMSE_180_m','bias_accepted_rows','service_qualified'];values=[fmt(r[k]) for k in fields[:5]]+[str(r['bias_accepted_rows'])+'/270','yes' if r['service_qualified'] else 'no'];tex.append(label(method)+' & '+' & '.join(values)+' \\\\')
    for field,rendered in zip(fields,values):cells.append({'table':'primary','method':method,'cache':'primary','field':field,'raw_value':r[field],'rendered':rendered,'summary_source':str(source),'summary_SHA':hashlib.sha256(source.read_bytes()).hexdigest()})
tex+=['\\bottomrule\\end{tabular}\\end{table*}']
tex+=['\\begin{table*}[t]\\centering\\small','\\caption{All controls and ablations on the second building cache and already-seen parking00. Both use the same19 policies and complete coverage. Latencies match Table~\\ref{tab:primary}; Q is independently calculated against each cache/route natural cap. Neither column is a new independent R2 test.}\\label{tab:other}','\\begin{tabular}{lrrrrrrrr}\\toprule',' & \\multicolumn{4}{c}{Building00 sensitivity cache} & \\multicolumn{4}{c}{Parking00 seen historical route}\\\\','Policy & Natural & Bias90 & Exposure & Q & Natural & Bias90 & Exposure & Q\\\\\\midrule']
for method in order:
    values=[]
    for cache in ['sensitivity','parking']:
        r=get(cache,method);fields=['natural_RMSE_m','bias_RMSE_90_m','bias_accepted_rows','service_qualified'];v=[fmt(r[fields[0]]),fmt(r[fields[1]]),str(r['bias_accepted_rows'])+'/270','yes' if r['service_qualified'] else 'no'];values+=v
        for field,rendered in zip(fields,v):cells.append({'table':'other','method':method,'cache':cache,'field':field,'raw_value':r[field],'rendered':rendered,'summary_source':str(source),'summary_SHA':hashlib.sha256(source.read_bytes()).hexdigest()})
    tex.append(label(method)+' & '+' & '.join(values)+' \\\\')
tex+=['\\bottomrule\\end{tabular}\\end{table*}']
(version/'generated_tables.tex').write_text('\n'.join(tex)+'\n');(version/'table_cell_bindings.json').write_text(json.dumps(cells,indent=2)+'\n');figures=version/'figures';figures.mkdir(exist_ok=False)
for name in ['latency_error_tradeoff','first_registered_bias_event']:
    for suffix in ['pdf','svg','png']:(figures/(name+'.'+suffix)).write_bytes((ROOT/'artifacts/r2/S3'/(name+'.'+suffix)).read_bytes())
(version/'figure_sources.json').write_text(json.dumps({'plot_script':'experiments/r2/make_figures.py','source_point_files':['artifacts/r2/S3/tradeoff_points.csv','artifacts/r2/S3/representative_event_points.csv'],'source_manifest':'artifacts/r2/S3/figure_manifest.json','full_summary_SHA':hashlib.sha256(source.read_bytes()).hexdigest()},indent=2)+'\n')
OUT=Path(os.environ['LIO_GINS_RUN_DIR']);(OUT/'table_generation.json').write_text(json.dumps({'version':str(version),'table_cells':len(cells),'table_source_SHA':hashlib.sha256(source.read_bytes()).hexdigest()},indent=2)+'\n');print(json.dumps({'generated_cells':len(cells),'version':str(version)}))
