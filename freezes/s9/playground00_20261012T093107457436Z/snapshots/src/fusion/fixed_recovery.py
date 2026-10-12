"""B6: declared fixed wait and finite squared-R recovery on the shared KF.

A local control inspired by phased recovery covariance protection; not a full
Dual-ACKF reproduction. No local-motion evidence or truth is consumed here.
"""
import numpy as np


class FixedRecovery:
    def __init__(self,wait_s=2.,recovery_s=5.,protection=25.,onset_nis=16.266236,gap_s=2.):
        if not np.isfinite([wait_s,recovery_s,protection,onset_nis,gap_s]).all() or wait_s<0 or recovery_s<=0 or protection<1 or onset_nis<=0 or gap_s<=0:raise ValueError('invalid fixed recovery parameters')
        self.wait=wait_s;self.duration=recovery_s;self.protection=protection;self.onset=onset_nis;self.gap=gap_s
        self.state='NORMAL';self.last_t=None;self.release=None

    def decide(self,t,nominal_nis):
        if not np.isfinite([t,nominal_nis]).all() or nominal_nis<0 or (self.last_t is not None and t<=self.last_t):raise ValueError('finite ordered observations and NIS required')
        lost=self.last_t is not None and t-self.last_t>self.gap
        onset=self.state=='NORMAL' and nominal_nis>self.onset
        self.last_t=t
        if lost or onset:
            self.state='WAIT';self.release=t+self.wait
        if self.state=='WAIT':
            if t<self.release:return {'admit':False,'state':'WAIT','r_multiplier':1.,'reason':'fixed_wait'}
            self.state='RECOVERY'
        if self.state=='RECOVERY':
            elapsed=t-self.release
            if elapsed>=self.duration:self.state='NORMAL'
            else:return {'admit':True,'state':'RECOVERY','r_multiplier':1+(self.protection-1)*(1-elapsed/self.duration)**2,'reason':'fixed_squared_R_protection'}
        return {'admit':True,'state':'NORMAL','r_multiplier':1.,'reason':'huber_baseline'}
