#!/usr/bin/env python3
"""Offline development evaluation; shared initial translation, no trajectory fit."""
import argparse,hashlib,json,os,sys
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.adapters.geodesy import llh_to_ned
from src.adapters.research_access import verify_access,record_opening,check_raw_identity
from src.evaluation.reference import load_i2nav_local_ned,load_kf_gins_llh,interpolate_with_gaps,horizontal_metrics
p=argparse.ArgumentParser();p.add_argument('kf_run');p.add_argument('init_run');p.add_argument('--freeze');a=p.parse_args()
root=Path(__file__).resolve().parents[1];out=Path(os.environ['LIO_GINS_RUN_DIR']);ic=json.loads((Path(a.init_run)/'initial_condition.json').read_text())
seq=ic['sequence'];role=ic.get('role','development');access=verify_access(seq,role,a.freeze);record_opening(access,'offline_native_GNSS_INS_evaluation')
protocol=ic['protocol'];loc=json.loads((root/'configs/data_locations.json').read_text());data=root/loc['dataset_root']/seq;navpath=Path(a.kf_run)/'KF_GINS_Navresult.nav';refpath=data/(seq+'_groundtruth.nav')
nav=load_kf_gins_llh(navpath);ref=load_i2nav_local_ned(refpath);gnss=np.loadtxt(data/(seq+'_F9P_GNSS.pos'));imu_times=np.loadtxt(data/(seq+'_ADIS16465_IMU.txt'),usecols=0)
if np.any(np.diff(nav[:,1])<=0) or np.any(np.diff(ref[:,0])<=0):raise ValueError('nonmonotonic trajectory; explicit policy required')
origin=ic['origin_ADIS_llh_deg_m'];translation=np.array(ic['reference_initial_local_NED_m']);npos=llh_to_ned(nav[:,2:5],origin)+translation
start=ic['reference_epoch_sow'];end=min(ref[-1,0],imu_times[-1]);grid=np.arange(np.ceil(start*10)/10,np.floor(end*10)/10+.01,.1)
n,nvalid=interpolate_with_gaps(nav[:,1],npos,grid,protocol['KF_output_max_interpolation_gap_s']);r,rvalid=interpolate_with_gaps(ref[:,0],ref[:,1:4],grid,protocol['reference_max_interpolation_gap_s']);err=n-r
m=horizontal_metrics(err,len(grid));m['vertical_rmse_m']=float(np.sqrt(np.nanmean(err[:,2]**2)))
np.savetxt(out/'per_epoch.csv',np.column_stack([grid,n,r,err,nvalid,rvalid]),delimiter=',',header='sow,N,E,D,ref_N,ref_E,ref_D,error_N,error_E,error_D,output_available,reference_available',comments='')
g=gnss[(gnss[:,0]>=grid[0])&(gnss[:,0]<=grid[-1])];rg,vg=interpolate_with_gaps(ref[:,0],ref[:,1:10],g[:,0],.02)
rots=Rotation.from_euler('ZYX',rg[:,6:9][:,::-1],degrees=True).as_matrix();refantenna=rg[:,:3]+np.einsum('nij,j->ni',rots,np.array(ic['antenna_lever_FRD_m']))
gpos=llh_to_ned(g[:,1:4],origin)+translation;gerr=gpos-refantenna
np.savetxt(out/'raw_GNSS_epoch_errors.csv',np.column_stack([g[:,0],gerr,vg]),delimiter=',',header='sow,error_N,error_E,error_D,reference_available',comments='')
k1,_=interpolate_with_gaps(nav[:,1],npos,g[:,0],.02);same_epochs=horizontal_metrics(k1-rg[:,:3],len(g))
metrics={'sequence':seq,'role':role,'freeze_id':access['freeze_id'] if access else None,'experiment_kind':'natural_data','method':'B1_KF_GINS_unmodified_initial_run','initialization_protocol_id':protocol['protocol_id'],'initialization_run':str(Path(a.init_run).resolve()),'source_run':str(Path(a.kf_run).resolve()),'alignment':'one predetermined common initial translation; no fitted trajectory transform','quantity':'initial_position_conditioned_error_not_absolute_WGS84_accuracy','reference_point':'ADIS16465_center','metrics_10Hz':m,'B0_raw_F9P_SPP_1Hz_antenna_errors':horizontal_metrics(gerr,len(g)),'B0_reference_point_note':'raw GNSS is antenna; offline reference is transformed to antenna using reference attitude, never supplied to an estimator','B1_same_GNSS_epochs_ADIS_errors':same_epochs,'grid_sow_range':[float(grid[0]),float(grid[-1])],'grid_source':'predeclared initialization and input IMU/reference overlap, not output coverage','reference_AT128_dependency':'MM/INS reference shares AT128 information; not independent truth sensor','nav_rows':len(nav),'week_field_zero_placeholder':bool((nav[:,0]==0).all()),'strong_baseline_status':'pending full LIO interface and predeclared noise sensitivity','not_method_gain_evidence':True,'holdout_performance_opened':role=='heldout','input_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [navpath,refpath,data/(seq+'_F9P_GNSS.pos'),Path(a.init_run)/'initial_condition.json']}}
(out/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig,ax=plt.subplots(2,1,figsize=(10,7),constrained_layout=True)
ax[0].plot(r[:,1],r[:,0],label='MM/INS reference');ax[0].plot(n[:,1],n[:,0],label='KF-GINS ADIS + F9P');ax[0].plot(gpos[:,1],gpos[:,0],'.',markersize=1,label='F9P antenna');ax[0].set(xlabel='East (m)',ylabel='North (m)',aspect='equal');ax[0].legend()
ax[1].plot(grid-grid[0],np.linalg.norm(err[:,:2],axis=1));ax[1].set(xlabel='Time from evaluation start (s)',ylabel='KF-GINS horizontal error (m)')
fig.savefig(out/'building00_KF_initial.png',dpi=160);print(json.dumps(metrics,indent=2))
if m['coverage']<.99:raise ValueError('baseline coverage failed; retain unavailable epochs')
