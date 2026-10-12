"""WGS84 and frame utilities. R_A_B maps B vectors to A."""
import numpy as np

A_WGS84 = 6378137.0
F_WGS84 = 1.0 / 298.257223563
E2 = F_WGS84 * (2 - F_WGS84)


def llh_to_ecef(llh_deg_m):
    p = np.asarray(llh_deg_m, dtype=float)
    if p.shape[-1] != 3 or not np.isfinite(p).all():
        raise ValueError('finite [lat_deg, lon_deg, h_m] required')
    if np.any(np.abs(p[..., 0]) > 90) or np.any(np.abs(p[..., 1]) > 180):
        raise ValueError('latitude/longitude outside range')
    lat, lon = np.deg2rad(p[..., 0]), np.deg2rad(p[..., 1])
    n = A_WGS84 / np.sqrt(1 - E2 * np.sin(lat)**2)
    return np.stack([(n+p[..., 2])*np.cos(lat)*np.cos(lon),
                     (n+p[..., 2])*np.cos(lat)*np.sin(lon),
                     (n*(1-E2)+p[..., 2])*np.sin(lat)], axis=-1)


def ecef_to_ned_rotation(origin_deg_m):
    lat, lon = np.deg2rad(np.asarray(origin_deg_m, float)[:2])
    s, c, sl, cl = np.sin(lat), np.cos(lat), np.sin(lon), np.cos(lon)
    return np.array([[-s*cl,-s*sl,c],[-sl,cl,0],[-c*cl,-c*sl,-s]])


def llh_to_ned(llh_deg_m, origin_deg_m):
    return (llh_to_ecef(llh_deg_m)-llh_to_ecef(origin_deg_m)) @ ecef_to_ned_rotation(origin_deg_m).T


def check_rotation(r, atol=1e-6):
    r = np.asarray(r, float)
    if r.shape != (3,3) or not np.isfinite(r).all() or not np.allclose(r.T@r,np.eye(3),atol=atol,rtol=0) or abs(np.linalg.det(r)-1)>atol:
        raise ValueError('proper orthogonal rotation required')
    return r


def quat_xyzw_rotation(q):
    q = np.asarray(q, float)
    if q.shape != (4,) or not np.isfinite(q).all() or abs(np.linalg.norm(q)-1)>1e-6:
        raise ValueError('unit xyzw quaternion required; no silent normalization')
    x,y,z,w = q
    return check_rotation(np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],
                                   [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],
                                   [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]]))


def antenna_position(p_adis_n, r_n_b, lever_frd):
    return np.asarray(p_adis_n, float) + check_rotation(r_n_b) @ np.asarray(lever_frd, float)
