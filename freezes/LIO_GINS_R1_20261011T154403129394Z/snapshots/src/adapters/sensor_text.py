"""Explicit i2Nav sensor schemas; retains bad rows for metadata audit."""
from pathlib import Path
import hashlib
import numpy as np

SCHEMAS = {'adis_increment': ['sow_s','dtheta_x_rad','dtheta_y_rad','dtheta_z_rad','dvel_x_mps','dvel_y_mps','dvel_z_mps'],
           'f9p_spp': ['sow_s','latitude_deg','longitude_deg','altitude_m','std_n_m','std_e_m','std_d_m']}


def load_sensor(path, schema):
    if schema not in SCHEMAS:
        raise ValueError('explicit sensor schema required')
    a = np.loadtxt(path, ndmin=2)
    if a.shape[1] != len(SCHEMAS[schema]):
        raise ValueError(f'{schema}: expected {len(SCHEMAS[schema])} columns, got {a.shape[1]}')
    if len(a) == 0:
        raise ValueError('empty sensor input')
    return a


def audit_table(a, schema):
    a = np.asarray(a, float)
    d = np.diff(a[:,0])
    finite = np.isfinite(a).all(axis=1)
    info = {'schema':schema,'columns':SCHEMAS[schema], 'rows':len(a),
            'finite_rows':int(finite.sum()),'duplicate_times':int((d==0).sum()),
            'backward_times':int((d<0).sum()), 'time_min':float(np.nanmin(a[:,0])), 'time_max':float(np.nanmax(a[:,0]))}
    pos = d[np.isfinite(d)&(d>0)]
    info['median_dt_s'] = float(np.median(pos)) if len(pos) else None
    info['max_gap_s'] = float(pos.max()) if len(pos) else None
    if schema == 'f9p_spp':
        valid = finite & (abs(a[:,1])<=90) & (abs(a[:,2])<=180) & (a[:,4:7]>0).all(axis=1)
        info['valid_receiver_rows'] = int(valid.sum())
        info['invalid_std_rows'] = int((~np.isfinite(a[:,4:7]).all(axis=1)|(a[:,4:7]<=0).any(axis=1)).sum())
    return info


def receiver_covariance(std_ned, std_floor_m):
    std = np.asarray(std_ned,float)
    floor = np.asarray(std_floor_m,float)
    if std.shape != (3,) or floor.shape != (3,) or not np.isfinite(std).all() or not np.isfinite(floor).all() or np.any(std<=0) or np.any(floor<=0):
        raise ValueError('invalid standard deviations: reject, do not silently clean')
    return np.diag(np.maximum(std,floor)**2)


def gps_to_unix(week, sow, gps_minus_utc_s=18):
    if not isinstance(week, (int,np.integer)) or week<0 or not np.isfinite(sow) or not 0<=sow<604800:
        raise ValueError('explicit GPS week and in-week SOW required')
    return week*604800 + float(sow) + 315964800 - gps_minus_utc_s


def unix_to_gps(timestamp, gps_minus_utc_s=18):
    if not np.isfinite(timestamp):
        raise ValueError('finite UNIX timestamp required')
    sec = timestamp + gps_minus_utc_s - 315964800
    week = int(np.floor(sec/604800))
    return week, sec-week*604800
