"""r01 causal motion verification on raw GNSS; monitoring never adds a measurement.

The score is an engineering normalization, not calibrated independent evidence.
No estimator posterior, reference state, or artificial fault label is accessed.
"""
from collections import deque
import numpy as np

class MotionRecovery:
    def __init__(self, window_s, score_limit, good_duration_s, wait_s=2., recovery_s=15.,
                 protection=15., onset_nis=16.266236, gap_s=2., monitor_gap_s=1.5,
                 q_time_m2ps=.001, q_distance_m2pm=.001, max_wait_s=60.,
                 check_motion=True, decay=True):
        numbers=[window_s,score_limit,good_duration_s,wait_s,recovery_s,protection,onset_nis,
                 gap_s,monitor_gap_s,q_time_m2ps,q_distance_m2pm,max_wait_s]
        if not np.isfinite(numbers).all() or min(window_s,score_limit,recovery_s,onset_nis,gap_s,monitor_gap_s,max_wait_s)<=0 or min(good_duration_s,wait_s,q_time_m2ps,q_distance_m2pm)<0 or protection<1:
            raise ValueError('finite valid motion recovery parameters required')
        self.window=window_s;self.limit=score_limit;self.good_duration=good_duration_s
        self.wait=wait_s;self.duration=recovery_s;self.protection=protection
        self.onset=onset_nis;self.gap=gap_s;self.monitor_gap=monitor_gap_s
        self.qt=q_time_m2ps;self.qd=q_distance_m2pm;self.max_wait=max_wait_s
        self.check_motion=check_motion;self.decay=decay
        self.history=deque();self.last_t=None;self.state='NORMAL'
        self.blocked_since=None;self.earliest=None;self.good_since=None;self.release=None

    def isolate(self,t):
        if self.state in ['NORMAL','RECOVERING'] or self.blocked_since is None:
            self.blocked_since=t;self.earliest=t+self.wait
        self.good_since=None;self.release=None
        self.state='UNRESOLVED' if t-self.blocked_since>=self.max_wait else 'ISOLATED'

    def output_state(self,t):
        return 'OUTAGE' if self.last_t is not None and t-self.last_t>self.gap else self.state

    def decide(self,t,z,lio_antenna,R,nominal_nis,healthy=True,travel_m=0.):
        z=np.asarray(z,float);local=np.asarray(lio_antenna,float);r=np.asarray(R,float)
        if z.shape!=(3,) or local.shape!=(3,) or r.shape!=(3,3) or not np.isfinite(np.r_[t,z,local,r.ravel(),nominal_nis,travel_m]).all() or nominal_nis<0 or travel_m<0 or (self.last_t is not None and t<=self.last_t):
            raise ValueError('ordered finite observation and independent local evidence required')
        if not np.allclose(r,r.T) or np.linalg.eigvalsh(r).min()<=0:raise ValueError('positive symmetric receiver covariance required')
        gap=self.last_t is not None and t-self.last_t>self.gap
        if self.last_t is not None and t-self.last_t>self.monitor_gap:self.history.clear()
        self.last_t=t
        if not healthy:
            self.history.clear();self.isolate(t);self.state='UNRESOLVED'
            return {'admit':True,'state':'UNRESOLVED','r_multiplier':1.,'motion_score':None,
                    'qualification_elapsed_s':0.,'reason':'local_health_unverified_Huber_fallback'}
        while self.history and self.history[0][0]<t-self.window-.5:self.history.popleft()
        previous=[v for v in self.history if 0<=t-self.window-v[0]<=.5]
        score=None
        if previous:
            old=previous[-1];dt=t-old[0];distance=max(0.,travel_m-old[4])
            d=(z-old[1])-(local-old[2]);cov=r[:2,:2]+old[3][:2,:2]+np.eye(2)*(self.qt*dt+self.qd*distance)
            score=float(d[:2]@np.linalg.solve(cov,d[:2]))
        self.history.append((float(t),z.copy(),local.copy(),r.copy(),float(travel_m)))
        good=score is not None and (not self.check_motion or score<=self.limit)
        onset=self.state=='NORMAL' and nominal_nis>self.onset
        bad=score is not None and self.check_motion and score>self.limit
        if gap:self.blocked_since=None  # Every actual outage starts a new wait.
        if gap or onset or bad:self.isolate(t)
        if self.state=='NORMAL':
            return {'admit':True,'state':'NORMAL','r_multiplier':1.,'motion_score':score,
                    'qualification_elapsed_s':0.,'reason':'ordinary_Huber'}
        if self.state=='RECOVERING':
            if not good:self.isolate(t)
            else:
                elapsed=t-self.release
                if elapsed>=self.duration:self.state='NORMAL'
                else:
                    return {'admit':True,'state':'RECOVERING',
                        'r_multiplier':1+(self.protection-1)*(1-elapsed/self.duration)**2 if self.decay else 1.,
                        'motion_score':score,'qualification_elapsed_s':t-self.good_since,'reason':'motion_verified_squared_R'}
        if self.state=='NORMAL':
            return {'admit':True,'state':'NORMAL','r_multiplier':1.,'motion_score':score,
                    'qualification_elapsed_s':t-self.good_since,'reason':'recovery_finished'}
        if not good:self.good_since=None
        elif self.good_since is None:self.good_since=t
        qualified=0. if self.good_since is None else t-self.good_since
        if good and qualified>=self.good_duration and t>=self.earliest:
            self.state='RECOVERING';self.release=t;self.blocked_since=None
            return {'admit':True,'state':'RECOVERING','r_multiplier':self.protection if self.decay else 1.,
                    'motion_score':score,'qualification_elapsed_s':qualified,'reason':'motion_qualified_reintegration'}
        if self.blocked_since is not None and t-self.blocked_since>=self.max_wait:self.state='UNRESOLVED'
        return {'admit':False,'state':self.state,'r_multiplier':1.,'motion_score':score,
                'qualification_elapsed_s':qualified,'reason':'motion_qualification_wait'}
