#!/usr/bin/env python3
"""Bounded development GNSS identity/covariance check, no truth or accuracy."""
import json,os,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.adapters.rosbag_metadata import read_metadata,bounded_samples,decode_navsatfix
from src.adapters.sensor_text import unix_to_gps
root=Path(__file__).resolve().parents[1];out=Path(os.environ['LIO_GINS_RUN_DIR']);bag=root/'data/i2nav-dataset/building00/building00.bag';meta=read_metadata(bag);samples=bounded_samples(bag,meta,{'/ublox/f9p/fix':4})['/ublox/f9p/fix'];g=np.loadtxt(bag.parent/'building00_F9P_GNSS.pos');records=[]
for recorded,raw in samples:
 msg=decode_navsatfix(raw);week,sow=unix_to_gps(msg['stamp']);idx=int(np.argmin(abs(g[:,0]-sow)));row=g[idx];c=np.array(msg['covariance_ENU']).reshape(3,3);diag=np.diag(c);expected_ENU=row[[5,4,6]]**2
 records.append({'message':msg,'gps_week':week,'sow':sow,'original_text_row_id':idx,'timestamp_minus_text_s':sow-row[0],'record_minus_header_s':recorded-msg['stamp'],'llh_minus_text':(np.array(msg['llh_deg_m'])-row[1:4]).tolist(),'cov_ENU_minus_std_squared':(diag-expected_ENU).tolist(),'max_cov_offdiagonal':float(np.max(abs(c-np.diag(diag))))})
report={'sequence':'building00','role':'development','sample_count':len(records),'records':records,'reference_access':False,'holdout_performance_opened':False,'NavSatFix_covariance_rule':'ENU variance, reorder ENU->NED; do not square twice; text stores stdN/stdE/stdD','timestamp_precision_policy':'text SOW printed to 3 decimal places: tolerate half a millisecond plus floating serialization; all algorithms retain the same text measurement clock, not a truth-fitted shift'}
(out/'F9P_interfaces.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if any(abs(r['timestamp_minus_text_s'])>.0005005 or np.max(np.abs(r['llh_minus_text']))>1e-6 or np.max(np.abs(r['cov_ENU_minus_std_squared']))>1e-8 for r in records):raise ValueError('F9P bag/text sensor identity or covariance mismatch beyond serialization precision')
