#!/usr/bin/env python3
"""Static complete-case figures, including the supplemental negative control audit."""
import argparse,csv,json,os
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from replay_experiment_batch import digest
p=argparse.ArgumentParser();p.add_argument('heldout_summary_run');p.add_argument('long_wait_run');p.add_argument('development_verification_run');a=p.parse_args();out=Path(os.environ['LIO_GINS_RUN_DIR']);hp=Path(a.heldout_summary_run)/'heldout_summary.json';ap=Path(a.long_wait_run)/'long_wait_audit.json';vp=Path(a.development_verification_run)/'final_verification.json';h=json.loads(hp.read_text());audit=json.loads(ap.read_text());v=json.loads(vp.read_text());sources={str(p.resolve()):digest(p) for p in [hp,ap,vp]}
rows=[]
fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained')
for ax,label,cache in zip(axes,['primary','sensitivity'],['20261011T141044340351Z_P2_9dd3f300','20261011T134125698776Z_P2_0de7714e']):
    selected=[r for r in audit['table'] if Path(r['cache']).name==cache];candidate=next(r for r in v['tables'][label] if r['name']=='P')
    ax.plot([r['qualification_s'] for r in selected],[r['primary_macro_RMSE_m'] for r in selected],'o-',label='Fixed time qualification')
    ax.axhline(candidate['primary_macro_RMSE_m'],ls='--',color='#bf6b24',label='Frozen P')
    ax.set_xlabel('Fixed qualification duration (s)');ax.set_ylabel('Primary event macro horizontal RMSE (m)');ax.set_title(label+' development cache');ax.grid(alpha=.2);ax.legend()
    rows += [{'cache':label,'method':'clock_'+str(r['qualification_s']),'natural_RMSE_m':r['natural_RMSE_m'],'primary_macro_RMSE_m':r['primary_macro_RMSE_m']} for r in selected]+[{'cache':label,'method':'P','natural_RMSE_m':candidate['natural_RMSE_m'],'primary_macro_RMSE_m':candidate['primary_macro_RMSE_m']}]
fig.suptitle('Supplemental development-only audit, registered after test access');fig.savefig(out/'supplemental_long_wait_counterevidence.png',dpi=180);plt.close(fig)
with (out/'supplemental_long_wait_points.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

fig,axes=plt.subplots(1,2,figsize=(12,4),layout='constrained')
table=h['table'];names=[r['method'] for r in table]
axes[0].bar(names,[r['primary_macro_RMSE_m'] for r in table],color=['#5b7896']*5+['#bf6b24']+['#87a4b8']*4);axes[0].set_ylabel('Primary event macro horizontal RMSE (m)');axes[0].set_title('Original frozen parking00 matrix');axes[0].tick_params(axis='x',rotation=60);axes[0].grid(axis='y',alpha=.2)
case_ids=['short_jump3','cluster_jump10','loss30_normal','loss60_normal','loss30_bias3','loss30_bias10','ramp10']
for method in ['B2','B4','B6','P']:
    indexed={r['case']:r for r in h['all_cases'] if r['method']==method};axes[1].plot(range(7),[indexed[c]['event_macro_RMSE_m'] for c in case_ids],'o-',label=method)
axes[1].set_xticks(range(7),case_ids,rotation=60,ha='right');axes[1].set_ylabel('Event macro horizontal RMSE (m)');axes[1].set_title('All seven categories');axes[1].legend();axes[1].grid(alpha=.2)
fig.savefig(out/'original_frozen_parking_all_cases.png',dpi=180);plt.close(fig)
with (out/'original_frozen_parking_summary_points.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(table[0]));w.writeheader();w.writerows(table)
with (out/'original_frozen_parking_all_case_points.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(h['all_cases'][0]));w.writeheader();w.writerows(h['all_cases'])
(out/'figure_identity.json').write_text(json.dumps({'input_SHA256':sources,'output_SHA256':{p.name:digest(p) for p in out.iterdir() if p.suffix in ['.csv','.png']},'interpretation':'original frozen heldout comparison is retained; supplementary controls are not retroactively blind tests; no success-metric change','no_new_parameters':True},indent=2)+'\n');print(json.dumps({'figures':2,'complete_case_points':len(h['all_cases']),'late_controls_only_development':True}))
