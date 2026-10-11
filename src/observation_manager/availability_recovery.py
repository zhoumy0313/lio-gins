"""r02: only available motion/outage evidence overrides mature fixed recovery.

The fixed policy is a decision shadow, never a second filter or measurement.
"""
from src.fusion.fixed_recovery import FixedRecovery
from src.observation_manager.motion_recovery import MotionRecovery

class AvailabilityRecovery(MotionRecovery):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.fixed=FixedRecovery(wait_s=self.wait,recovery_s=self.duration,
            protection=self.protection,onset_nis=self.onset,gap_s=self.gap)
        self.overriding=False;self.evidence_unavailable=False

    def output_state(self,t):
        if self.last_t is not None and t-self.last_t>self.gap:return 'OUTAGE'
        if self.evidence_unavailable:return 'UNRESOLVED'
        return self.state if self.overriding else self.fixed.state

    def decide(self,t,z,lio_antenna,R,nominal_nis,healthy=True,travel_m=0.):
        gap=self.last_t is not None and t-self.last_t>self.gap
        fixed=self.fixed.decide(t,nominal_nis)
        # NIS-driven protection is already handled by the same mature policy.
        # The additional manager needs independent motion or actual gap evidence.
        motion=super().decide(t,z,lio_antenna,R,0.,healthy=healthy,travel_m=travel_m)
        score=motion['motion_score'];bad=score is not None and self.check_motion and score>self.limit
        if not healthy:
            self.overriding=False;self.state='NORMAL';self.blocked_since=None
            self.earliest=None;self.good_since=None;self.release=None
            self.evidence_unavailable=True
            return {**fixed,'r_multiplier':fixed['r_multiplier'] if self.decay else 1.,
                'state':'UNRESOLVED','motion_score':None,'qualification_elapsed_s':0.,
                'reason':'unavailable_local_evidence_mature_recovery_fallback'}
        self.overriding=self.overriding or gap or bad
        self.evidence_unavailable=score is None and not self.overriding
        if self.overriding:
            if motion['state']!='NORMAL':return motion
            self.overriding=False
        return {**fixed,'r_multiplier':fixed['r_multiplier'] if self.decay else 1.,
            'state':'UNRESOLVED' if self.evidence_unavailable else fixed['state'],
            'motion_score':score,'qualification_elapsed_s':motion['qualification_elapsed_s'],
            'reason':'available_motion_no_extra_veto' if score is not None else 'incomplete_monitor_window_mature_fallback'}
