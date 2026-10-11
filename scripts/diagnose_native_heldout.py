#!/usr/bin/env python3
"""Offline native B1 failure description; no calibration, tuning or estimator changes."""
import argparse,json,os,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.adapters.geodesy import llh_to_ned
from src.adapters.research_access import sha
p=argparse.ArgumentParser();p.add_argument('heldout_matrix');a=p.parse_args();matrixpath=Path(a.heldout_matrix).resolve();m=json.loads(matrixpath.read_text());out=Path(os.environ['LIO_GINS_RUN_DIR']);root=Path(__file__).resolve().parents[1]
navpath=Path(m['native_B1'])/'KF_GINS_Navresult.nav';evalpath=Path(m['native_evaluation'])/'metrics.json';icpath=Path(m['initialization'])/'initial_condition.json';refpath=root/'data/i2nav-dataset/parking00/parking00_groundtruth.nav';gnsspath=root/'data/i2nav-dataset/parking00/parking00_F9P_GNSS.pos'
ic=json.loads(icpath.read_text());nav=np.loadtxt(navpath);ref=np.loadtxt(refpath);gnss=np.loadtxt(gnsspath);metric=json.loads(evalpath.read_text());epochpath=Path(m['native_evaluation'])/'per_epoch.csv';e=np.loadtxt(epochpath,delimiter=',',skiprows=1)
def speedstats(v):
    v=np.linalg.norm(v,axis=1);return {k:float(x) for k,x in zip(['median_mps','P95_mps','maximum_mps'],[np.median(v),np.percentile(v,95),v.max()])}
pos=llh_to_ned(nav[:,2:5],ic['origin_ADIS_llh_deg_m']);derived=np.diff(pos,axis=0)/np.diff(nav[:,1])[:,None]
horizontal_error=np.linalg.norm(e[:,7:9],axis=1);j=np.searchsorted(gnss[:,0],e[:,0],side='right')-1;j=np.clip(j,0,len(gnss)-1);std=np.linalg.norm(gnss[j,4:6],axis=1)
bins=[]
for lo,hi in [(0,2),(2,10),(10,float('inf'))]:
    mask=(std>=lo)&(std<hi)&np.isfinite(horizontal_error);bins.append({'receiver_horizontal_std_interval_m':[lo,hi if np.isfinite(hi) else None],'epochs':int(mask.sum()),'fraction':float(mask.mean()),'B1_horizontal_RMSE_m':float(np.sqrt(np.mean(horizontal_error[mask]**2))) if mask.any() else None})
worst=int(np.nanargmax(horizontal_error));first=np.flatnonzero(horizontal_error>10)
result={'source_matrix':str(matrixpath),'native_B1_metric':metric['metrics_10Hz'],'native_velocity':speedstats(nav[:,5:8]),'native_position_difference_velocity':speedstats(derived),'reference_velocity':speedstats(ref[:,4:7]),'first_error_over_10m_sow':float(e[first[0],0]) if len(first) else None,'worst_error_sow':float(e[worst,0]),'receiver_horizontal_std_at_worst_error_m':float(std[worst]),'receiver_STD_bins':bins,'all_native_rows_finite':bool(np.isfinite(nav).all()),'native_clock_ordered':bool(np.all(np.diff(nav[:,1])>0)),
    'interpretation':'large error is a real frozen native-config failure; STD association is descriptive, not a causal explanation. Noise priors transferred and selected on building00, no parking calibration. Do not use this weak result as the main percentage-gain comparator or claim it represents the best achievable KF-GINS.',
    'retuned':False,'input_SHA256':{str(p):sha(p) for p in [matrixpath,navpath,evalpath,icpath,refpath,gnsspath,epochpath]}}
(out/'native_failure_diagnostic.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
