"""A: independently recompute retained 3m/10m/clean events and natural grids."""
import csv,json,os
from pathlib import Path
import numpy as np
from common import *
OUT=Path(os.environ['LIO_GINS_S10_OUT']);evidence=[];eventrows=[];provenance=[];checks=[];maxdiff=0.
for route,item in catalog().items():
 c=route_context(route);original={ (r['method'],r['case'],int(r['event'])):r for r in csv.DictReader((ROOT/item['folder']/'event_table.csv').open()) if r['cache']==item['cache_label']}
 natural={};data_cache={};source_keys=[]
 for method in METHODS:
  row=item['rows'][(method,'natural')];run=resolve(row['backend']);grid,error=trajectory_errors(route,run);h=np.linalg.norm(error[:,:2],axis=1);natural[method]=float(np.sqrt(np.mean(h*h))) if np.isfinite(h).all() else None
  old=row['whole']['horizontal_RMSE_m'];assert old is None or abs(natural[method]-old)<1e-11
 capbase=min(natural[m] for m in ['B4','B5','B6']);cap=capbase+max(.02*capbase,.05)
 for method in METHODS:
  percase={}
  for case in CASES+['natural']:
   row=item['rows'][(method,case)];run=resolve(row['backend']);identity=read_json(run/'backend_identity.json');config=read_json(run/'backend_resolved.json');gnssp=resolve(identity['gnss_source']);icp=resolve(Path(identity['initialization_run'])/'initial_condition.json');cachep=resolve(Path(identity['source_cache_run'])/'lio_cache.npz')
   assert sha(gnssp)==identity['gnss_sha256'] and sha(cachep)==identity['source_cache_sha256'] and sha(icp)==identity['initialization_sha256']
   for p,digest in row['provenance']['input_SHA'].items():assert sha(resolve(ROOT/p))==digest,'old source/result changed: '+p
   assert sha(run/'backend_resolved.json')==row['provenance']['config_SHA']
   provenance.append({'route':route,'method':method,'case':case,'role':item['role'],'same_bag_sensitivity':item['repeat'],'archived_event_source':str(ROOT/item['folder']/'event_results.json.gz'),'archived_event_SHA':sha(ROOT/item['folder']/'event_results.json.gz'),'backend_run':str(run),'source_commit':read_json(run/'manifest.json').get('source_commit'),'run_manifest_SHA':sha(run/'manifest.json'),'backend_identity_SHA':sha(run/'backend_identity.json'),'config_SHA':sha(run/'backend_resolved.json'),'cache_SHA':identity['source_cache_sha256'],'initialization_SHA':identity['initialization_sha256'],'GNSS_SHA':identity['gnss_sha256'],'trajectory_SHA':sha(run/'trajectory.csv'),'updates_SHA':sha(run/'per_update.jsonl'),'reference_SHA':sha(c['reference_path']),'S10_evaluator_SHA':sha(__file__),'metric_version':'inherited10Hz/full post90 and180/three-event macro/accepted-flag C180'})
   if case=='natural':continue
   grid,error=trajectory_errors(route,run);u=updates(str(run));gnss=load_gnss(gnssp);nat=load_gnss(c['stress']/'natural.csv');byid={int(r[0]):r for r in nat};injected={int(g[0]) for g in gnss if np.linalg.norm(g[2:5]-byid[int(g[0])][2:5])>1e-8};me=[]
   for i,event in enumerate(events(route,case)):
    returned=float(gnss[gnss[:,1]>=event['recovery_start_sow']][0,1]);assert returned==row['events'][i]['t_return_sow']
    delay,available,firstid=clocks(u,returned);end=returned+event['fault_parameters'].get('bias_hold_s',0);ids={int(g[0]) for g in gnss if returned<=g[1]<end and int(g[0]) in injected};accepted=sum(x['accepted'] for x in u if x['original_gnss_id'] in ids)
    w90=window(grid,error,returned,90);w180=window(grid,error,returned,180);old=original[(method,case,i)];oldval=float(old['RMSE_90']) if old['RMSE_90'] else None;delta=abs(w90['RMSE']-oldval) if oldval is not None else None
    if delta is not None:maxdiff=max(maxdiff,delta);assert delta<1e-11
    assert delay==(float(old['T_admit_s']) if old['T_admit_s'] else None) and accepted==int(old['injected_rows_accepted']) and len(ids)==int(old['injected_rows_exposed'])
    e={'route':route,'cache_label':item['cache_label'],'role':item['role'],'same_bag_sensitivity':item['repeat'],'method':method,'case':case,'event':i,'direction':['N','E','NE'][i],'return_sow':returned,'RMSE_90_m':w90['RMSE'],'RMSE_180_m':w180['RMSE'],'P95_90_m':w90['P95'],'Max_90_m':w90['Max'],'coverage_90':w90['coverage'],'coverage_180':w180['coverage'],'T_admit_s':delay,'T_available_bound_s':available,'admission_status':'C180' if delay is None else 'OBSERVED','first_accepted_original_id':firstid,'injected_accepted':accepted,'injected_exposed':len(ids),'archived_RMSE_90_m':oldval,'independent_absolute_difference_m':delta,'backend_run':str(run),'config_SHA':sha(run/'backend_resolved.json'),'cache_SHA':identity['source_cache_sha256']};eventrows.append(e);me.append(e)
   assert len(me)==3;percase[case]=me
  clean=percase['loss30_normal'];d=[e['T_admit_s'] for e in clean];avail=[e['T_available_bound_s'] for e in clean];coverage=all(e['coverage_90']==1 and e['coverage_180']==1 for es in percase.values() for e in es)
  for case in ['loss30_bias3','loss30_bias10']:
   es=percase[case];evidence.append({'route':route,'role':item['role'],'same_bag_sensitivity':item['repeat'],'method':method,'case':case,'RMSE_90_macro_m':macro([e['RMSE_90_m'] for e in es]),'RMSE_180_macro_m':macro([e['RMSE_180_m'] for e in es]),'each_event_90_m':json.dumps([e['RMSE_90_m'] for e in es]),'each_event_180_m':json.dumps([e['RMSE_180_m'] for e in es]),'natural_RMSE_m':natural[method],'natural_cap_m':cap,'clean_max_admit_s':max(d) if all(t is not None for t in d) else None,'clean_admit_each_s':json.dumps(d),'clean_available_bound_each_s':json.dumps(avail),'clean_censored_events':sum(t is None for t in d),'service_cost_qualified':qualified(natural[method],cap,d,coverage),'injected_accepted':sum(e['injected_accepted'] for e in es),'injected_exposed':sum(e['injected_exposed'] for e in es),'biased_admit_each_s':json.dumps([e['T_admit_s'] for e in es]),'coverage_complete':coverage})
 # Verify single-factor configuration and same input/init/cache for every retained case.
 for case in CASES+['natural']:
  p=item['rows'][('P',case)];n=item['rows'][('P_without_anchor',case)];pc=read_json(resolve(p['backend'])/'backend_resolved.json');nc=read_json(resolve(n['backend'])/'backend_resolved.json');diff=[k for k in set(pc)|set(nc) if pc.get(k)!=nc.get(k)];assert diff==['method']
  pi=read_json(resolve(p['backend'])/'backend_identity.json');ni=read_json(resolve(n['backend'])/'backend_identity.json');assert all(pi[k]==ni[k] for k in ['gnss_sha256','initialization_sha256','source_cache_sha256','A_NED_local','initial_lio_position'])
  checks.append({'route':route,'case':case,'configuration_difference':diff,'same_data_init_cache_alignment':True,'single_factor_dispatch_source':'experiments/s9/street00/run_candidate.py: extra_manager use_anchor=method!=P_without_anchor; same decay/check_motion and class','P_natural_equals_no_anchor':natural['P']==natural['P_without_anchor']})
 print(json.dumps({'route':route,'event_rows':len(eventrows),'largest_RMSE_discrepancy_m':maxdiff}),flush=True)
for e in evidence:
 n=next(r for r in evidence if r['route']==e['route'] and r['case']==e['case'] and r['method']=='P_without_anchor');e['P_vs_no_anchor_fraction']=improvement(e['RMSE_90_macro_m'],n['RMSE_90_macro_m']) if e['method']=='P' else None
csv_write(OUT/'evidence_matrix.csv',evidence);csv_write(OUT/'independent_event_table.csv',eventrows);json_write(OUT/'evidence_matrix.json',evidence);json_write(OUT/'event_table.json',eventrows);json_write(OUT/'manifest.json',{'analysis':'S10 post-hoc; not new confirmatory test','base_S9_commit':BASE,'routes':ROUTES,'methods':METHODS,'cases':CASES,'all_pair_provenance':provenance,'single_factor_checks':checks,'max_independent_RMSE_discrepancy_m':maxdiff,'source_data_traced':True,'all_six_routes_and_same_bag_repeat_retained':True,'script_SHA':sha(__file__),'common_SHA':sha(ROOT/'experiments/s10/common.py')})
lines=['# A evidence matrix','', 'Read-only recomputation from archived trajectories and raw accepted logs, full inherited10Hz grids, all six routes plus a separately labeled same-bag repeat, all19 policies. No new frontend/backend run or tuning. S10 is post-hoc and does not replace original10m primary evaluation.','',f'1197 event/case/method records; largest independent RMSE discrepancy {maxdiff:.17g}m. Every source/config/cache/init/input/trajectory/log/reference identity retained in manifest.json. P/no-anchor config differs only method dispatch, whose sole relevant mechanism switch is use_anchor; data, initial state, cache and alignment are equal.','', '|Route|P3m macro|No-anchor|Fraction improvement|Natural/cap|Clean max|Qualified|','|---|---:|---:|---:|---|---|---|']
for route in catalog():
 p=next(e for e in evidence if e['route']==route and e['method']=='P' and e['case']=='loss30_bias3');n=next(e for e in evidence if e['route']==route and e['method']=='P_without_anchor' and e['case']=='loss30_bias3');lines.append(f"|{route}|{p['RMSE_90_macro_m']:.9f}|{n['RMSE_90_macro_m']:.9f}|{p['P_vs_no_anchor_fraction']:.9f}|{p['natural_RMSE_m']:.9f}/{p['natural_cap_m']:.9f}|{p['clean_max_admit_s']}|{p['service_cost_qualified']}|")
(OUT/'EVIDENCE_MATRIX.md').write_text('\n'.join(lines)+'\n')
