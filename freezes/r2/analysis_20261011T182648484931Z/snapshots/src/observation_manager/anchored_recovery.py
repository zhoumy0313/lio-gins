"""r03: raw-observation anchor checks only during gap-triggered reacquisition.

Qualification is a rule, not proof of absolute correctness. Large local drift
can be indistinguishable from GNSS bias. An anchor never becomes a measurement.
"""
import numpy as np
from src.observation_manager.availability_recovery import AvailabilityRecovery

class AnchoredRecovery(AvailabilityRecovery):
    def __init__(self,anchor_score_limit,anchor_good_duration_s,anchor_Q_growth_multiplier,
                 use_anchor=True,**kwargs):
        super().__init__(**kwargs)
        if not np.isfinite([anchor_score_limit,anchor_good_duration_s,anchor_Q_growth_multiplier]).all() or min(anchor_score_limit,anchor_good_duration_s)<=0 or anchor_Q_growth_multiplier<1:
            raise ValueError('finite positive anchor qualification and growth required')
        self.anchor_limit=anchor_score_limit;self.anchor_duration=anchor_good_duration_s
        self.anchor_growth=anchor_Q_growth_multiplier;self.use_anchor=use_anchor
        self.anchor=None;self.anchor_active=False;self.trust_since=None

    def decide(self,t,z,lio_antenna,R,nominal_nis,healthy=True,travel_m=0.,observation_id=None):
        gap=self.last_t is not None and t-self.last_t>self.gap
        if gap:
            self.anchor_active=self.use_anchor and self.anchor is not None
            self.trust_since=None
        result=super().decide(t,z,lio_antenna,R,nominal_nis,healthy=healthy,travel_m=travel_m)
        anchor_score=None;anchor_age=None;anchor_id=None
        if self.anchor is not None:
            anchor_age=t-self.anchor['sow'];anchor_id=self.anchor['observation_id']
        if self.anchor_active and healthy:
            a=self.anchor;dt=t-a['sow'];distance=max(0.,travel_m-a['travel_m'])
            d=np.asarray(z)-(a['z']+np.asarray(lio_antenna)-a['local'])
            cov=np.asarray(R)[:2,:2]+a['R'][:2,:2]+np.eye(2)*self.anchor_growth*(self.qt*dt+self.qd*distance)
            anchor_score=float(d[:2]@np.linalg.solve(cov,d[:2]))
            if self.check_motion and anchor_score>self.anchor_limit:
                self.overriding=True;self.isolate(t)
                result={**result,'admit':False,'state':self.state,'r_multiplier':1.,
                    'qualification_elapsed_s':0.,'reason':'retained_anchor_inconsistent'}
            elif result['admit'] and result['state']=='NORMAL' and not self.overriding:
                self.anchor_active=False
        short_good=result['motion_score'] is not None and result['motion_score']<=self.limit
        promotable=self.use_anchor and not self.anchor_active and not self.overriding and result['admit'] and result['state']=='NORMAL' and healthy and short_good and nominal_nis<=self.onset
        if not promotable:self.trust_since=None
        else:
            if self.trust_since is None:self.trust_since=t
            if t-self.trust_since>=self.anchor_duration:
                self.anchor={'sow':float(t),'z':np.asarray(z,float).copy(),
                    'local':np.asarray(lio_antenna,float).copy(),'R':np.asarray(R,float).copy(),
                    'travel_m':float(travel_m),'observation_id':observation_id}
        return {**result,'anchor_score':anchor_score,'anchor_available':self.anchor is not None,
            'anchor_active':self.anchor_active,'anchor_measurement_sow_used':t-anchor_age if anchor_age is not None else None,
            'anchor_age_s':anchor_age,'anchor_original_gnss_id_used':anchor_id,
            'anchor_promoted_sow':self.anchor['sow'] if self.anchor is not None else None}
