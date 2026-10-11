#!/usr/bin/env python3
"""Offline fixed event diagnostics: perturbed vs matching natural control windows."""
import argparse,csv,hashlib,json,os
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=argparse.ArgumentParser();p.add_argument('screen_run');a=p.parse_args();source=Path(a.screen_run).resolve();out=Path(os.environ['LIO_GINS_RUN_DIR']);selected=json.loads((source/'selected_baselines.json').read_text());records=[];sources=[source/'selected_baselines.json'];curves=[]
case_id='loss30_bias10';event_index=0
for method in ['B2','B3','B4','B5','B6']:
    runs=selected['complete_selected'][method];natural=next(r for r in runs if r['case']=='natural');natural_file=Path(natural['evaluation'])/'per_epoch.csv';n=np.loadtxt(natural_file,delimiter=',',skiprows=1);sources.append(natural_file)
    for r in runs:
        m=r['metrics'];data_file=Path(r['evaluation'])/'per_epoch.csv';v=np.loadtxt(data_file,delimiter=',',skiprows=1);sources.append(data_file)
        if v.shape!=n.shape or not np.array_equal(v[:,0],n[:,0]):raise ValueError('natural/stress evaluation grids differ')
        for i,e in enumerate(m['events']):
            window=e['event']['window_sow'];mask=(n[:,0]>=window[0])&(n[:,0]<=window[1]);h=np.linalg.norm(n[mask,7:9],axis=1)
            normal_rmse=float(np.sqrt(np.mean(h*h))) if np.isfinite(h).all() else None
            records.append({'method':method,'config':r['name'],'case':r['case'],'event_index':i,'event':e['event'],'event_RMSE_m':e['metrics']['horizontal_rmse_m'],'matching_natural_window_RMSE_m':normal_rmse,'change_from_natural_RMSE_m':e['metrics']['horizontal_rmse_m']-normal_rmse if normal_rmse is not None else None,'recovery_s':e['metrics']['recovery_time_s'],'recovery_timeout':not e['metrics']['recovered_within_timeout'],'correction_max_m':m['update_correction_max_m'],'backend_run':r['backend']['output'],'evaluation_run':r['evaluation']})
            if r['case']==case_id and i==event_index and method in ['B3','B4','B5','B6']:
                curves.append((method,r,e['event'],v[mask]))
with (out/'all_event_comparisons.csv').open('w') as f:
    w=csv.writer(f);w.writerow(['method','config','case','event','event_RMSE_m','natural_window_RMSE_m','change_m','recovery_s','timeout','backend_run','evaluation_run'])
    for r in records:w.writerow([r['method'],r['config'],r['case'],r['event_index'],r['event_RMSE_m'],r['matching_natural_window_RMSE_m'],r['change_from_natural_RMSE_m'],r['recovery_s'],r['recovery_timeout'],r['backend_run'],r['evaluation_run']])
fig,axes=plt.subplots(3,1,figsize=(11,8),sharex=True,constrained_layout=True);points=[]
for method,r,event,v in curves:
    t0=event['fault_start_sow'];axes[0].plot(v[:,0]-t0,np.linalg.norm(v[:,7:9],axis=1),label=method)
    log=Path(r['backend']['output'])/'per_update.jsonl';sources.append(log);updates=[json.loads(line) for line in log.read_text().splitlines()];updates=[u for u in updates if event['window_sow'][0]<=u['measurement_sow']<=event['window_sow'][1]]
    times=np.array([u['measurement_sow']-t0 for u in updates]);axes[1].plot(times,[u['nominal_nis'] for u in updates],label=method,marker='.',markersize=2);axes[2].plot(times,[u['correction_norm_m'] for u in updates],label=method,marker='.',markersize=2)
    points.extend([[method,float(row[0]),float(np.linalg.norm(row[7:9]))] for row in v])
for ax in axes:ax.axvspan(0,30,color='gray',alpha=.15);ax.axvspan(30,120,color='orange',alpha=.1);ax.grid(alpha=.2)
axes[0].set_ylabel('Horizontal error (m)');axes[0].set_title('Fixed example: first loss30_bias10 event, all chosen robust controls');axes[0].legend(ncol=4)
axes[1].set_ylabel('Nominal NIS');axes[2].set_ylabel('Pure update correction (m)');axes[2].set_xlabel('Seconds from fault start (gray: deletion; orange: artificial persistent offset)')
fig.savefig(out/'fixed_recovery_event.png',dpi=180);fig.savefig(out/'fixed_recovery_event.pdf');plt.close(fig)
with (out/'figure_error_points.csv').open('w') as f:w=csv.writer(f);w.writerow(['method','sow','horizontal_error_m']);w.writerows(points)
(out/'diagnostic_manifest.json').write_text(json.dumps({'scope':'offline development diagnostics; not a new protocol or online fault input','fixed_example_case':case_id,'fixed_example_event_index':event_index,'example_selection':'first predeclared persistent-10m-recovery event, no performance-based event picking','all_event_comparisons':records,'limitations':'artificial perturbation may sometimes cancel real receiver error; compare every fixed direction/event, do not assume every added offset worsens absolute error','input_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}},indent=2)+'\n');print(json.dumps({'all_events':len(records),'figure':'fixed_recovery_event.png'}))
