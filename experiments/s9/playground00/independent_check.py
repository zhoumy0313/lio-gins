"""Independent NumPy-interp metrics review; does not import the main evaluator."""
import json,os,sys,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3];OUT=Path(os.environ['LIO_GINS_RUN_DIR']);analysis=Path(sys.argv[1]);rows=json.loads((analysis/'event_results.json').read_text());memo={};differences=[];clocks=0;exposure=0;windows=0
from gate import verify_access,record_opening
context=json.loads((ROOT/'artifacts/s9/playground00/technical_context.json').read_text());access=verify_access('playground00','s9_prospective_heldout',ROOT/context['freeze_relative_path'],ROOT/'configs/s9/P.json');record_opening(access,'offline_independent_recompute')
for row in rows:
    run=Path(row['backend']);identity=json.loads((run/'backend_identity.json').read_text());ic=json.loads((Path(identity['initialization_run'])/'initial_condition.json').read_text());seq=ic['sequence'];assert identity.get('sequence',seq)==seq
    if seq not in memo:
        ref=np.loadtxt(ROOT/'data/i2nav-dataset'/seq/(seq+'_groundtruth.nav'));meta=json.loads((ROOT/'artifacts/s9/playground00/data_manifest.json').read_text());sensor_end=next(f['metadata']['time_max'] for f in meta['files'] if f['filename']==seq+'_ADIS16465_IMU.txt');end=min(ref[-1,0],sensor_end);grid=np.arange(np.ceil(ic['reference_epoch_sow']*10),np.floor(end*10)+1)/10
        truth=np.column_stack([np.interp(grid,ref[:,0],ref[:,j]) for j in [1,2,3]]);assert np.max(np.diff(ref[:,0]))<.02;memo[seq]=(grid,truth)
    grid,truth=memo[seq];nav=np.loadtxt(run/'trajectory.csv',delimiter=',',skiprows=1);lookup={int(round(v[0]*10)):v for v in nav};values=np.vstack([lookup[int(round(t*10))][1:4] for t in grid]);assert np.isfinite(values).all();h=np.sqrt(np.sum((values[:,:2]-truth[:,:2])**2,axis=1));differences.append(abs(float(np.sqrt(np.mean(h**2)))-row['whole']['horizontal_RMSE_m']))
    logs=[json.loads(l) for l in (run/'per_update.jsonl').read_text().splitlines()];assert len(logs)==len({u['original_gnss_id'] for u in logs})
    stress=Path(identity['gnss_source']).parent;natural=np.loadtxt(stress/'natural.csv',delimiter=',',skiprows=1);gnss=np.loadtxt(identity['gnss_source'],delimiter=',',skiprows=1);nmap={int(g[0]):g for g in natural};injection_ids={int(g[0]) for g in gnss if not np.allclose(g[2:5],nmap[int(g[0])][2:5],rtol=0,atol=1e-8)};manifest=json.loads((stress/'event_manifest.json').read_text());case=next(c for c in manifest['cases'] if c['id']==row['case'])
    for e,event in zip(row['events'],case['events']):
        returned=e['t_return_sow'];assert returned==min(g[1] for g in gnss if g[1]>=event['recovery_start_sow']);actual=sorted(u['measurement_sow'] for u in logs if u['accepted'] and returned<=u['measurement_sow']<returned+180);delay=actual[0]-returned if actual else None;assert delay==e['T_admit_s'];first=min((u for u in logs if u['accepted'] and returned<=u['measurement_sow']<returned+180),key=lambda u:u['measurement_sow'],default=None);assert e['T_available_bound_s']==(first['available_sow']-returned if first else None);assert ('OBSERVED' if actual else 'CENSORED')==e['status'];clocks+=1
        for duration in [10,30,60,90,180]:
            values=h[(grid>=returned-1e-8)&(grid<returned+duration-1e-8)];assert len(values)==duration*10;rmse=float(np.sqrt(np.mean(values**2)));differences.append(abs(rmse-e['post_return'][str(duration)]['horizontal_RMSE_m']));windows+=1
        end=event['recovery_start_sow']+event['fault_parameters'].get('bias_hold_s',0) if event['fault_parameters'].get('bias_hold_s',0) else event['fault_end_sow'];ids={int(g[0]) for g in gnss if event['fault_start_sow']<=g[1]<end and int(g[0]) in injection_ids};count=sum(u['accepted'] for u in logs if u['original_gnss_id'] in ids);assert count==e['injected_rows_accepted'] and len(ids)==e['injected_rows_exposed'];exposure+=1
maxdiff=max(differences);result={'pairs':len(rows),'independent_error_values_checked':len(differences),'windows_checked':windows,'accepted_clocks_checked':clocks,'injection_exposure_checks':exposure,'max_absolute_error_difference_m':maxdiff,'passed':maxdiff<1e-10,'main_evaluator_imported':False,'analysis_SHA':hashlib.sha256((analysis/'event_results.json').read_bytes()).hexdigest()}
(OUT/'independent_check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));assert result['passed']
