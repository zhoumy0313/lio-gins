#!/usr/bin/env python3
"""Validate and cache a sealed development FAST-LIO run, without any reference."""
import argparse,hashlib,json,os,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.adapters.sensor_text import unix_to_gps
p=argparse.ArgumentParser();p.add_argument('frontend_run');a=p.parse_args();root=Path(__file__).resolve().parents[1];out=Path(os.environ['LIO_GINS_RUN_DIR']);source=Path(a.frontend_run).resolve();manifest=json.loads((source/'manifest.json').read_text())
if manifest['status']!='PASSED' or manifest['kind']!='real_frontend':raise ValueError('frontend did not complete successfully')
identity=json.loads((source/'frontend_input_identity.json').read_text())
if Path(identity['bag']).name!='building00.bag':raise ValueError('heldout cache is closed')
nav=np.loadtxt(source/'trajectory.csv',ndmin=2);events=np.loadtxt(source/'interface_events.csv',delimiter=',',skiprows=1,ndmin=2)
if nav.shape[1]!=8 or events.shape!=(len(nav),9) or not np.isfinite(nav).all() or not np.isfinite(events).all():raise ValueError('invalid trajectory/interface schema or row match')
if np.any(np.diff(nav[:,0])<=0) or np.max(abs(nav[:,0]-events[:,1]))>1e-6:raise ValueError('output timestamp mismatch or reversal')
norm=np.linalg.norm(nav[:,4:8],axis=1);quantization_error=float(np.max(abs(norm-1)))
if quantization_error>2e-6:raise ValueError('quaternion outside declared six-decimal serialization tolerance')
# Explicit serialization repair; not a hidden frame/alignment correction.
quat=nav[:,4:8]/norm[:,None]
week,sow=unix_to_gps(nav[0,0]);time=nav[:,0]-nav[0,0]+sow
if week!=2364:raise ValueError('development GPS week differs from audited bag')
# ROS clock is ticked at 100 Hz in replay. Add one tick to its sampled value to
# report a conservative clock-resolution bound, and never precede scan end.
available_unix=np.maximum.accumulate(np.maximum(events[:,2]+.01,nav[:,0]))
available=available_unix-nav[0,0]+sow
span=np.diff(time);metadata={'role':'development','source_frontend_run':str(source),'input_identity':identity,'gps_week':week,'time_sow_range':[float(time[0]),float(time[-1])],'output_rows':len(nav),'expected_raw_AT128_frames':12443,'raw_frame_output_ratio':float(len(nav)/12443),'max_scan_pose_gap_s':float(span.max()),'gaps_over_150ms':int((span>.15).sum()),'maximum_quaternion_norm_serialization_error':quantization_error,'quaternion_policy':'explicit normalization only for six-decimal serialization error <=2e-6','availability_policy':'max(scan_end, sampled_ROS_clock+one_10ms_clock_tick), cumulative maximum; replay clock resolution bound, not measured field latency','clock_precedes_scan_end_max_s':float(np.max(nav[:,0]-events[:,2])),'frontend_processing_time_source':'fast_lio_time_log.csv; full replay wall measured separately','health_diagnostic':'effective point count and mean absolute plane residual, not increment covariance','source_sha256':{name:hashlib.sha256((source/name).read_bytes()).hexdigest() for name in ['trajectory.csv','interface_events.csv','fast_lio_time_log.csv','frontend_input_identity.json']},'reference_access':False,'holdout_performance_opened':False}
np.savez(out/'lio_cache.npz',sow=time,position=nav[:,1:4],quaternion_xyzw=quat,available_sow=available,effective_points=events[:,4],mean_abs_plane_residual_m=events[:,5],velocity=events[:,6:9])
metadata['cache_sha256']=hashlib.sha256((out/'lio_cache.npz').read_bytes()).hexdigest();(out/'cache_identity.json').write_text(json.dumps(metadata,indent=2)+'\n');print(json.dumps(metadata,indent=2))
if metadata['raw_frame_output_ratio']<.99:raise ValueError('insufficient frontend output; inspect dropped/initialization frames')
