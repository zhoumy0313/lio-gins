#!/usr/bin/env python3
"""Offline development figures: all cases and fixed-cache verification, with SHA bindings."""
import argparse,csv,hashlib,json,os
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

p=argparse.ArgumentParser();p.add_argument('baseline_screen');p.add_argument('candidate_screen');p.add_argument('verification_run');a=p.parse_args()
out=Path(os.environ['LIO_GINS_RUN_DIR']);bpath=Path(a.baseline_screen)/'selected_baselines.json';cpath=Path(a.candidate_screen)/'candidate_screen.json';vpath=Path(a.verification_run)/'final_verification.json'
b=json.loads(bpath.read_text());c=json.loads(cpath.read_text());v=json.loads(vpath.read_text());sources={str(p.resolve()):hashlib.sha256(p.read_bytes()).hexdigest() for p in [bpath,cpath,vpath]}
def bind(p):sources[str(p.resolve())]=hashlib.sha256(p.read_bytes()).hexdigest()
def write_rows(name,rows):
    path=out/name
    with path.open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    return path

rows=[]
for label,table in v['tables'].items():
    rows += [{'cache':label,**r} for r in table]
tablepath=write_rows('all_fixed_method_summary.csv',rows)
fig,axes=plt.subplots(1,2,figsize=(12,4),layout='constrained')
for label,ax in zip(['primary','sensitivity'],axes):
    table=v['tables'][label];names=[r['name'] for r in table];target=[r['primary_macro_RMSE_m'] for r in table]
    ax.bar(names,target,color=['#5b7896']*4+['#cf762b']+['#87a4b8']*4)
    ax.set_title(label+' local-motion cache');ax.set_ylabel('Primary event macro horizontal RMSE (m)');ax.tick_params(axis='x',rotation=60);ax.grid(axis='y',alpha=.2)
fig.savefig(out/'fixed_cache_attribution.png',dpi=180);plt.close(fig)

cases=list(next(iter(v['records']['primary'].values())));case_ids=[r['case'] for r in cases]
fullrows=[]
for cache,groups in v['records'].items():
    for name,records in groups.items():
        for r in records:
            if r['metrics'] is None:continue
            metric=r['metrics'];fullrows.append({'cache':cache,'method':name,'case':r['case'],'whole_route_horizontal_RMSE_m':metric['metrics']['horizontal_rmse_m'],'event_macro_RMSE_m':metric['event_macro_RMSE_m'],'coverage':metric['metrics']['coverage'],'backend_run':r['backend']['output'],'evaluation_run':r['evaluation']})
            bind(Path(r['evaluation'])/'metrics.json')
casepath=write_rows('all_eight_cases.csv',fullrows)
fig,axes=plt.subplots(1,2,figsize=(12,4),layout='constrained')
for cache,ax in zip(['primary','sensitivity'],axes):
    for name in ['B4','B5','B6','P']:
        records=v['records'][cache][name]
        y=[r['metrics']['event_macro_RMSE_m'] for r in records if r['case']!='natural']
        ax.plot(np.arange(7),y,'o-',label=name)
    ax.set_xticks(np.arange(7),[i for i in case_ids if i!='natural'],rotation=60,ha='right');ax.set_ylabel('Event macro horizontal RMSE (m)');ax.set_title(cache+' — all seven stress categories');ax.grid(alpha=.2);ax.legend()
fig.savefig(out/'all_stress_categories.png',dpi=180);plt.close(fig)

records=v['records']['primary'];case='loss30_bias10'
pr=next(r for r in records['P'] if r['case']==case);br=next(r for r in records['B6'] if r['case']==case)
event=pr['metrics']['events'][0]['event'];start=event['recovery_start_sow'];lo=start-45;hi=start+100
fig,axes=plt.subplots(3,1,figsize=(10,7),sharex=True,layout='constrained');curve=[]
for method,r in [('B6',br),('P',pr)]:
    path=Path(r['evaluation'])/'per_epoch.csv';bind(path)
    arr=np.loadtxt(path,delimiter=',',skiprows=1);part=arr[(arr[:,0]>=lo)&(arr[:,0]<=hi)];error=np.sqrt(part[:,7]**2+part[:,8]**2)
    axes[0].plot(part[:,0]-start,error,label=method)
    curve += [{'method':method,'seconds_from_recovery':float(t-start),'horizontal_error_m':float(e)} for t,e in zip(part[:,0],error)]
write_rows('first_preregistered_bias10_event_errors.csv',curve)
logpath=Path(pr['backend']['output'])/'per_update.jsonl';bind(logpath);updates=[json.loads(l) for l in logpath.read_text().splitlines()];updates=[u for u in updates if lo<=u['measurement_sow']<=hi]
logrows=[{'seconds_from_recovery':u['measurement_sow']-start,'accepted':u['accepted'],'state':u['state'],'anchor_score':u.get('anchor_score'),'short_motion_score':u.get('motion_score'),'anchor_original_gnss_id_used':u.get('anchor_original_gnss_id_used')} for u in updates];write_rows('first_preregistered_bias10_event_admissions.csv',logrows)
t=[u['measurement_sow']-start for u in updates]
for key,title in [('motion_score','short motion score'),('anchor_score','retained anchor score')]:axes[1].plot(t,[u.get(key,np.nan) if u.get(key) is not None else np.nan for u in updates],label=title)
axes[1].axhline(c['selected']['config']['anchor']['anchor_score_limit'],color='gray',ls='--',label='anchor limit')
axes[2].step(t,[int(u['accepted']) for u in updates],where='post');axes[2].set_yticks([0,1],['reject','admit']);axes[2].set_xlabel('Seconds from the first preregistered bias recovery')
axes[0].set_ylabel('Horizontal error (m)');axes[0].legend();axes[1].set_ylabel('Engineering score');axes[1].legend()
for ax in axes:ax.axvspan(0,90,alpha=.08,color='orange');ax.grid(alpha=.2)
fig.savefig(out/'first_preregistered_bias10_event.png',dpi=180);plt.close(fig)
generated={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.suffix in ['.png','.csv']}
(out/'figure_identity.json').write_text(json.dumps({'input_SHA256':sources,'generated_SHA256':generated,'scope':'development only; complete categories, no confidence interval from two same-route caches; first event selected by registered ordering, not score','heldout_opened':False},indent=2)+'\n')
print(json.dumps({'figures':[p for p in generated if p.endswith('.png')],'all_case_rows':len(fullrows),'heldout_opened':False}))
