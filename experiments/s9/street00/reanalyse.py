"""Offline R2 evaluator: fixed grids, real accepted flags, censoring, all events.
The estimator never imports this file or reads the reference or injection labels.
"""
import argparse,csv,hashlib,json,os,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from src.evaluation.reference import load_i2nav_local_ned,interpolate_with_gaps
from gate import verify_access,record_opening
CONTEXT=json.loads((ROOT/'artifacts/s9/street00/technical_context.json').read_text()) if (ROOT/'artifacts/s9/street00/technical_context.json').exists() else {}
ROUTES={'street00':tuple(CONTEXT[k] for k in ['cache','initialization','stress'])} if CONTEXT else {}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def accepted_clock(updates,returned,horizon=180):
    candidates=[u for u in updates if returned<=u['measurement_sow']<returned+horizon and u['accepted'] is True]
    first=min(candidates,key=lambda u:u['measurement_sow']) if candidates else None
    return {'status':'OBSERVED' if first else 'CENSORED','T_admit_s':first['measurement_sow']-returned if first else None,'T_available_bound_s':first['available_sow']-returned if first else None,'censor_bound_s':horizon,'first_gnss_id':first['original_gnss_id'] if first else None,'first_correction_m':first['correction_norm_m'] if first else None}
def full_window(grid,errors,start,duration):
    selected=(grid>=start-1e-8)&(grid<start+duration-1e-8);h=np.linalg.norm(errors[selected,:2],axis=1);expected=int(round(duration*10));valid=np.isfinite(h)
    complete=len(h)==expected and valid.all()
    return {'status':'COMPLETE' if complete else 'PARTIAL_OR_MISSING','samples_expected':expected,'samples_present':len(h),'samples_valid':int(valid.sum()),'coverage':float(valid.sum()/expected),'horizontal_RMSE_m':float(np.sqrt(np.mean(h*h))) if complete else None,'horizontal_P95_m':float(np.percentile(h,95)) if complete else None,'horizontal_Max_m':float(np.max(h)) if complete else None}
def error_recovery(grid,errors,returned,threshold=3,duration=5,timeout=90):
    h=np.linalg.norm(errors[:,:2],axis=1);ix=np.flatnonzero((grid>=returned)&(grid<=returned+timeout));needed=int(round(duration*10))+1
    for k in range(max(0,len(ix)-needed+1)):
        ids=ix[k:k+needed]
        if np.all(np.isfinite(h[ids])&(h[ids]<=threshold)):return {'status':'OBSERVED','time_s':float(grid[ids[0]]-returned)}
    return {'status':'CENSORED','time_s':None,'censor_bound_s':timeout}
def evaluate(row,reference_cache):
    run=Path(row['backend']);identity=json.loads((run/'backend_identity.json').read_text());cache=row['cache'];_,init,stress=ROUTES[cache];stress=ROOT/'outputs'/stress
    eventpath=stress/'event_manifest.json';manifest=json.loads(eventpath.read_text());case=next(c for c in manifest['cases'] if c['id']==row['case']);icpath=ROOT/'outputs'/init/'initial_condition.json';ic=json.loads(icpath.read_text());seq=ic['sequence'];refpath=ROOT/'data/i2nav-dataset'/seq/(seq+'_groundtruth.nav')
    data=Path(case['data_path']);assert sha(data)==case['sha256']==identity['gnss_sha256']
    assert sha(run/'backend_resolved.json')==hashlib.sha256((json.dumps(row['config'],indent=2)+'\n').encode()).hexdigest()
    if cache not in reference_cache:
        ref=load_i2nav_local_ned(refpath);rawmanifest=json.loads((ROOT/'artifacts/s9/street00/data_manifest.json').read_text());end=min(next(f['metadata']['time_max'] for f in rawmanifest['files'] if f['filename']==seq+'_ADIS16465_IMU.txt'),ref[-1,0]);start=ic['reference_epoch_sow'];grid=np.arange(int(np.ceil(start*10)),int(np.floor(end*10))+1)/10
        truth,rv=interpolate_with_gaps(ref[:,0],ref[:,1:4],grid,ic['protocol']['reference_max_interpolation_gap_s']);reference_cache[cache]=(grid,truth,rv)
    grid,truth,rv=reference_cache[cache];nav=np.loadtxt(run/'trajectory.csv',delimiter=',',skiprows=1,ndmin=2);assert nav.shape[1]==7 and np.all(np.diff(nav[:,0])>0)
    j=np.searchsorted(nav[:,0],grid);idx=np.clip(j,0,len(nav)-1);matches=(j<len(nav))&(np.abs(nav[idx,0]-grid)<1e-8)&(nav[idx,6]==1);positions=nav[idx,1:4].copy();positions[~matches]=np.nan;errors=positions-truth
    updates=[json.loads(line) for line in (run/'per_update.jsonl').read_text().splitlines()];ids=[u['original_gnss_id'] for u in updates];assert len(ids)==len(set(ids));assert all(u['available_sow']>=u['measurement_sow'] for u in updates)
    h=np.linalg.norm(errors[:,:2],axis=1);complete=np.isfinite(h).all();whole={'samples_expected':len(grid),'samples_valid':int(np.isfinite(h).sum()),'coverage':float(np.isfinite(h).mean()),'horizontal_RMSE_m':float(np.sqrt(np.mean(h*h))) if complete else None,'horizontal_P95_m':float(np.percentile(h,95)) if complete else None,'horizontal_Max_m':float(np.max(h)) if complete else None}
    gnss=np.loadtxt(data,delimiter=',',skiprows=1,ndmin=2);natural=np.loadtxt(stress/'natural.csv',delimiter=',',skiprows=1,ndmin=2);nat_by_id={int(r[0]):r for r in natural};injected={int(r[0]) for r in gnss if np.linalg.norm(r[2:5]-nat_by_id[int(r[0])][2:5])>1e-8};events=[]
    for number,event in enumerate(case['events']):
        start=event['recovery_start_sow'];remaining=gnss[gnss[:,1]>=start];assert len(remaining)>0;returned=float(remaining[0,1]);clock=accepted_clock(updates,returned)
        bias_hold=event['fault_parameters'].get('bias_hold_s',0);exposure_end=start+bias_hold if bias_hold else event['fault_end_sow']
        exposed_ids={int(r[0]) for r in gnss if event['fault_start_sow']<=r[1]<exposure_end and int(r[0]) in injected};injected_updates=[u for u in updates if u['original_gnss_id'] in exposed_ids];accepted=[u for u in injected_updates if u['accepted']];post=[u for u in updates if returned<=u['measurement_sow']<returned+180 and u['accepted']]
        bias_end=start+bias_hold
        after_bias=accepted_clock(updates,bias_end,90) if bias_hold else None
        row_event={'event_index':number,'fault_start_sow':event['fault_start_sow'],'t_return_sow':returned,**clock,'actual_post180_updates':len(post),'maximum_post180_correction_m':max([u['correction_norm_m'] for u in post],default=0),'injected_rows_exposed':len(exposed_ids),'injected_rows_logged':len(injected_updates),'injected_rows_accepted':len(accepted),'injected_acceptance_fraction':len(accepted)/len(exposed_ids) if exposed_ids else None,'post_return':{str(w):full_window(grid,errors,returned,w) for w in [10,30,60,90,180]},'offline_error_recovery':error_recovery(grid,errors,returned),'first_update_after_bias_removed':after_bias,'bias_hold_s':bias_hold,'risk_definition':'artificial injected-row acceptance, not real GNSS error probability'}
        events.append(row_event)
    provenance={'backend_run':str(run),'cache_SHA':identity['source_cache_sha256'],'config_SHA':sha(run/'backend_resolved.json'),'input_SHA':{str(p.relative_to(ROOT)):sha(p) for p in [run/'trajectory.csv',run/'per_update.jsonl',run/'backend_identity.json',data,eventpath,icpath,refpath]},'evaluator_SHA':sha(__file__),'S9_role':'prospective_heldout','initialization_conditioned':True}
    parity=None
    if row.get('evaluation'):
        original=json.loads((Path(row['evaluation'])/'metrics.json').read_text());parity=abs(whole['horizontal_RMSE_m']-original['metrics']['horizontal_rmse_m'])
        assert parity<1e-12,parity
    return {**row,'whole':whole,'events':events,'provenance':provenance,'original_whole_RMSE_absolute_difference_m':parity},(grid,errors)
def main():
    access=verify_access('street00','s9_prospective_heldout',ROOT/CONTEXT['freeze_relative_path'],ROOT/'configs/s9/P.json');record_opening(access,'offline_independent_precision_evaluation')
    parser=argparse.ArgumentParser();parser.add_argument('index');args=parser.parse_args();out=Path(os.environ['LIO_GINS_RUN_DIR']);index=json.loads(Path(args.index).read_text());cache={};results=[];epoch_dir=out/'per_epoch';epoch_dir.mkdir()
    for row in index:
        result,(grid,errors)=evaluate(row,cache);results.append(result)
        np.savetxt(epoch_dir/('_'.join([row['cache'],row['method'],row['case']])+'.csv'),np.column_stack([grid,errors]),delimiter=',',header='sow,error_N,error_E,error_D',comments='')
    methods=sorted({r['method'] for r in index});expected=len(methods)*len(ROUTES)*8;keys={(r['cache'],r['method'],r['case']) for r in results};assert len(keys)==len(results);assert len(results)==expected,(len(results),expected)
    (out/'event_results.json').write_text(json.dumps(results,indent=2,allow_nan=False)+'\n');summary=[];flat=[]
    for r in results:
        for e in r['events']:flat.append({'cache':r['cache'],'method':r['method'],'case':r['case'],'event':e['event_index'],'T_admit_s':e['T_admit_s'],'status':e['status'],'T_available_bound_s':e['T_available_bound_s'],'injected_rows_accepted':e['injected_rows_accepted'],'injected_rows_exposed':e['injected_rows_exposed'],**{'RMSE_'+w:e['post_return'][w]['horizontal_RMSE_m'] for w in ['10','30','60','90','180']},'backend_run':r['backend'],'config_SHA':r['provenance']['config_SHA'],'cache_SHA':r['provenance']['cache_SHA']})
    for cachelabel in ROUTES:
        robust_nat=[r['whole']['horizontal_RMSE_m'] for r in results if r['cache']==cachelabel and r['case']=='natural' and r['method'] in ['B4','B5','B6']];best=min(robust_nat);cap=best+max(.02*best,.05)
        for method in methods:
            rows={r['case']:r for r in results if r['cache']==cachelabel and r['method']==method};clean=rows['loss30_normal']['events'];biased=rows['loss30_bias10']['events'];delays=[e['T_admit_s'] for e in clean];available=[e['T_available_bound_s'] for e in clean];nat=rows['natural']['whole']['horizontal_RMSE_m'];normal_ok=nat is not None and nat<=cap+1e-12
            summary.append({'cache':cachelabel,'method':method,'natural_RMSE_m':nat,'natural_cap_m':cap,'normal_cost_eligible':normal_ok,'clean_latency_max_s':max(delays) if all(t is not None for t in delays) else None,'clean_censored_events':sum(t is None for t in delays),'clean_T_admit_each_s':delays,'clean_T_available_bound_each_s':available,'clean_deadline15_pass_count':sum(t is not None and t<=15+1e-8 for t in delays),'coverage_eligible':all(r['whole']['coverage']==1 and all(w['status']=='COMPLETE' for e in r['events'] for w in e['post_return'].values()) for r in rows.values()),'service_qualified':normal_ok and all(t is not None and t<=15+1e-8 for t in delays) and all(r['whole']['coverage']==1 and all(w['status']=='COMPLETE' for e in r['events'] for w in e['post_return'].values()) for r in rows.values()),'availability_bound_deadline15_pass_count':sum(t is not None and t<=15+1e-8 for t in available),'bias_accepted_rows':sum(e['injected_rows_accepted'] for e in biased),'bias_exposed_rows':sum(e['injected_rows_exposed'] for e in biased),'bias_censored_events':sum(e['status']=='CENSORED' for e in biased),**{'clean_RMSE_'+str(w)+'_m':float(np.mean([e['post_return'][str(w)]['horizontal_RMSE_m'] for e in clean])) if all(e['post_return'][str(w)]['horizontal_RMSE_m'] is not None for e in clean) else None for w in [10,30,60,90,180]},**{'bias_RMSE_'+str(w)+'_m':float(np.mean([e['post_return'][str(w)]['horizontal_RMSE_m'] for e in biased])) if all(e['post_return'][str(w)]['horizontal_RMSE_m'] is not None for e in biased) else None for w in [10,30,60,90,180]}})
    def write_csv(name,rows):
        with (out/name).open('w') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    write_csv('event_table.csv',flat);write_csv('summary_table.csv',summary);(out/'summary_table.json').write_text(json.dumps(summary,indent=2)+'\n')
    audit={'pairs':len(results),'expected_pairs':expected,'coverage_complete':all(r['whole']['coverage']==1 for r in results),'all_windows_complete':all(w['status']=='COMPLETE' for r in results for e in r['events'] for w in e['post_return'].values()),'inherited_RMSE_parity_max_m':max(r['original_whole_RMSE_absolute_difference_m'] or 0 for r in results),'right_censor_retained':True,'future_labels_online':False,'new_route_accessed':True,'role':'prospective_heldout','freeze_id':access['freeze_id']}
    (out/'analysis_audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit))
if __name__=='__main__':main()
