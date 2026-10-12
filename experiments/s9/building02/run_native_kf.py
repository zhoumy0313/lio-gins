#!/usr/bin/env python3
"""Unmodified pinned KF-GINS on development ADIS + F9P; no truth access."""
import argparse,hashlib,json,os,subprocess,sys,time
from pathlib import Path
import numpy as np
import yaml
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from gate import verify_native_access as verify_access,record_opening,check_raw_identity,check_frozen_input
p=argparse.ArgumentParser();p.add_argument('initialization_run');p.add_argument('--noise-scale',type=float,default=2.0);p.add_argument('--freeze');a=p.parse_args()
root=Path(__file__).resolve().parents[3];out=Path(os.environ['LIO_GINS_RUN_DIR']);ic=json.loads((Path(a.initialization_run)/'initial_condition.json').read_text())
seq=ic['sequence'];role=ic.get('role','development');access=verify_access(seq,role,a.freeze);record_opening(access,'native_GNSS_INS_baseline')
if ic['reference_state_rows_read']!=1:raise ValueError('wrong initialization')
if access is not None and a.noise_scale!=2:raise ValueError('heldout native noise is frozen at STD scale2')
protocol=json.loads((root/'configs/initialization_protocol.json').read_text())
if ic['protocol']!=protocol:raise ValueError('initialization protocol changed')
loc=json.loads((root/'configs/data_locations.json').read_text());data=root/loc['dataset_root']/seq
repo=root/'third_party/KF-GINS';commit=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
if commit!='8291a93e49de513fe9d21f819500d39082ded611' or subprocess.check_output(['git','-C',str(repo),'status','--porcelain'],text=True).strip():raise ValueError('KF-GINS differs from pinned clean source')
gnss=np.loadtxt(data/(seq+'_F9P_GNSS.pos'));valid=np.isfinite(gnss).all(axis=1)&(abs(gnss[:,1])<=90)&(abs(gnss[:,2])<=180)&(gnss[:,4:7]>0).all(axis=1)
if np.any(np.diff(gnss[:,0])<=0):raise ValueError('GNSS ordering requires explicit input decision')
clean=gnss[valid].copy();clean[:,4:7]=np.maximum(clean[:,4:7],protocol['GNSS_std_floor_NED_m'])
np.savetxt(out/'GNSS_F9P_common_floor.pos',clean,fmt='%.12f')
(out/'gnss_row_ids.json').write_text(json.dumps({'kept_original_row_ids':np.flatnonzero(valid).tolist(),'rejected_original_row_ids':np.flatnonzero(~valid).tolist(),'floor_m':protocol['GNSS_std_floor_NED_m']})+'\n')
config={'imupath':str(data/(seq+'_ADIS16465_IMU.txt')),'gnsspath':str(out/'GNSS_F9P_common_floor.pos'),'outputpath':str(out),'imudatalen':7,'imudatarate':200,'starttime':ic['KF_native_start_sow'],'endtime':-1,'initpos':ic['KF_initpos_llh_deg_m'],'initvel':ic['initvel_NED_mps'],'initatt':ic['initatt_rpy_deg'],'initposstd':ic['initial_F9P_std_NED_m'],'initvelstd':protocol['initial_velocity_std_mps'],'initattstd':protocol['initial_attitude_std_deg'],'imunoise':protocol['imunoise'],'antlever':ic['antenna_lever_FRD_m']}
for name in ['initgyrbias','initaccbias','initgyrscale','initaccscale']:config[name]=[0,0,0]
screen=json.loads((root/'configs/KF_noise_sensitivity.json').read_text())
if a.noise_scale not in screen['std_multipliers']:raise ValueError('undeclared noise sensitivity')
config['imunoise']=dict(config['imunoise'])
for key in screen['scaled_parameters']:config['imunoise'][key]=[v*a.noise_scale for v in config['imunoise'][key]]
path=out/'kf_gins_resolved.yaml';path.write_text(yaml.safe_dump(config,sort_keys=False));binary=repo/'bin/KF-GINS';check_frozen_input(access,binary);check_frozen_input(access,Path(a.initialization_run)/'initial_condition.json');start=time.monotonic();rc=subprocess.run([str(binary),str(path)],cwd=repo).returncode
(out/'baseline_identity.json').write_text(json.dumps({'method':'B1_KF_GINS_unmodified','sequence':seq,'role':role,'freeze_id':access['freeze_id'] if access else None,'noise_std_multiplier':a.noise_scale,'sensor_input':'ADIS16465_increment_F9P_SPP_common_floor','reference_access_online':False,'initialization_run':str(Path(a.initialization_run).resolve()),'protocol_id':protocol['protocol_id'],'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'wall_seconds_including_native_IO':time.monotonic()-start,'exit_code':rc,'strong_baseline_status':'fixed R1 STD-scale2 natural GNSS/INS transfer; no new-route tuning, not main gain denominator'},indent=2)+'\n')
sys.exit(rc)
