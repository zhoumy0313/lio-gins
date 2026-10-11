#!/usr/bin/env python3
"""Natural B0–B6 at identical observed receiver epochs; explicit point conventions."""
import argparse,csv,hashlib,json,os,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.evaluation.reference import horizontal_metrics
p=argparse.ArgumentParser();p.add_argument('screen_run');p.add_argument('B1_evaluation');a=p.parse_args();out=Path(os.environ['LIO_GINS_RUN_DIR']);screen=Path(a.screen_run).resolve();b1=Path(a.B1_evaluation).resolve();s=json.loads((screen/'selected_baselines.json').read_text());b=json.loads((b1/'metrics.json').read_text())
if b['sequence']!='building00' or b['role']!='development':raise ValueError('heldout table closed')
raw=np.loadtxt(b1/'raw_GNSS_epoch_errors.csv',delimiter=',',skiprows=1);times=raw[:,0];records=[];sources=[screen/'selected_baselines.json',b1/'metrics.json',b1/'raw_GNSS_epoch_errors.csv']
records.append({'method':'B0','reference_point':'F9P_antenna','metrics':horizontal_metrics(raw[:,1:4],len(times)),'source':str(b1),'note':'offline reference translated to antenna using reference attitude; not an online oracle correction'})
for method in ['B1','B2','B3','B4','B5','B6']:
    run=b1 if method=='B1' else Path(next(r['evaluation'] for r in s['complete_selected'][method] if r['case']=='natural'))
    file=run/'per_epoch.csv';v=np.loadtxt(file,delimiter=',',skiprows=1);j=np.searchsorted(v[:,0],times);left=np.clip(j-1,0,len(v)-1);right=np.clip(j,0,len(v)-1);idx=np.where(abs(v[left,0]-times)<=abs(v[right,0]-times),left,right)
    valid=abs(v[idx,0]-times)<=1e-8;errors=v[idx,7:10].copy();errors[~valid]=np.nan
    np.savetxt(out/(method+'_receiver_epoch_errors.csv'),np.column_stack([times,errors,valid]),delimiter=',',header='sow,error_N,error_E,error_D,output_time_matched',comments='')
    records.append({'method':method,'reference_point':'ADIS_center','metrics':horizontal_metrics(errors,len(times)),'source':str(run),'note':'same 1200 observed epochs; match integer tick with <=10ns floating serialization allowance'});sources.append(file)
result={'role':'development','sequence':'building00','experiment_kind':'natural','expected_receiver_epochs':len(times),'time_range_sow':[float(times[0]),float(times[-1])],'records':records,'reference_point_limit':'B0 receiver antenna; B1-B6 ADIS center. Do not treat point difference as method effect; contribution comparison uses same-input B3-B6.', 'timing_scope':'offline accuracy only','input_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},'heldout_opened':False}
(out/'receiver_epoch_table.json').write_text(json.dumps(result,indent=2)+'\n')
with (out/'receiver_epoch_table.csv').open('w') as f:
    w=csv.writer(f);w.writerow(['method','point','RMSE_m','P95_m','max_m','coverage','epochs','evaluation_run'])
    for r in records:m=r['metrics'];w.writerow([r['method'],r['reference_point'],m['horizontal_rmse_m'],m['horizontal_p95_m'],m['horizontal_max_m'],m['coverage'],m['samples_expected'],r['source']])
print(json.dumps(result,indent=2))
