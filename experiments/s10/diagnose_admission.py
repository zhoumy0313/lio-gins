"""C/E1: aligned actual decisions and offline anchor decomposition, no replay."""
import gzip,json,os,collections
from pathlib import Path
import numpy as np
from common import *
from mechanism_support import event_window_updates
OUT=Path(os.environ['LIO_GINS_S10_OUT']);summary=[];attribution=[];alltimes=[]
registered=json.loads((ROOT/'artifacts/s10/event_table.json').read_text());offline_labels=list(csv.DictReader((ROOT/'artifacts/s10/injection_row_labels_offline.csv').open()));labelmap={(x['route'],x['case'],int(x['original_gnss_id'])):x for x in offline_labels}
for route,item in catalog().items():
 c=route_context(route);nat=load_gnss(c['stress']/'natural.csv');nmap={int(g[0]):g for g in nat};ncache=np.load(c['cache']/'lio_cache.npz');route_points=[]
 for case in CASES:
  gnss=load_gnss(c['stress']/(case+'.csv'));gmap={int(g[0]):g for g in gnss};series={m:updates(str(resolve(item['rows'][(m,case)]['backend']))) for m in METHODS};by={m:{u['original_gnss_id']:u for u in series[m]} for m in METHODS}
  scoped=event_window_updates(series['P'],events(route,case))
  p_times=sorted(set(u['measurement_sow'] for u in scoped)|{u['anchor_measurement_sow_used'] for u in scoped if u.get('anchor_measurement_sow_used') is not None})
  local=local_antenna(c,p_times);truth=antenna_truth(c,p_times);loc={t:v for t,v in zip(p_times,local)};tr={t:v for t,v in zip(p_times,truth)}
  # Logged local health is sensor/cache-computable, not ground truth quality.
  health={}
  for t in p_times:
   j=int(np.searchsorted(ncache['sow'],t));assert j<len(ncache['sow']);i=j if ncache['sow'][j]==t else j-1
   health[t]=(float(min(ncache['effective_points'][i],ncache['effective_points'][j])),float(max(ncache['mean_abs_plane_residual_m'][i],ncache['mean_abs_plane_residual_m'][j])))
  for ei,event in enumerate(events(route,case)):
   start=event['recovery_start_sow'];end=start+90;exposed=[g for g in gnss if start<=g[1]<end];ids={int(g[0]) for g in exposed};p=by['P'];no=by['P_without_anchor'];nis=by['NIS0'];extra=[oid for oid in ids if not p[oid]['accepted'] and no[oid]['accepted']]
   veto=[oid for oid in ids if p[oid]['reason']=='retained_anchor_inconsistent'];veto_short_good=[oid for oid in veto if p[oid].get('motion_score') is not None and p[oid]['motion_score']<=4]
   # Pure constant displacement cancels from pairs lying inside the same injected interval.
   invariant=[]
   for g in exposed:
    prev=next((old for old in exposed if abs(old[1]-(g[1]-5))<1e-8),None)
    if prev is not None:invariant.append(float(np.linalg.norm((g[2:5]-prev[2:5])-(nmap[int(g[0])][2:5]-nmap[int(prev[0])][2:5]))))
   assert not invariant or max(invariant)<1e-8
   derived=[]
   for u in series['P']:
    if not start-40<=u['measurement_sow']<start+180:continue
    t=u['measurement_sow'];oid=u['original_gnss_id'];anchor_t=u.get('anchor_measurement_sow_used');aid=u.get('anchor_original_gnss_id_used');decomp={k:None for k in ['anchor_receiver_error_h_m','relative_LIO_error_h_m','current_receiver_error_h_m','anchor_residual_h_m','anchor_injected','decomposition_max_abs_difference_m']}
    if anchor_t is not None and aid is not None:
     assert aid in gmap;anchor_error=gmap[aid][2:5]-tr[anchor_t];current_error=gmap[oid][2:5]-tr[t];drift=(loc[t]-loc[anchor_t])-(tr[t]-tr[anchor_t]);residual=gmap[oid][2:5]-(gmap[aid][2:5]+loc[t]-loc[anchor_t]);identity_error=float(max(abs(residual-(current_error-anchor_error-drift))));assert identity_error<1e-9
     decomp.update(anchor_receiver_error_h_m=float(np.linalg.norm(anchor_error[:2])),relative_LIO_error_h_m=float(np.linalg.norm(drift[:2])),current_receiver_error_h_m=float(np.linalg.norm(current_error[:2])),anchor_residual_h_m=float(np.linalg.norm(residual[:2])),anchor_injected=bool(np.linalg.norm(gmap[aid][2:5]-nmap[aid][2:5])>1e-8),decomposition_max_abs_difference_m=identity_error)
    pts,res=health[t];healthy=pts>=100 and res<=.2;assert healthy==u.get('local_health_verified',healthy)
    if u['reason']=='retained_anchor_inconsistent':assert u.get('anchor_score')>4 and healthy and not u['accepted']
    derived.append({'route':route,'case':case,'event':ei,'method':'P','original_gnss_id':oid,'measurement_sow':t,'relative_s':t-start,'available_sow':u['available_sow'],'accepted':u['accepted'],'reason':u['reason'],'state':u.get('state'),'nominal_nis':u['nominal_nis'],'motion_score':u.get('motion_score'),'anchor_score':u.get('anchor_score'),'anchor_active':u.get('anchor_active'),'anchor_age_s':u.get('anchor_age_s'),'anchor_id_used':aid,'local_health_verified':u.get('local_health_verified'),'local_effective_points_min':pts,'local_plane_residual_max_m':res,'r_multiplier':u.get('r_multiplier'),'correction_norm_m':u['correction_norm_m'],'qualification_elapsed_s':u.get('qualification_elapsed_s'),'no_anchor_accepted':no.get(oid,{}).get('accepted'),'NIS0_accepted':nis.get(oid,{}).get('accepted'),'NIS0_nominal_nis':nis.get(oid,{}).get('nominal_nis'),**decomp})
   p90=[u for u in derived if 0<=u['relative_s']<90]
   for method in METHODS:
    selected=[u for u in series[method] if start<=u['measurement_sow']<start+180];bias=[u for u in selected if u['measurement_sow']<end];scores=[u.get('motion_score') for u in bias if u.get('motion_score') is not None];anchor_scores=[u.get('anchor_score') for u in bias if u.get('anchor_score') is not None];ages=[u.get('anchor_age_s') for u in bias if u.get('anchor_age_s') is not None];src=next(x for x in registered if x['route']==route and x['case']==case and x['method']==method and x['event']==ei)
    summary.append({'route':route,'case':case,'event':ei,'method':method,'RMSE_90_m':src['RMSE_90_m'],'RMSE_180_m':src['RMSE_180_m'],'T_admit_s':src['T_admit_s'],'T_available_bound_s':src['T_available_bound_s'],'injected_accepted':src['injected_accepted'],'actual_first_admission_status':src['admission_status'],'first_accepted_id':src['first_accepted_original_id'],'logged_post90_rows':len(bias),'accepted_post90_rows':sum(u['accepted'] for u in bias),'reasons':json.dumps(dict(collections.Counter(u['reason'] for u in bias)),sort_keys=True),'motion_score_logged_rows':len(scores),'motion_good_rows':sum(v<=4 for v in scores),'anchor_score_logged_rows':len(anchor_scores),'anchor_veto_rows':sum(u['reason']=='retained_anchor_inconsistent' for u in bias),'anchor_age_min_s':min(ages) if ages else None,'anchor_age_max_s':max(ages) if ages else None,'local_health_false_rows':sum(u.get('local_health_verified') is False for u in bias),'NIS_limit':read_json(resolve(item['rows'][(method,case)]['backend'])/'backend_resolved.json')['nis_limit'],'maximum_post90_correction_m':max(u['correction_norm_m'] for u in bias),'backend_run':src['backend_run']})
   p_src=next(x for x in registered if x['route']==route and x['case']==case and x['method']=='P' and x['event']==ei);n_src=next(x for x in registered if x['route']==route and x['case']==case and x['method']=='P_without_anchor' and x['event']==ei)
   gp,ep=trajectory_errors(route,p_src['backend_run']);gn,en=trajectory_errors(route,n_src['backend_run']);pre=np.flatnonzero(gp<event['fault_start_sow']);before_gap=float(np.linalg.norm(ep[pre[-1],:2]-en[pre[-1],:2]))
   worst=[d for d in p90 if d['relative_LIO_error_h_m'] is not None];additional_labels=[labelmap[(route,case,i)] for i in extra if (route,case,i) in labelmap]
   attribution.append({'route':route,'case':case,'event':ei,'P_minus_no_anchor_RMSE_90_m':p_src['RMSE_90_m']-n_src['RMSE_90_m'],'before_fault_P_no_anchor_position_difference_h_m':before_gap,'extra_rejected_vs_no_anchor':len(extra),'extra_rejected_and_NIS0_accepted':sum(nis[i]['accepted'] for i in extra),'direct_anchor_veto_rows':len(veto),'veto_with_short_window_good_rows':len(veto_short_good),'veto_without_short_window_score_rows':sum(p[i].get('motion_score') is None for i in veto),'direct_veto_also_NIS0_accepted':sum(nis[i]['accepted'] for i in veto),'extra_rejected_injection_cancels_rows':sum(x['injection_reduces_error']=='True' for x in additional_labels),'constant_bias_short_difference_max_m':max(invariant) if invariant else None,'offline_relative_LIO_error_max_m':max((x['relative_LIO_error_h_m'] for x in worst),default=None),'offline_anchor_receiver_error_max_m':max((x['anchor_receiver_error_h_m'] for x in worst),default=None),'logged_health_false_rows':sum(x['local_health_verified'] is False for x in p90),'decomposition_identity_checked':bool(worst),'not_an_online_truth_metric':True,'single_cause_global_claim':False})
   route_points.extend(derived)
   # Aligned raw update records for every method, not a favorable subset.
   for method in METHODS:
    if method=='P':continue
    for u in series[method]:
     if start-40<=u['measurement_sow']<start+180:route_points.append({'route':route,'case':case,'event':ei,'method':method,'relative_s':u['measurement_sow']-start,**u})
  print(json.dumps({'route':route,'case':case,'event_mechanisms':len(attribution)}),flush=True)
 with gzip.open(OUT/(route+'_aligned_updates.json.gz'),'wt') as f:json.dump(route_points,f,allow_nan=False)
csv_write(OUT/'admission_diagnosis.csv',summary);csv_write(OUT/'event_attribution.csv',attribution);json_write(OUT/'event_attribution.json',attribution)
lines=['# C event-level mechanism diagnosis','', 'Existing logs only; all3m/10m/clean events, all19 policies, six routes and a separate same-bag repeat. Actual per-ID paired decisions, source coordinates and output clocks retained. S10 is post-hoc exploratory.','', 'P/no-anchor is the single-factor comparison. P and actual NIS0 have different posterior histories; a hypothetical NIS decision from P nominal NIS is not substituted for the actual NIS0 log. Constant injected displacement cancels to numerical precision for5s pairs entirely inside each bias interval; this mathematical identity alone is not field fault detection evidence.','', '|Route/case/event|P−no-anchor90m|Extra rejected|Also NIS0 accepted|Direct anchor veto|Veto while short score good|Prior position difference m|Max offline relative LIO error m|','|---|---:|---:|---:|---:|---:|---:|---:|']
for r in attribution:
 if r['case']=='loss30_bias3':lines.append(f"|{r['route']}/{r['case']}/{r['event']}|{r['P_minus_no_anchor_RMSE_90_m']:.9f}|{r['extra_rejected_vs_no_anchor']}|{r['extra_rejected_and_NIS0_accepted']}|{r['direct_anchor_veto_rows']}|{r['veto_with_short_window_good_rows']}|{r['before_fault_P_no_anchor_position_difference_h_m']:.9g}|{r['offline_relative_LIO_error_max_m']}|")
lines+=['','Anchor decomposition is checked exactly: current receiver error minus anchor receiver error minus relative LIO error equals anchor residual. These reference-derived terms are offline explanations, never online scores or qualification. Receiver/anchor errors and reference inaccuracies can correlate, so no single global cause is established by RMSE. Actual healthy-cache flags can coexist with poor relative motion/old anchors; points/plane residual do not certify absolute drift. No truth-free reliable applicability classifier or new threshold is fitted.','', 'All street00 events, including its nearly neutral Event2, remain. Fixed representative timelines are street00 Event0 and building02 Event1, as declared before reconstruction; full other events/logs are retained. No-decay is not asserted necessary.10m NIS/P near-tie and both negative routes are retained. Per-ID additional rejection and direct veto are distinct: veto can also change later qualification and filtering histories. Events within a route are dependent, not IID.']
(OUT/'MECHANISM_DIAGNOSIS.md').write_text('\n'.join(lines)+'\n');json_write(OUT/'mechanism_manifest.json',{'diagnostic_rows':len(summary),'event_attributions':len(attribution),'aligned19_method_logs_retained':True,'anchor_decomposition_offline_only':True,'constant_bias_difference_invariance_verified':True,'selection':'fixed street00 E0 and building02 E1; every street/negative-route event retained','script_SHA':sha(__file__),'common_SHA':sha(ROOT/'experiments/s10/common.py')})
