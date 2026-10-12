"""Read-only identity/time/interface audit. Never compares reference positions."""
import datetime,json,os,sys,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from src.adapters.sensor_text import load_sensor,audit_table,unix_to_gps
from src.adapters.rosbag_metadata import read_metadata,bounded_samples,decode_imu,decode_insprobe_imu,decode_pointcloud_layout,decode_navsatfix
OUT=Path(os.environ['LIO_GINS_RUN_DIR']);DATA=ROOT/'data/i2nav-dataset/building02'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 records=[]
 for suffix,schema in [('.bag','rosbag_v2'),('_ADIS16465_IMU.txt','adis_increment'),('_F9P_GNSS.pos','f9p_spp'),('_groundtruth.nav','reference_time_only'),('_trajectory.csv','tum_time_schema_only')]:
  p=DATA/('building02'+suffix);before=p.stat();print('Identity: '+p.name,flush=True)
  item={'filename':p.name,'path':str(p),'size_bytes':before.st_size,'sha256':sha(p),'mtime_ns':before.st_mtime_ns,'ctime_ns':before.st_ctime_ns,'schema':schema,'status':'PRESENT','performance_opened':False}
  assert p.stat().st_size==before.st_size and p.stat().st_mtime_ns==before.st_mtime_ns,'input changed during audit'
  if schema=='rosbag_v2':
   assert p.open('rb').read(13)==b'#ROSBAG V2.0\n'
   expected=json.loads((ROOT/'third_party/i2Nav-Robot/sha256sum/sha256sum.json').read_text())[p.name]
   assert item['sha256']==expected
   item['official_sha256']=expected
  elif schema in ['adis_increment','f9p_spp']:
   a=load_sensor(p,schema);item['metadata']=audit_table(a,schema)
   assert np.isfinite(a).all() and np.all(np.diff(a[:,0])>0)
   if schema=='f9p_spp':assert (abs(a[:,1])<=90).all() and (abs(a[:,2])<=180).all()
  else:
   # Parse row structure/nonfinite counts and TIME ONLY; no reference state comparison.
   times=[];nonfinite=0;columns=10 if schema=='reference_time_only' else 8
   with p.open() as f:
    for line in f:
     a=np.fromstring(line,sep=' ');assert a.shape==(columns,)
     nonfinite+=int(not np.isfinite(a).all());times.append(a[0])
   t=np.array(times);d=np.diff(t)
   item['metadata']={'rows':len(t),'columns':columns,'time_min':float(t[0]),'time_max':float(t[-1]),'duplicate_times':int((d==0).sum()),'backward_times':int((d<0).sum()),'max_gap_s':float(d.max()),'nonfinite_rows':nonfinite,'state_payload_used':False}
   assert nonfinite==0 and (d>=0).all()
   item['metadata']['duplicate_rule']='stable first original row at each time; no performance-based selection'
  records.append(item)
 bag=DATA/'building02.bag';meta=read_metadata(bag);samples=bounded_samples(bag,meta,{'/adi/adis16465/imu':256,'/insprobe/adis16465/imu':512,'/hesai/at128/points':20})
 imu=[decode_imu(d) for _,d in samples['/adi/adis16465/imu']];custom=[decode_insprobe_imu(d) for _,d in samples['/insprobe/adis16465/imu']];pc=[decode_pointcloud_layout(d) for _,d in samples['/hesai/at128/points']]
 text=load_sensor(DATA/'building02_ADIS16465_IMU.txt','adis_increment');week,sow=unix_to_gps(imu[0]['stamp']);t=np.array([unix_to_gps(i['stamp'])[1] for i in imu]);j=np.clip(np.searchsorted(text[:,0],t),0,len(text)-1);j=np.where(abs(text[np.maximum(j-1,0),0]-t)<abs(text[j,0]-t),np.maximum(j-1,0),j)
 custom_time=np.array([c['stamp'] for c in custom]);ci=np.searchsorted(custom_time,np.array([i['stamp'] for i in imu]));assert (ci<len(custom)).all();custom=[custom[k] for k in ci]
 inc=np.array([c['incremental_angles']+c['incremental_velocity'] for c in custom]);rates=np.array([i['angular_velocity']+i['linear_acceleration'] for i in imu]);obs=text[j,1:7];dt=np.diff(t)
 assert all(c['week']==week and abs(c['stamp']-i['stamp'])<1e-6 for c,i in zip(custom,imu))
 assert abs(inc-obs).max()<1e-8 and abs(t-text[j,0]).max()<1e-6
 assert abs(np.array([c['sow'] for c in custom])-t).max()<1e-6
 assert unix_to_gps(meta['end_unix'])[0]==week,'week rollover requires explicit adapter'
 cross={'gps_week':week,'gps_minus_utc_s':18,'first_sow':sow,'first_unix_utc':datetime.datetime.fromtimestamp(imu[0]['stamp'],datetime.timezone.utc).isoformat(),'custom_IMU_week':custom[0]['week'],'matching_policy':'match by exact standard header timestamp within 1e-6s; custom stream begins 21 rows earlier, no index pairing','samples':len(imu),'max_custom_increment_minus_text':float(abs(inc-obs).max()),'max_text_stamp_residual_s':float(abs(t-text[j,0]).max()),'max_rate_times_actual_dt_error_by_axis':abs(rates[1:]*dt[:,None]-obs[1:]).max(axis=0).tolist(),'max_rate_times_nominal_dt_error_by_axis':abs(rates*.005-obs).max(axis=0).tolist(),'pointcloud_samples':pc,'record_minus_header_imu_s':samples['/adi/adis16465/imu'][0][0]-imu[0]['stamp']}
 for item in records:
  if item['schema']=='tum_time_schema_only':
   item['metadata']['time_basis']='GPS_seconds_of_week';assert 0<=item['metadata']['time_min']<=item['metadata']['time_max']<604800
 gnss=load_sensor(DATA/'building02_F9P_GNSS.pos','f9p_spp');ref=next(r['metadata'] for r in records if r['schema']=='reference_time_only');common_end=min(ref['time_max'],text[-1,0]);start=max(ref['time_min'],float(text[0,0]),float(gnss[0,0]));support=[]
 protocol=json.loads((ROOT/'configs/development_experiment_protocol.json').read_text())
 for case in protocol['stress_cases']:
  for offset,direction in zip(protocol['event_starts_seconds_from_common_initial_epoch'],protocol['directions_NED']):
   k=int(np.searchsorted(gnss[:,0],start+offset));assert k<len(gnss)
   fault=float(gnss[k,0]);duration=case.get('duration_s',case.get('ramp_s',0)+case.get('hold_s',0))
   if case['kind']=='jump':duration=float(gnss[min(k+case['epochs']-1,len(gnss)-1),0]+1-fault)
   end=fault+duration;returned=gnss[np.searchsorted(gnss[:,0],end),0]
   good=fault-10>=start and returned+180<=common_end
   support.append({'case':case['id'],'offset_s':offset,'direction':direction,'fault_start_sow':fault,'t_return_sow':float(returned),'post180_supported':bool(good)})
 # Predeclared rule: unsupported events block opening the complete primary matrix.
 assert all(e['post180_supported'] for e in support),'fixed event windows unsupported; no performance-based replacements'
 manifest={'goal_id':'LIO-GINS-S9-MULTISCENARIO','sequence':'building02','role':'prospective_heldout_technical_audit','files':records,'bag_metadata':{k:v for k,v in meta.items() if k!='chunks'},'sensor_crosscheck':cross,'common_reference_sensor_range_sow':[start,float(common_end)],'fixed_event_support':support,'performance_opened':False,'reference_state_payload_used':False,'raw_read_only':True,'official_text_checksums_available':False,'extra_files_preserved':[p.name for p in DATA.iterdir() if p.name not in [r['filename'] for r in records]]}
 (OUT/'data_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'five_verified':True,'gps_week':week,'span_s':common_end-start,'events_supported':len(support)}))
if __name__=='__main__':main()
