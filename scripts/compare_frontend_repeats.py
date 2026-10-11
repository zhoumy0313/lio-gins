#!/usr/bin/env python3
"""Compare real same-input frontend outputs and complete native timing evidence."""
import argparse,hashlib,json,os
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
p=argparse.ArgumentParser();p.add_argument('first');p.add_argument('repeat');a=p.parse_args()
folders=[Path(a.first).resolve(),Path(a.repeat).resolve()];out=Path(os.environ['LIO_GINS_RUN_DIR'])
ids=[json.loads((f/'frontend_input_identity.json').read_text()) for f in folders]
if ids[0]['sha256']!=ids[1]['sha256'] or ids[0]['image']['binary_sha256']!=ids[1]['image']['binary_sha256']:
    raise ValueError('repeat input or estimator binary differs')
trajectories=[np.loadtxt(f/'trajectory.csv',ndmin=2) for f in folders]
x,y=trajectories
if x.shape!=y.shape or not np.allclose(x[:,0],y[:,0],rtol=0,atol=1e-6):
    raise ValueError('frame identity differs; cannot compare as paired samples')
d=y[:,1:4]-x[:,1:4];angle=(Rotation.from_quat(x[:,4:8]).inv()*Rotation.from_quat(y[:,4:8])).magnitude()
timing=folders[1]/'fast_lio_time_log.csv';t=np.loadtxt(timing,delimiter=',',skiprows=1,ndmin=2)
if t.shape!=(len(y),11) or np.max(abs(t[:,0]-y[:,0]))>1e-6:raise ValueError('timing/output frame correspondence failed')
result={'kind':'same_input_real_frontend_repeat','source_runs':[str(f) for f in folders],
    'paired_frames':len(x),'position_3D_difference_RMS_m':float(np.sqrt(np.mean(np.sum(d*d,axis=1)))),
    'position_3D_difference_max_m':float(np.max(np.linalg.norm(d,axis=1))),
    'rotation_difference_max_rad':float(angle.max()),'timing_rows':len(t),
    'timing_scope':'native IMU processing through incremental mapping, excludes input preprocessing and callbacks; 1x ROS bag replay, not field end-to-end latency',
    'processing_ms':dict(zip(['mean','p50','p95','max'],map(float,[np.mean(t[:,1])*1000,*np.percentile(t[:,1]*1000,[50,95]),np.max(t[:,1])*1000]))),
    'scientific_limit':'one pair is numerical sensitivity evidence, not independent statistical replication',
    'input_sha256':{str(f/name):hashlib.sha256((f/name).read_bytes()).hexdigest() for f in folders for name in ['trajectory.csv','frontend_input_identity.json']}}
np.savetxt(out/'paired_differences.csv',np.column_stack([x[:,0],d,angle]),delimiter=',',header='unix,delta_x_m,delta_y_m,delta_z_m,delta_rotation_rad',comments='')
(out/'repeat_consistency.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
