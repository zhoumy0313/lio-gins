"""Offline GNSS antenna-error diagnostic; never labels observations online."""
import json,os,hashlib
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation,Slerp
from reanalyse import ROOT,ROUTES
OUT=Path(os.environ['LIO_GINS_RUN_DIR'])
from gate import verify_access,record_opening
context=json.loads((ROOT/'artifacts/s9/building02/technical_context.json').read_text());access=verify_access('building02','s9_prospective_heldout',ROOT/context['freeze_relative_path'],ROOT/'configs/s9/P.json');record_opening(access,'offline_receiver_injection_cancellation')
results=[]
for label in ['building02']:
    _,init,stress=ROUTES[label];stress=ROOT/'outputs'/stress;icpath=ROOT/'outputs'/init/'initial_condition.json';ic=json.loads(icpath.read_text());seq=ic['sequence'];referencepath=ROOT/'data/i2nav-dataset'/seq/(seq+'_groundtruth.nav');ref=np.loadtxt(referencepath);ref=ref[np.r_[True,np.diff(ref[:,0])>0]]
    natural=np.loadtxt(stress/'natural.csv',delimiter=',',skiprows=1);biased=np.loadtxt(stress/'loss30_bias10.csv',delimiter=',',skiprows=1);nmap={int(g[0]):g for g in natural};events=next(c for c in json.loads((stress/'event_manifest.json').read_text())['cases'] if c['id']=='loss30_bias10')['events']
    for i,event in enumerate(events):
        start=event['recovery_start_sow'];g=biased[(biased[:,1]>=start)&(biased[:,1]<start+90)];t=g[:,1];positions=np.column_stack([np.interp(t,ref[:,0],ref[:,j]) for j in [1,2,3]]);rotation=Slerp(ref[:,0],Rotation.from_euler('ZYX',ref[:,7:10][:,::-1],degrees=True))(t);antenna=positions+rotation.apply(np.tile(ic['antenna_lever_FRD_m'],(len(t),1)));n=np.vstack([nmap[int(r[0])] for r in g]);raw_error=np.linalg.norm(n[:,2:4]-antenna[:,:2],axis=1);injected_error=np.linalg.norm(g[:,2:4]-antenna[:,:2],axis=1)
        results.append({'route':seq,'event_index':i,'rows':len(g),'natural_receiver_horizontal_RMSE_m':float(np.sqrt(np.mean(raw_error**2))),'injected_receiver_horizontal_RMSE_m':float(np.sqrt(np.mean(injected_error**2))),'injection_reduces_actual_receiver_horizontal_error_rows':int(np.sum(injected_error<raw_error)),'protocol':'common initialization-conditioned NED; reference lever arm via offline ZYX rotations and Slerp; not absolute geodetic origin','SHA':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [referencepath,icpath,stress/'natural.csv',stress/'loss30_bias10.csv']}})
(OUT/'injection_cancellation.json').write_text(json.dumps({'events':results,'truth_use':'offline only','risk_proxy_is_not_error_probability':True},indent=2)+'\n');print(json.dumps(results))
