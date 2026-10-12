"""Bounded GNSS/text and text trajectory schema checks, no precision comparison."""
import json,os,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from src.adapters.rosbag_metadata import read_metadata,bounded_samples,decode_navsatfix,decode_insprobe_imu
from src.adapters.sensor_text import unix_to_gps
data=ROOT/'data/i2nav-dataset/building01';bag=data/'building01.bag';meta=read_metadata(bag);samples=bounded_samples(bag,meta,{'/ublox/f9p/fix':16,'/insprobe/adis16465/imu':16});g=np.loadtxt(data/'building01_F9P_GNSS.pos');llh=[];std=[];stamps=[];weeks=[]
for _,raw in samples['/ublox/f9p/fix']:
 fix=decode_navsatfix(raw);week,t=unix_to_gps(fix['stamp']);weeks.append(week);i=int(np.argmin(abs(g[:,0]-t)));stamps.append(abs(g[i,0]-t));llh.append(np.array(fix['llh_deg_m'])-g[i,1:4]);enu=np.diag(np.array(fix['covariance_ENU']).reshape(3,3));std.append(np.sqrt(enu[[1,0,2]])-g[i,4:7])
assert len(set(weeks))==1 and weeks[0]==json.loads((ROOT/'artifacts/s8/data_manifest.json').read_text())['sensor_crosscheck']['gps_week']
assert max(stamps)<=0.0005 and np.max(abs(np.array(llh)))<1e-4 and np.max(abs(np.array(std)))<1e-6
offsets=[]
for _,raw in samples['/insprobe/adis16465/imu']:
 c=decode_insprobe_imu(raw);offsets.append(c['week']*604800+c['sow']+315964800-c['stamp'])
assert np.max(abs(np.array(offsets)-18))<1e-6
norm_errors=[];lines=0
with (data/'building01_trajectory.csv').open() as f:
 for line in f:
  a=np.fromstring(line,sep=' ');assert a.shape==(8,);norm_errors.append(abs(np.linalg.norm(a[4:8])-1));lines+=1
assert max(norm_errors)<2e-6
result={'observed_GPS_minus_UTC_s':{'min':min(offsets),'max':max(offsets),'basis':'custom week/SOW minus ROS UNIX header, independently calculated'},'bounded_F9P_rows':16,'GPS_week':weeks[0],'max_stamp_text_residual_s':max(stamps),'text_SOW_serialization_bound_s':0.0005,'timestamp_policy':'F9P text SOW has 3 decimals; bag header retains sub-millisecond precision; backend uses unchanged text, no adjustment','max_llh_bag_text_by_axis':np.max(abs(np.array(llh)),axis=0).tolist(),'max_STD_NED_bag_text_by_axis':np.max(abs(np.array(std)),axis=0).tolist(),'covariance_order':'NavSatFix ENU diagonal reordered NED then sqrt; not fitted','trajectory_text_rows':lines,'trajectory_schema':'whitespace SOW,N,E,D,qx,qy,qz,qw; reference only, no position comparisons','max_serialized_quaternion_norm_error':max(norm_errors),'position_error_computed':False}
(Path(os.environ['LIO_GINS_RUN_DIR'])/'extra_interfaces.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
