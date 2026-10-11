"""Bounded two-endpoint LIO interpolation with explicit endpoint availability."""
import numpy as np
from scipy.spatial.transform import Rotation,Slerp


class BufferedLIO:
    def __init__(self,times,positions,quaternions,availability,max_span_s=.15):
        self.times=np.asarray(times,float);self.positions=np.asarray(positions,float);self.q=np.asarray(quaternions,float);self.available=np.asarray(availability,float)
        n=len(self.times)
        if n<2 or self.positions.shape!=(n,3) or self.q.shape!=(n,4) or self.available.shape!=(n,):raise ValueError('LIO array schema mismatch')
        if not all(np.isfinite(x).all() for x in [self.times,self.positions,self.q,self.available]):raise ValueError('nonfinite LIO input')
        if np.any(np.diff(self.times)<=0) or np.any(np.diff(self.available)<0) or np.any(self.available<self.times):raise ValueError('LIO time/availability ordering violation')
        if np.max(abs(np.linalg.norm(self.q,axis=1)-1))>1e-6:raise ValueError('explicitly validated unit quaternions required')
        if not np.isfinite(max_span_s) or max_span_s<=0:raise ValueError('positive interpolation span required')
        self.max_span=max_span_s;self.previous_query=-np.inf

    def query(self,t,available_until=None):
        if not np.isfinite(t) or t<self.previous_query:raise ValueError('queries must follow measurement order')
        self.previous_query=t
        j=int(np.searchsorted(self.times,t,side='left'))
        if j==len(self.times) or t<self.times[0]:return {'valid':False,'reason':'outside_LIO_support'}
        if self.times[j]==t:
            i=j;fraction=0.
        else:
            i=j-1;span=self.times[j]-self.times[i]
            if span>self.max_span:return {'valid':False,'reason':'LIO_gap','left':i,'right':j}
            fraction=(t-self.times[i])/span
        available=float(max(self.available[i],self.available[j]))
        # One floating-point ULP avoids rejecting an exactly equal decimal
        # boundary (e.g. .1+.02 versus .12); no physical lookahead is added.
        if available_until is not None and available>np.nextafter(available_until,np.inf):return {'valid':False,'reason':'endpoint_not_available','available_time':available}
        p=self.positions[i]+fraction*(self.positions[j]-self.positions[i])
        r=Rotation.from_quat(self.q[j]).as_matrix() if i==j else Slerp([self.times[i],self.times[j]],Rotation.from_quat(self.q[[i,j]]))([t]).as_matrix()[0]
        return {'valid':True,'position':p,'rotation':r,'measurement_time':float(t),'available_time':available,'delay_s':available-t,'left':i,'right':j}
