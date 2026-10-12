"""Fixed all-event and opposite-case vector figures from actual retained sources."""
import gzip,json,os
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from common import *
OUT=Path(os.environ['LIO_GINS_S10_OUT']);plt.rcParams.update({'font.size':8,'axes.labelsize':8,'axes.titlesize':8,'legend.fontsize':7,'xtick.labelsize':7,'ytick.labelsize':7,'pdf.fonttype':42,'ps.fonttype':42})
sources={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'artifacts/s10/evidence_matrix.json',ROOT/'artifacts/s10/event_table.json',ROOT/'artifacts/s10/event_attribution.json',ROOT/'docs/research_s10/ANALYSIS_REGISTRATION.md']}
ev=read_json(ROOT/'artifacts/s10/event_table.json');matrix=read_json(ROOT/'artifacts/s10/evidence_matrix.json');outputs={};points=[]
colors={'P':'#c93239','P_without_anchor':'#2374ab','NIS0':'#222222','Clock90':'#b07c22'}
names={'P':'P','P_without_anchor':'No anchor','NIS0':'Strict NIS','Clock90':'Clock90'}
def save(fig,name):
 fig.savefig(OUT/(name+'.pdf'),bbox_inches='tight');fig.savefig(OUT/(name+'.svg'),bbox_inches='tight');fig.savefig(OUT/(name+'.png'),bbox_inches='tight',dpi=180);plt.close(fig)
 for ext in ['pdf','svg','png']:outputs[name+'.'+ext]=sha(OUT/(name+'.'+ext))
def source_row(route,method,event,case='loss30_bias3'):return next(x for x in ev if x['route']==route and x['method']==method and x['case']==case and x['event']==event)
def curve(ax,route,method,event,duration=90,case='loss30_bias3'):
 r=source_row(route,method,event,case);grid,error=trajectory_errors(route,r['backend_run']);selected=(grid>=r['return_sow']-1e-8)&(grid<r['return_sow']+duration-1e-8);t=grid[selected]-r['return_sow'];h=np.linalg.norm(error[selected,:2],axis=1);assert len(t)==round(duration*10) and np.isfinite(h).all()
 ax.plot(t,h,color=colors[method],lw=1.2 if method=='P' else .85,label=names[method]);sources[str(resolve(r['backend_run'])/'trajectory.csv')]=sha(resolve(r['backend_run'])/'trajectory.csv')
 for x,y in zip(t,h):points.append({'figure_scope':route+'/'+case,'route':route,'case':case,'event':event,'method':method,'relative_s':float(x),'horizontal_error_m':float(y),'source_run':r['backend_run']})
 return r
# A: an estimator-native conceptual structure; no synthetic plot pretending to be measured data.
fig,axes=plt.subplots(1,2,figsize=(7.1,2.0))
for ax in axes:ax.axis('off');ax.set_xlim(0,1);ax.set_ylim(0,1)
axes[0].set_title('Short window: constant displacement cancels',loc='left')
axes[0].text(.03,.66,r'$z_{k}=z^{0}_{k}+b,\quad z_{k-5}=z^{0}_{k-5}+b$',fontsize=10)
axes[0].text(.03,.37,r'$(z_k-z_{k-5})-(a_k-a_{k-5})$',fontsize=11)
axes[0].text(.03,.1,'No added information about constant b\nwhen both rows share it; gap resets history.',fontsize=8)
axes[1].set_title('Historical anchor: span the outage',loc='left')
axes[1].text(.03,.69,r'$\hat z_k=z_a+(a_k-a_a),\quad e^A_k=z_k-\hat z_k$',fontsize=10)
axes[1].text(.03,.49,'Past admitted raw GNSS / LIO',fontsize=8)
axes[1].annotate('Admission veto',(.73,.26),(.03,.28),arrowprops={'arrowstyle':'->'},fontsize=8)
axes[1].text(.02,.05,'Anchor is a decision memory, never another measurement.\nOnly current original GNSS updates the position KF once.',fontsize=8)
fig.tight_layout(w_pad=2);save(fig,'A_anchor_concept')
# B: every fixed street event, with actual admission in the biased case stated explicitly.
for route,name in [('street00','B_street_all_events'),('building02','S_building02_all_events')]:
 fig,axes=plt.subplots(1,3,figsize=(7.1,2.25),sharex=True)
 for i,ax in enumerate(axes):
  for m in colors:curve(ax,route,m,i)
  p=source_row(route,'P',i);n=source_row(route,'P_without_anchor',i)
  ax.set_title(f"{['N','E','NE'][i]}: P {p['RMSE_90_m']:.3f} / no anchor {n['RMSE_90_m']:.3f} m")
  ax.set_xlabel('Seconds after biased return');ax.grid(alpha=.2)
  delay='C180' if p['T_admit_s'] is None else f"{p['T_admit_s']:.0f}s"
  ax.text(.02,.96,f"P first admit {delay}; {p['injected_accepted']}/90 injected",transform=ax.transAxes,va='top',fontsize=7,bbox={'facecolor':'white','alpha':.8,'edgecolor':'none'})
  if p['T_admit_s'] is not None and p['T_admit_s']<90:ax.axvline(p['T_admit_s'],color=colors['P'],ls=':',lw=.8)
 axes[0].set_ylabel('Horizontal error (m)');fig.legend(*axes[0].get_legend_handles_labels(),loc='lower center',ncol=4,bbox_to_anchor=(.5,-.08),frameon=False);fig.tight_layout();save(fig,name)
# C: representative cases fixed in the pre-reconstruction editorial registration.
fig,axes=plt.subplots(3,2,figsize=(7.1,4.0),sharex='col',gridspec_kw={'height_ratios':[1.15,1,.9]});scorepoints=[]
for col,(route,event) in enumerate([('street00',0),('building02',1)]):
 for m in colors:curve(axes[0,col],route,m,event,180)
 axes[0,col].set_title(f'{route}, fixed { ["N","E","NE"][event] } event')
 path=ROOT/'artifacts/s10'/(route+'_aligned_updates.json.gz');sources[str(path.relative_to(ROOT))]=sha(path)
 with gzip.open(path,'rt') as f:raw=json.load(f)
 p=[x for x in raw if x['method']=='P' and x['case']=='loss30_bias3' and x['event']==event and 0<=x['relative_s']<180];n=[x for x in raw if x['method']=='NIS0' and x['case']=='loss30_bias3' and x['event']==event and 0<=x['relative_s']<180]
 for field,color,label in [('anchor_score','#c93239','Anchor'),('motion_score','#2374ab','Short window')]:
  axes[1,col].plot([x['relative_s'] for x in p],[np.nan if x.get(field) is None else x[field] for x in p],color=color,lw=1,label=label)
 axes[1,col].axhline(4,color='#555',ls='--',lw=.8,label='Engineering limit 4');axes[1,col].set_yscale('symlog',linthresh=1)
 axes[2,col].plot([x['relative_s'] for x in n],[x['nominal_nis'] for x in n],color='#333',lw=.85,label='Actual NIS0 posterior')
 axes[2,col].axhline(11.3448667301,color='#555',ls='--',lw=.8,label='NIS gate 11.3449');axes[2,col].set_yscale('symlog',linthresh=1)
 for accepted,marker,color in [(True,'o','#3d8c4f'),(False,'x','#999')]:
  nr=[x for x in n if x['accepted']==accepted];axes[2,col].scatter([x['relative_s'] for x in nr],[x['nominal_nis'] for x in nr],s=5,marker=marker,color=color,alpha=.7,label='NIS accepted' if accepted else 'NIS rejected')
 pa=[x for x in p if x['accepted']];axes[1,col].scatter([x['relative_s'] for x in pa],[.98]*len(pa),transform=axes[1,col].get_xaxis_transform(),marker='|',s=35,color=colors['P'],label='P accepted (rug)')
 for ax in axes[:,col]:ax.axvspan(0,90,color='#e6cf82',alpha=.17);ax.axvline(90,color='#777',lw=.7,ls=':');ax.grid(alpha=.15)
 axes[2,col].set_xlabel('Seconds after biased return')
 for x in p:scorepoints.append(x)
axes[0,0].set_ylabel('Position error (m)');axes[1,0].set_ylabel('Anchor / short score');axes[2,0].set_ylabel('Logged NIS0 NIS')
axes[0,0].legend(loc='upper left',fontsize=7,framealpha=.8,ncol=2);axes[1,0].legend(loc='lower left',fontsize=7,framealpha=.8,ncol=2);axes[2,0].legend(loc='lower left',fontsize=7,framealpha=.8,ncol=2);fig.tight_layout(h_pad=.25);save(fig,'C_fixed_mechanism_timelines')
csv_write(OUT/'mechanism_score_points.csv',scorepoints)
# D: all6 routes; same-bag repeat belongs to the evidence, not an extra scene.
routes=[r for r in catalog() if r!='building00_repeat'];p=[next(x for x in matrix if x['route']==r and x['method']=='P' and x['case']=='loss30_bias3') for r in routes];n=[next(x for x in matrix if x['route']==r and x['method']=='P_without_anchor' and x['case']=='loss30_bias3') for r in routes]
fig,ax=plt.subplots(figsize=(7.1,2.05));x=np.arange(len(routes));ax.bar(x-.16,[r['RMSE_90_macro_m'] for r in n],.3,color=colors['P_without_anchor'],label='No anchor');ax.bar(x+.16,[r['RMSE_90_macro_m'] for r in p],.3,color=colors['P'],label='P')
for i,row in enumerate(p):
 status='Q pass' if row['service_cost_qualified'] else 'cost fail' if row['clean_max_admit_s'] is not None and row['clean_max_admit_s']<=15 else 'cost + delay fail'
 ax.text(i,max(row['RMSE_90_macro_m'],n[i]['RMSE_90_macro_m'])+.15,status,ha='center',fontsize=7)
ax.set_xticks(x,['building00\nseen dev','parking00\nseen retro','building01\nS8 (now seen)','street00\nS9 (now seen)','playground00\nS9 (now seen)','building02\nS9 (now seen)']);ax.set_ylabel('3m post90 event-macro RMSE (m)');ax.legend(frameon=False,loc='upper left');ax.set_ylim(0,12);ax.grid(axis='y',alpha=.2);fig.tight_layout();save(fig,'D_all_six_route_contrasts')
csv_write(OUT/'trajectory_points.csv',points);csv_write(OUT/'cross_route_points.csv',[{'route':r,'P_macro_m':pp['RMSE_90_macro_m'],'no_anchor_macro_m':nn['RMSE_90_macro_m'],'P_natural_m':pp['natural_RMSE_m'],'cap_m':pp['natural_cap_m'],'clean_each_s':pp['clean_admit_each_s'],'qualification':pp['service_cost_qualified']} for r,pp,nn in zip(routes,p,n)])
json_write(OUT/'figure_manifest.json',{'figures':outputs,'sources':sources,'selection':'all fixed street/negative-route events; representative street00 E0 and building02 E1 as declared before C; all6routes, repeat excluded only as separate sensitivity identity','points_files':{name:sha(OUT/name) for name in ['trajectory_points.csv','mechanism_score_points.csv','cross_route_points.csv']},'script_SHA':sha(__file__),'no_fabricated_missing_score':True,'all_actual_position_points_full_grid':True,'offline_reference_curves_only':True})
print(json.dumps({'vector_figures':5,'point_rows':len(points),'all6routes':True,'old_outputs_modified':False}))
