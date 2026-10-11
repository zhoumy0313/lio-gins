"""Scientific vector plots from retained per-event points; no selected winners."""
import argparse,csv,hashlib,json,os,sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2]
plt.rcParams.update({'font.size':9,'pdf.fonttype':42,'svg.fonttype':'none'})
p=argparse.ArgumentParser();p.add_argument('analysis');a=p.parse_args();source=Path(a.analysis);OUT=Path(os.environ['LIO_GINS_RUN_DIR']);rows=json.loads((source/'summary_table.json').read_text());events=json.loads((source/'event_results.json').read_text())
fig,axes=plt.subplots(1,3,figsize=(10.8,3.5),sharey=True)
for ax,cache,title in zip(axes,['primary','sensitivity','parking'],['building00: primary cache','building00: sensitivity cache','parking00: seen historical route']):
    data=[r for r in rows if r['cache']==cache];clocks=sorted([r for r in data if r['method'].startswith('Clock')],key=lambda r:r['clean_latency_max_s'])
    ax.plot([r['clean_latency_max_s'] for r in clocks],[r['bias_RMSE_90_m'] for r in clocks],'-o',color='#3465a4',ms=4,label='Clock family')
    for r in clocks:ax.annotate(r['method'][5:],(r['clean_latency_max_s'],r['bias_RMSE_90_m']),xytext=(2,5),textcoords='offset points',fontsize=7)
    for method,color,marker in [('B3','#666666','s'),('B4','#cc5800','^'),('B5','#8a3a8a','D'),('B6','#208030','v'),('P','#d02020','*')]:
        r=next(r for r in data if r['method']==method);ax.scatter(r['clean_latency_max_s'],r['bias_RMSE_90_m'],color=color,marker=marker,s=100 if method=='P' else 25,zorder=4,label=method)
        ax.annotate(method,(r['clean_latency_max_s'],r['bias_RMSE_90_m']),xytext=(4,-11 if method=='B3' else 4),textcoords='offset points',fontsize=7)
    for r in data:
        if r['method'].startswith('P_without'):ax.scatter(r['clean_latency_max_s'],r['bias_RMSE_90_m'],s=20,color='#777777',marker='x',zorder=2)
    ax.axvline(15,color='#555555',ls=':',lw=1);ax.set_title(title,fontsize=9);ax.set_xlabel('Maximum clean admission latency (s)');ax.grid(alpha=.2);ax.set_xlim(-4,101)
axes[0].set_ylabel('Biased post-return 90-s horizontal RMSE (m)');axes[0].legend(fontsize=7,loc='upper right');fig.tight_layout()
for ext in ['pdf','svg','png']:fig.savefig(OUT/('latency_error_tradeoff.'+ext),dpi=180)
plt.close(fig)
# Representative event: first event by registered order, not selected by gain.
methods=['B4','B6','Clock10','Clock90','P'];colors=['#cc5800','#208030','#3465a4','#7b50a5','#d02020'];fig,axes=plt.subplots(3,1,figsize=(7.1,5.1),sharex=True,gridspec_kw={'height_ratios':[2,1,1]});pointrows=[]
for method,color in zip(methods,colors):
    r=next(r for r in events if r['cache']=='primary' and r['method']==method and r['case']=='loss30_bias10');returned=r['events'][0]['t_return_sow'];epochs=np.loadtxt(source/'per_epoch'/('primary_'+method+'_loss30_bias10.csv'),delimiter=',',skiprows=1);mask=(epochs[:,0]>=returned-10)&(epochs[:,0]<returned+180);t=epochs[mask,0]-returned;h=np.linalg.norm(epochs[mask,1:3],axis=1);axes[0].plot(t,h,color=color,label=method,lw=1)
    updates=[json.loads(l) for l in (Path(r['backend'])/'per_update.jsonl').read_text().splitlines()];u=[x for x in updates if returned-10<=x['measurement_sow']<returned+180];ut=np.array([x['measurement_sow']-returned for x in u]);accepted=np.array([bool(x['accepted']) for x in u]);offset=methods.index(method);axes[1].scatter(ut[accepted],np.full(int(accepted.sum()),offset),s=6,color=color);axes[2].plot(ut,[x['correction_norm_m'] for x in u],color=color,lw=.8)
    for x,y in zip(t,h):pointrows.append({'method':method,'cache':'primary','case':'loss30_bias10','event':0,'relative_s':x,'horizontal_error_m':y,'backend_run':r['backend'],'config_SHA':r['provenance']['config_SHA'],'cache_SHA':r['provenance']['cache_SHA']})
for ax in axes:ax.axvspan(0,90,color='#edc674',alpha=.2);ax.axvline(0,color='#555555',ls=':');ax.grid(alpha=.2)
axes[0].set_ylabel('Horizontal error (m)');axes[0].legend(ncol=5,fontsize=8);axes[1].set_yticks(range(len(methods)));axes[1].set_yticklabels(methods,fontsize=8);axes[1].set_ylabel('Accepted rows');axes[2].set_ylabel('Correction (m)');axes[2].set_xlabel('Time after first returned observation (s)');fig.tight_layout()
for ext in ['pdf','svg','png']:fig.savefig(OUT/('first_registered_bias_event.'+ext),dpi=180)
plt.close(fig)
with (OUT/'representative_event_points.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(pointrows[0]));w.writeheader();w.writerows(pointrows)
with (OUT/'tradeoff_points.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(OUT/'figure_manifest.json').write_text(json.dumps({'analysis_run':str(source),'source_SHA':{str(source/name):hashlib.sha256((source/name).read_bytes()).hexdigest() for name in ['summary_table.json','event_results.json']},'figure_script_SHA':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'event_selection':'primary cache, loss30_bias10, first registered event index 0, fixed order','all_controls_in_point_table':True,'B2_censored':'excluded from finite x-axis; reported as CENSORED in complete tables','new_route_opened':False},indent=2)+'\n')
print(json.dumps({'vector_figures':2,'all_methods_point_rows':len(rows),'representative_point_rows':len(pointrows)}))
