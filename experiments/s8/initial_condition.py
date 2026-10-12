#!/usr/bin/env python3
"""Isolated single-reference-epoch initializer; development only before freeze."""
import argparse,hashlib,json,os,sys
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from src.adapters.geodesy import llh_to_ecef,ecef_to_ned_rotation
from gate import technical_access as verify_access,technical_opening as record_opening,check_raw_identity
root=Path(__file__).resolve().parents[2];out=Path(os.environ['LIO_GINS_RUN_DIR'])
p=argparse.ArgumentParser();p.add_argument('--sequence',choices=['building01'],default='building01');p.add_argument('--freeze');a=p.parse_args();seq=a.sequence;role='s8_prospective_heldout';access=verify_access(seq,role,a.freeze);record_opening(access,'controlled_first_reference_epoch_initialization')
protocol=json.loads((root/'configs/initialization_protocol.json').read_text())
loc=json.loads((root/'configs/data_locations.json').read_text());data=root/loc['dataset_root']/seq
refpath=data/(seq+'_groundtruth.nav')
for original in [refpath,data/(seq+'_F9P_GNSS.pos'),data/(seq+'_ADIS16465_IMU.txt')]:check_raw_identity(access,original)
with refpath.open() as f:row=np.fromstring(f.readline(),sep=' ')
if row.shape!=(10,) or not np.isfinite(row).all():raise ValueError('invalid first reference epoch; do not search by performance')
t=float(row[0]);vel=row[4:7];att=row[7:10];r=Rotation.from_euler('ZYX',att[::-1],degrees=True).as_matrix()
gnss=np.loadtxt(data/(seq+'_F9P_GNSS.pos'));valid=np.isfinite(gnss).all(axis=1)&(gnss[:,4:7]>0).all(axis=1)&(gnss[:,0]<=t)
ids=np.flatnonzero(valid)
if not len(ids):raise ValueError('no causally available initial GNSS')
gid=int(ids[-1]);g=gnss[gid];lever=np.array([0,-.07,-.365]);delta=vel*(t-g[0])-r@lever
initial_ecef=llh_to_ecef(g[1:4])+ecef_to_ned_rotation(g[1:4]).T@delta
# Fixed-point WGS84 inverse, only used on a finite mid-latitude GNSS seed.
def ecef_to_llh(xyz):
    x,y,z=xyz;p=np.hypot(x,y);lon=np.arctan2(y,x);e2=6.6943799901413165e-3;lat=np.arctan2(z,p*(1-e2))
    for _ in range(10):
        n=6378137/np.sqrt(1-e2*np.sin(lat)**2);h=p/np.cos(lat)-n;lat=np.arctan2(z,p*(1-e2*n/(n+h)))
    n=6378137/np.sqrt(1-e2*np.sin(lat)**2);return np.array([np.rad2deg(lat),np.rad2deg(lon),p/np.cos(lat)-n])
llh=ecef_to_llh(initial_ecef)
if np.linalg.norm(llh_to_ecef(llh)-initial_ecef)>1e-5:raise ValueError('inverse geodesy roundtrip failure')
imu=np.loadtxt(data/(seq+'_ADIS16465_IMU.txt'));ii=int(np.searchsorted(imu[:,0],t));native_t=float(imu[ii,0]);dt=native_t-t
if not 0<=dt<=.006:raise ValueError('initial epoch not covered by expected IMU rate')
native_llh=ecef_to_llh(initial_ecef+ecef_to_ned_rotation(llh).T@(vel*dt))
identity={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [refpath,data/(seq+'_F9P_GNSS.pos'),data/(seq+'_ADIS16465_IMU.txt'),root/'configs/initialization_protocol.json']}
ic={'protocol':protocol,'sequence':seq,'role':role,'reference_state_rows_read':1,'reference_row_index':0,'reference_epoch_sow':t,'reference_initial_local_NED_m':row[1:4].tolist(),'initvel_NED_mps':vel.tolist(),'initatt_rpy_deg':att.tolist(),'R_NED_body_initial':r.tolist(),'origin_ADIS_llh_deg_m':llh.tolist(),'initial_F9P_row_id':gid,'initial_F9P_sow':float(g[0]),'initial_F9P_std_NED_m':np.maximum(g[4:7],protocol['GNSS_std_floor_NED_m']).tolist(),'antenna_lever_FRD_m':lever.tolist(),'KF_native_start_sow':native_t,'KF_epoch_offset_s':dt,'KF_initpos_llh_deg_m':native_llh.tolist(),'input_sha256':identity,'read_future_reference_states':False,'no_absolute_origin_claim':True}
if access is not None:ic['freeze_id']=access['freeze_id']
(out/'initial_condition.json').write_text(json.dumps(ic,indent=2)+'\n');print(json.dumps(ic,indent=2))
