"""Fixed all-route tradeoff plot; no favorable event or route selection."""
import csv,hashlib,json,os,sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2];OUT=Path(os.environ['LIO_GINS_RUN_DIR']);state=json.loads((ROOT/'docs/research_s9/STATE.json').read_text());old=ROOT/'artifacts/r2/S3/summary_table.json';s8=ROOT/'artifacts/s8/C/summary_table.json';sources=[old,s8]+[Path(state['routes'][r]['analysis_run'])/'summary_table.json' for r in state['included_routes']];rows=[r for p in sources for r in json.loads(p.read_text())];labels=['primary','parking','building01']+state['included_routes'];n=len(labels);fig,axes=plt.subplots(2,3,figsize=(7.1,3.85));plt.rcParams.update({'pdf.fonttype':42,'svg.fonttype':'none'})
for ax,cache in zip(axes.flat,labels):
 data=[r for r in rows if r['cache']==cache];clocks=sorted([r for r in data if r['method'].startswith('Clock') and r['clean_latency_max_s'] is not None],key=lambda r:r['clean_latency_max_s']);ax.plot([r['clean_latency_max_s'] for r in clocks],[r['bias_RMSE_90_m'] for r in clocks],'-o',ms=2,color='#3465a4')
 for r in clocks:ax.annotate(r['method'][5:],(r['clean_latency_max_s'],r['bias_RMSE_90_m']),xytext=(1,6 if r['method'] not in ['Clock2','Clock10'] else -10),textcoords='offset points',fontsize=5)
 for r in data:
  m=r['method']
  if m.startswith('Clock') or r['clean_latency_max_s'] is None or r['bias_RMSE_90_m'] is None:continue
  color,marker=('#d02020','*') if m=='P' else ('#8a3a8a','x') if m=='P_without_anchor' else ('#888888','x') if m.startswith('P_without') else ('black','^') if m.startswith('NIS') else ('#208030','s')
  ax.scatter(r['clean_latency_max_s'],r['bias_RMSE_90_m'],s=48 if m=='P' else 10,color=color,marker=marker)
  if m=='P':ax.annotate('P',(r['clean_latency_max_s'],r['bias_RMSE_90_m']),xytext=(3,4),textcoords='offset points',fontsize=6)
 title={'primary':'building00: seen development','parking':'parking00: seen retrospective','building01':'building01: S8 test (now seen)'}.get(cache,cache+': S9 prospective');ax.set_title(title,fontsize=7);ax.axvline(15,color='gray',ls=':',lw=.8);ax.grid(alpha=.2);ax.tick_params(labelsize=6);ax.set_xlim(-5,max([95]+[r['clean_latency_max_s'] for r in data if r['clean_latency_max_s'] is not None])+7);ax.set_ylabel('Bias90 RMSE (m)',fontsize=7)
for ax in axes.flat[n:]:ax.set_visible(False)
fig.supxlabel('Maximum clean actual-update measurement delay (s)',fontsize=8);fig.tight_layout(pad=.6)
for ext in ['pdf','svg','png']:fig.savefig(OUT/('multiroute_tradeoff.'+ext),dpi=180)
plt.close(fig)
points=[r for r in rows if r['cache'] in labels]
with (OUT/'tradeoff_points.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in points for k in r)));w.writeheader();w.writerows(points)
(OUT/'figure_manifest.json').write_text(json.dumps({'selection':'every fixed route in registration order, every policy; no event chosen','B2':'censored x coordinate, retained in table and exported points','sources':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},'script_SHA':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'each_panel_own_vertical_scale':True},indent=2)+'\n');print('All fixed route policy points exported')
