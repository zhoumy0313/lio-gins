#!/usr/bin/env python3
"""Static scientific figures from sealed baseline metrics, with point/run identities."""
import argparse,csv,hashlib,json,os
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
p=argparse.ArgumentParser();p.add_argument('screen_run');a=p.parse_args();source=Path(a.screen_run).resolve();out=Path(os.environ['LIO_GINS_RUN_DIR'])
selected=json.loads((source/'selected_baselines.json').read_text());methods=['B2','B3','B4','B5','B6'];cases=['short_jump3','cluster_jump10','loss30_normal','loss60_normal','loss30_bias3','loss30_bias10','ramp10']
points=[];bindings=[]
for method in methods:
    for r in selected['complete_selected'][method]:
        m=r['metrics'];ev=Path(r['evaluation']);points.append([method,r['name'],r['case'],m['metrics']['horizontal_rmse_m'],m['event_macro_RMSE_m'],m['metrics']['coverage'],str(ev),hashlib.sha256((ev/'metrics.json').read_bytes()).hexdigest()]);bindings.append(ev/'metrics.json')
with (out/'figure_points.csv').open('w') as f:
    w=csv.writer(f);w.writerow(['method','config','case','route_RMSE_m','event_macro_RMSE_m','coverage','evaluation_run','metrics_SHA']);w.writerows(points)
fig,axes=plt.subplots(2,1,figsize=(12,7),gridspec_kw={'height_ratios':[1,2]},constrained_layout=True)
normal=[next(x[3] for x in points if x[0]==m and x[2]=='natural') for m in methods]
axes[0].bar(methods,normal,color=['#777777','#4393c3','#762a83','#1b7837','#e08214']);axes[0].set_ylabel('Horizontal RMSE (m)');axes[0].set_title('building00: natural F9P, common initial pose and shared LIO cache')
for i,v in enumerate(normal):axes[0].text(i,v,f'{v:.3f}',ha='center',va='bottom')
idx=np.arange(len(cases));width=.16
for i,m in enumerate(methods):
    values=[next(x[4] for x in points if x[0]==m and x[2]==c) for c in cases]
    axes[1].bar(idx+(i-2)*width,values,width,label=m)
axes[1].set_xticks(idx);axes[1].set_xticklabels(cases,rotation=20,ha='right');axes[1].set_ylabel('Macro event horizontal RMSE (m)');axes[1].set_title('Artificial GNSS pressure on real F9P; all predeclared categories');axes[1].legend(ncol=5)
fig.savefig(out/'baseline_overview.png',dpi=180);fig.savefig(out/'baseline_overview.pdf');plt.close(fig)
fig,ax=plt.subplots(figsize=(12,4),constrained_layout=True)
for m in methods:
    r=next(r for r in selected['complete_selected'][m] if r['case']=='natural');p=Path(r['evaluation'])/'per_epoch.csv';v=np.loadtxt(p,delimiter=',',skiprows=1)
    ax.plot(v[:,0]-v[0,0],np.linalg.norm(v[:,7:9],axis=1),label=m,linewidth=1);bindings.append(p)
ax.set_xlabel('Seconds from evaluation start');ax.set_ylabel('Horizontal error (m)');ax.set_title('building00 natural route; no whole-trajectory alignment');ax.legend(ncol=5)
fig.savefig(out/'natural_errors.png',dpi=180);fig.savefig(out/'natural_errors.pdf');plt.close(fig)
(out/'figure_manifest.json').write_text(json.dumps({'source_screen':str(source),'source_screen_SHA':hashlib.sha256((source/'selected_baselines.json').read_bytes()).hexdigest(),'point_data_SHA':hashlib.sha256((out/'figure_points.csv').read_bytes()).hexdigest(),'input_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in bindings},'notes':'development only; artificial pressure separate from natural; reference shares AT128; known initial state; not heldout'},indent=2)+'\n')
print('Saved two figures, PDFs, exact point data and run/file SHA bindings')
