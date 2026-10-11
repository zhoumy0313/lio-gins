#!/usr/bin/env python3
"""Offline official demo health check, separate from i2Nav route experiments."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from src.adapters.geodesy import llh_to_ned
from src.evaluation.reference import load_kf_gins_llh, interpolate_with_gaps, horizontal_metrics

p=argparse.ArgumentParser();p.add_argument('demo_run');a=p.parse_args()
root=Path(__file__).resolve().parents[1];out=Path(os.environ['LIO_GINS_RUN_DIR'])
navpath=Path(a.demo_run)/'KF_GINS_Navresult.nav';refpath=root/'third_party/KF-GINS/dataset/truth.nav'
nav=load_kf_gins_llh(navpath);ref=load_kf_gins_llh(refpath)
assert np.all(np.diff(nav[:,1])>0), 'output time reversal'
assert np.all(np.diff(ref[:,1])>=0), 'reference time reversal'
# The official demo truth contains different rows at rounded equal SOWs.
# Explicit engineering-only policy: first observed row; retain original file,
# duplicate counts and evaluate last-row sensitivity without selecting by error.
duplicates = np.flatnonzero(np.diff(ref[:,1])==0)
_,first = np.unique(ref[:,1],return_index=True)
_,revfirst = np.unique(ref[::-1,1],return_index=True)
last = len(ref)-1-revfirst
firstref = ref[first]
lastref = ref[np.sort(last)]
origin=ref[0,2:5]
start=max(nav[0,1],ref[0,1]);end=min(nav[-1,1],ref[-1,1])
grid=np.arange(np.ceil(start*10)/10,np.floor(end*10)/10+.01,.1)
n,nvalid=interpolate_with_gaps(nav[:,1],llh_to_ned(nav[:,2:5],origin),grid,.02)
r,rvalid=interpolate_with_gaps(firstref[:,1],llh_to_ned(firstref[:,2:5],origin),grid,.02)
rlast,_=interpolate_with_gaps(lastref[:,1],llh_to_ned(lastref[:,2:5],origin),grid,.02)
errors=n-r;metrics=horizontal_metrics(errors,len(grid))
metrics.update({'experiment_kind':'official_upstream_demo_health_only','source_demo_run':str(Path(a.demo_run).resolve()),
                'nav_rows':len(nav),'nav_sow_range':[float(nav[0,1]),float(nav[-1,1])],
                'time_monotonic':True,'output_all_finite':True,'reference_schema':'KF-GINS_llh_11_columns',
                'upstream_week_field_is_placeholder_zero':bool((nav[:,0]==0).all()),
                'reference_gps_week':int(ref[0,0]),'origin_llh_deg_m':origin.tolist(),
                'reference_duplicate_time_pairs':len(duplicates),'duplicate_policy':'first row per SOW, official demo only, raw preserved',
                'last_row_policy_sensitivity':horizontal_metrics(n-rlast,len(grid)),
                'max_first_last_reference_horizontal_difference_m':float(np.nanmax(np.linalg.norm((r-rlast)[:,:2],axis=1))),
                'alignment':'shared WGS84 ECEF-to-NED frame, no trajectory fit',
                'evaluation_hz':10,'max_interpolation_gap_s':.02,'vertical_rmse_m':float(np.sqrt(np.nanmean(errors[:,2]**2))),
                'input_sha256':{str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in [navpath,refpath]},
                'not_i2nav_robot_evidence':True,'not_method_gain_evidence':True})
np.savetxt(out/'per_epoch.csv',np.column_stack([grid,errors]),delimiter=',',header='sow_s,error_N_m,error_E_m,error_D_m',comments='')
(out/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig,ax=plt.subplots(2,1,figsize=(9,6),constrained_layout=True)
ax[0].plot(n[:,1],n[:,0],label='KF-GINS official demo');ax[0].plot(r[:,1],r[:,0],label='demo reference',alpha=.7)
ax[0].set(xlabel='East (m)',ylabel='North (m)',aspect='equal');ax[0].legend()
ax[1].plot(grid-grid[0],np.linalg.norm(errors[:,:2],axis=1));ax[1].set(xlabel='Time from evaluation start (s)',ylabel='Horizontal error (m)')
fig.savefig(out/'demo_health.png',dpi=160)
print(json.dumps(metrics,indent=2))
assert metrics['coverage']>.99 and metrics['horizontal_rmse_m']<5, 'demo health failed; inspect original inputs and initialization'
