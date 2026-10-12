"""Explicit incompatible .nav schemas: never infer reference coordinates by suffix."""
import numpy as np


def load_i2nav_local_ned(path):
    a = np.loadtxt(path,ndmin=2)
    if a.shape[1] != 10 or not np.isfinite(a).all():
        raise ValueError('i2Nav local NED reference requires 10 finite columns')
    return a


def load_kf_gins_llh(path):
    a = np.loadtxt(path,ndmin=2)
    if a.shape[1] != 11 or not np.isfinite(a).all():
        raise ValueError('KF-GINS LLH requires 11 finite columns')
    return a


def interpolate_with_gaps(times, values, grid, max_gap_s):
    t,v,g = np.asarray(times),np.asarray(values),np.asarray(grid)
    if len(t)<2 or not np.isfinite(t).all() or np.any(np.diff(t)<=0) or max_gap_s<=0:
        raise ValueError('strictly increasing reference time required')
    idx = np.searchsorted(t,g,side='right')-1
    left = np.clip(idx,0,len(t)-2)
    span = t[left+1]-t[left]
    valid = (g>=t[0])&(g<=t[-1])&(span<=max_gap_s)
    # An exact observed reference is valid even beside a gap.
    exact_idx = np.clip(np.searchsorted(t,g),0,len(t)-1)
    exact = t[exact_idx]==g
    result = v[left] + ((g-t[left])/span)[:,None]*(v[left+1]-v[left])
    result[exact] = v[exact_idx[exact]]
    valid |= exact
    result[~valid] = np.nan
    return result,valid


def horizontal_metrics(errors_ned, expected_count):
    e = np.asarray(errors_ned,float)
    valid = np.isfinite(e).all(axis=1)
    h = np.linalg.norm(e[valid,:2],axis=1)
    return {'samples_expected':int(expected_count),'samples_valid':int(valid.sum()),
            'coverage':float(valid.sum()/expected_count) if expected_count else 0.0,
            'horizontal_rmse_m':float(np.sqrt(np.mean(h*h))) if len(h) else None,
            'horizontal_p95_m':float(np.percentile(h,95)) if len(h) else None,
            'horizontal_max_m':float(h.max()) if len(h) else None}
