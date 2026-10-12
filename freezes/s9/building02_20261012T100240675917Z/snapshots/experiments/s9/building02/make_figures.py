"""Vector figures from complete retained results; fixed first-event selection."""
import csv,json,os,sys,hashlib
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[3];OUT=Path(os.environ['LIO_GINS_RUN_DIR']);analysis=Path(sys.argv[1]);old=ROOT/'artifacts/r2/S3/summary_table.json';rows=json.loads(old.read_text())+json.loads((analysis/'summary_table.json').read_text());events=json.loads((analysis/'event_results.json').read_text())
plt.rcParams.update({'font.size':9,'pdf.fonttype':42,'svg.fonttype':'none'})
fig,axes=plt.subplots(1,3,figsize=(7.1,2.65),sharey=False)
for ax,cache,title in zip(axes,['primary','parking','building02'],['building00: seen development','parking00: seen retrospective','building02: prospective test']):
 data=[r for r in rows if r['cache']==cache];clocks=sorted([r for r in data if r['method'].startswith('Clock') and r['clean_latency_max_s'] is not None],key=lambda r:r['clean_latency_max_s']);ax.plot([r['clean_latency_max_s'] for r in clocks],[r['bias_RMSE_90_m'] for r in clocks],'-o',color='#3465a4',ms=3,label='Clocks')
 for r in clocks:ax.annotate(r['method'][5:],(r['clean_latency_max_s'],r['bias_RMSE_90_m']),xytext=(2,-10 if r['method'] in ['Clock2','Clock10'] else 4),textcoords='offset points',fontsize=6)
 for r in data:
  if r['method'].startswith('Clock') or r['clean_latency_max_s'] is None or r['bias_RMSE_90_m'] is None:continue
  method=r['method'];color,marker=('#d02020','*') if method=='P' else ('black','^') if method.startswith('NIS') else ('#888888','x') if method.startswith('P_without') else ('#208030','s')
  ax.scatter(r['clean_latency_max_s'],r['bias_RMSE_90_m'],s=80 if method=='P' else 22,marker=marker,color=color,zorder=4)
  if method in ['P','NIS2','B6']:ax.annotate('NIS30' if method=='NIS2' else method,(r['clean_latency_max_s'],r['bias_RMSE_90_m']),xytext=(3,7 if method=='P' else -9),textcoords='offset points',fontsize=6)
 ax.axvline(15,color='#555555',ls=':',lw=1);ax.set_title(title,fontsize=8);ax.grid(alpha=.2)
 finite=[r['clean_latency_max_s'] for r in data if r['clean_latency_max_s'] is not None];ax.set_xlim(-5,max(finite+[95])+7)
 ax.set_ylabel('Bias90 horizontal RMSE (m)',fontsize=8)
fig.supxlabel('Maximum clean actual-update delay (s)',fontsize=9);fig.tight_layout()
for ext in ['pdf','svg','png']:fig.savefig(OUT/('latency_error_tradeoff.'+ext),dpi=180)
plt.close(fig)
methods=['NIS2','B6','Clock10','Clock90','P'];colors=['black','#208030','#3465a4','#7b50a5','#d02020'];fig,axes=plt.subplots(3,1,figsize=(3.6,3.5),sharex=True,gridspec_kw={'height_ratios':[2,1,1]});points=[]
for method,color in zip(methods,colors):
 r=next(r for r in events if r['method']==method and r['case']=='loss30_bias10');returned=r['events'][0]['t_return_sow'];epoch=np.loadtxt(analysis/'per_epoch'/f'building02_{method}_loss30_bias10.csv',delimiter=',',skiprows=1);mask=(epoch[:,0]>=returned-10)&(epoch[:,0]<returned+180);t=epoch[mask,0]-returned;h=np.linalg.norm(epoch[mask,1:3],axis=1);axes[0].plot(t,h,color=color,label='NIS30' if method=='NIS2' else method,lw=1)
 logs=[json.loads(l) for l in (Path(r['backend'])/'per_update.jsonl').read_text().splitlines()];u=[x for x in logs if returned-10<=x['measurement_sow']<returned+180];ut=np.array([x['measurement_sow']-returned for x in u]);accepted=np.array([x['accepted'] for x in u]);axes[1].scatter(ut[accepted],np.full(int(accepted.sum()),methods.index(method)),s=5,color=color);axes[2].plot(ut,[x['correction_norm_m'] for x in u],color=color,lw=.8)
 for x,y in zip(t,h):points.append({'method':method,'event':0,'relative_s':x,'horizontal_error_m':y,'backend_run':r['backend'],'config_SHA':r['provenance']['config_SHA'],'cache_SHA':r['provenance']['cache_SHA']})
for ax in axes:ax.axvspan(0,90,color='#edc674',alpha=.2);ax.axvline(0,color='#555555',ls=':');ax.grid(alpha=.2)
axes[0].set_ylabel('Horizontal error (m)');axes[0].legend(ncol=3,fontsize=6.5);axes[1].set_yticks(range(len(methods)));axes[1].set_yticklabels(['NIS30','B6','Clock10','Clock90','P'],fontsize=8);axes[1].set_ylabel('Accepted rows');axes[2].set_ylabel('Correction (m)');axes[2].set_xlabel('Time after returned observation (s)');fig.tight_layout()
for ext in ['pdf','svg','png']:fig.savefig(OUT/('first_registered_bias_event.'+ext),dpi=180)
plt.close(fig)
for name,values in [('representative_event_points.csv',points),('tradeoff_points.csv',rows)]:
 fields=list(dict.fromkeys(k for row in values for k in row))
 with (OUT/name).open('w') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(values)
(OUT/'figure_manifest.json').write_text(json.dumps({'analysis_run':str(analysis),'source_SHA':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [old,analysis/'summary_table.json',analysis/'event_results.json']},'script_SHA':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'representative_selection':'building02 loss30_bias10 first registered event0; predetermined methods NIS30/B6/Clock10/Clock90/P','all_controls_point_table':True,'second_building_cache':'retained R2 sensitivity, not independent; full points included','B2_censored':'in complete tables, no finite x-axis position'},indent=2)+'\n')
