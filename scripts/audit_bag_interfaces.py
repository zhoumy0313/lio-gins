#!/usr/bin/env python3
"""Metadata of both bags; bounded sensor interface checks on development only."""
import datetime,json,os,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.adapters.rosbag_metadata import read_metadata,bounded_samples,decode_imu,decode_insprobe_imu,decode_pointcloud_layout
from src.adapters.sensor_text import unix_to_gps,load_sensor
root=Path(__file__).resolve().parents[1];out=Path(os.environ['LIO_GINS_RUN_DIR']);loc=json.loads((root/'configs/data_locations.json').read_text());reports={}
for seq in ['building00','parking00']:
    bag=root/loc['dataset_root']/seq/(seq+'.bag');meta=read_metadata(bag)
    reports[seq]={k:v for k,v in meta.items() if k!='chunks'}
    reports[seq]['role']='development' if seq=='building00' else 'heldout_closed'
    reports[seq]['performance_opened']=False
    print(seq,'indexed metadata read',flush=True)
    if seq=='building00':
        samples=bounded_samples(bag,meta,{'/adi/adis16465/imu':256,'/insprobe/adis16465/imu':256,'/hesai/at128/points':20})
        imu=[decode_imu(d) for t,d in samples['/adi/adis16465/imu']];pc=[decode_pointcloud_layout(d) for t,d in samples['/hesai/at128/points']]
        text=load_sensor(bag.parent/(seq+'_ADIS16465_IMU.txt'),'adis_increment')
        week,sow=unix_to_gps(imu[0]['stamp']);t=np.array([unix_to_gps(i['stamp'])[1] for i in imu]);j=np.searchsorted(text[:,0],t);j=np.clip(j,0,len(text)-1)
        j=np.where(abs(text[np.maximum(j-1,0),0]-t)<abs(text[j,0]-t),np.maximum(j-1,0),j)
        residual=t-text[j,0];dt=np.r_[np.nan,np.diff(t)]
        rates=np.array([i['angular_velocity']+i['linear_acceleration'] for i in imu]);observed=text[j,1:7]
        # Both actual dt and documented nominal sampling interval are checked, not chosen by truth fit.
        err_actual=rates[1:]*dt[1:,None]-observed[1:]
        err_nominal=rates*.005-observed
        custom=[decode_insprobe_imu(d) for t,d in samples['/insprobe/adis16465/imu']]
        if any(abs(c['stamp']-i['stamp'])>1e-6 for c,i in zip(custom,imu)):raise ValueError('custom/standard IMU timestamps disagree')
        increments=np.array([c['incremental_angles']+c['incremental_velocity'] for c in custom])
        reports[seq]['sensor_crosscheck']={'bounded_sample_count':len(imu),'gps_week':week,'first_sow':sow,'first_unix_utc':datetime.datetime.fromtimestamp(imu[0]['stamp'],datetime.timezone.utc).isoformat(),'gps_minus_utc_s':18,'max_text_stamp_residual_s':float(abs(residual).max()),'median_imu_dt_s':float(np.nanmedian(dt)),'max_rate_times_actual_dt_error_by_axis':abs(err_actual).max(axis=0).tolist(),'max_rate_times_nominal_dt_error_by_axis':abs(err_nominal).max(axis=0).tolist(),'first_imu_frame':imu[0]['frame_id'],'first_imu':imu[0],'pointcloud_samples':pc,'record_minus_header_first_imu_s':samples['/adi/adis16465/imu'][0][0]-imu[0]['stamp']}
        reports[seq]['sensor_crosscheck'].update(custom_IMU_week=custom[0]['week'],max_custom_increment_minus_text_by_axis=abs(increments-observed).max(axis=0).tolist(),max_custom_sow_minus_text_s=float(np.max(abs(np.array([c['sow'] for c in custom])-text[j,0]))))
        if np.max(abs(increments-observed))>1e-8:raise ValueError('raw bag/text incremental IMU mismatch')
(out/'bag_interfaces.json').write_text(json.dumps(reports,indent=2)+'\n')
print(json.dumps({s:{'connections':v['connection_count'],'chunks':v['chunk_count'],'span_s':v['end_unix']-v['start_unix']} for s,v in reports.items()},indent=2))
