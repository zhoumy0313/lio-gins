"""Common 3-D linear position KF. Existing NIS/Huber policies are baselines."""
import numpy as np
from src.adapters.geodesy import check_rotation


def covariance(m, strict=False):
    a = np.asarray(m,float)
    if a.shape != (3,3) or not np.isfinite(a).all() or not np.allclose(a,a.T,atol=1e-12,rtol=1e-10):
        raise ValueError('finite symmetric 3x3 covariance required')
    eig = np.linalg.eigvalsh(a)
    invalid = (eig<=0).any() if strict else (eig < -1e-12).any()
    if invalid:
        raise ValueError('positive covariance required')
    return a.copy()


class PositionKF:
    def __init__(self, p0, p_cov, r_n_l):
        self.p = np.asarray(p0,float).copy()
        if self.p.shape != (3,) or not np.isfinite(self.p).all():
            raise ValueError('finite initial position required')
        self.P = covariance(p_cov)
        self.A = check_rotation(r_n_l).copy()
        self.seen_gnss_ids = set()

    def propagate(self, delta_lio_m, q):
        d = np.asarray(delta_lio_m,float)
        if d.shape != (3,) or not np.isfinite(d).all():
            raise ValueError('finite LIO increment required; resets handled by caller')
        q = covariance(q)
        self.p = self.p + self.A @ d
        self.P = covariance(self.P+q)

    def update(self, gnss_id, z_antenna_n, r, r_n_b, lever_frd, policy='disabled', nis_limit=11.3448667301, huber_limit=2.5, external_r_multiplier=1.0):
        if policy not in {'disabled','nis','huber'}:
            raise ValueError('unknown baseline policy')
        if not np.isfinite([nis_limit,huber_limit]).all() or nis_limit<=0 or huber_limit<=0:
            raise ValueError('positive finite baseline thresholds required')
        if not np.isfinite(external_r_multiplier) or external_r_multiplier<1:
            raise ValueError('external covariance multiplier must be finite and >=1')
        lever = np.asarray(lever_frd,float)
        if lever.shape != (3,) or not np.isfinite(lever).all():
            raise ValueError('finite FRD lever arm required')
        if gnss_id in self.seen_gnss_ids:
            raise ValueError('GNSS observation reused')
        self.seen_gnss_ids.add(gnss_id)
        z = np.asarray(z_antenna_n,float)
        if z.shape != (3,) or not np.isfinite(z).all():
            return {'accepted':False,'reason':'invalid_position'}
        try:
            r = covariance(r,strict=True)
        except ValueError:
            return {'accepted':False,'reason':'invalid_R'}
        residual = z - (self.p + check_rotation(r_n_b) @ lever)
        s = self.P+r
        nis = float(residual @ np.linalg.solve(s,residual))
        if policy == 'nis' and nis>nis_limit:
            return {'accepted':False,'reason':'nis_gate','nis':nis,'r_multiplier':1.0,'correction_norm_m':0.0}
        gamma = max(1.0,np.sqrt(nis)/huber_limit) if policy=='huber' else 1.0
        # Recovery protection multiplies the same nominal Huber covariance;
        # it must not make the baseline's outlier score smaller first.
        gamma *= external_r_multiplier
        r_eff = r*gamma
        k = np.linalg.solve((self.P+r_eff).T,self.P.T).T
        correction = k @ residual
        self.p += correction
        j = np.eye(3)-k
        post = j@self.P@j.T + k@r_eff@k.T
        self.P = covariance((post+post.T)/2)
        return {'accepted':True,'reason':policy,'nis':nis,'r_multiplier':gamma,'correction_norm_m':float(np.linalg.norm(correction))}
