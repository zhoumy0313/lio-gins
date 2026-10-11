#!/usr/bin/env python3
"""Read-only metadata audit for preregistered routes. No heldout accuracy evaluation."""
import hashlib
import json
import os
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from src.adapters.sensor_text import load_sensor,audit_table
from src.evaluation.reference import load_i2nav_local_ned

root=Path(__file__).resolve().parents[1]
out=Path(os.environ['LIO_GINS_RUN_DIR'])
checks=json.loads((root/'third_party/i2Nav-Robot/sha256sum/sha256sum.json').read_text())
meta=json.loads((root/'third_party/i2Nav-Robot/sequence_detail/i2nav_robot.json').read_text())
locations=json.loads((root/'configs/data_locations.json').read_text())
dataset=root/locations['dataset_root']
records=[]
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
for sequence,role in [('building00','development'),('parking00','heldout_closed')]:
    for suffix,schema in [('.bag','rosbag_v2'),('_ADIS16465_IMU.txt','adis_increment'),('_F9P_GNSS.pos','f9p_spp'),('_groundtruth.nav','i2nav_local_ned'),('_trajectory.csv','tum_xyzw'),('_MID360_IMU.txt','auxiliary_identity_only'),('_OEM7_GNSS.pos','auxiliary_identity_only'),('_RANGER_ODO.txt','auxiliary_identity_only')]:
        name=sequence+suffix;path=dataset/sequence/name
        print('Auditing '+name,flush=True)
        item={'sequence':sequence,'role':role,'filename':name,'path':str(path),'schema':schema,'status':'MISSING',
              'upstream_bag_sha256':checks.get(name),'size_bytes':None,'sha256':None,'performance_opened':False}
        if path.exists():
            try:
                item.update(status='PRESENT',size_bytes=path.stat().st_size,sha256=sha(path))
                if schema=='rosbag_v2':
                    with path.open('rb') as f:header=f.read(13)
                    if header!=b'#ROSBAG V2.0\n' or item['sha256']!=checks[name]:raise ValueError('bag magic/upstream SHA mismatch')
                    item['bag_topics_audit']='pending_container_or_rosbag_reader'
                elif schema in ['adis_increment','f9p_spp']:
                    item['metadata']=audit_table(load_sensor(path,schema),schema)
                    if item['metadata']['backward_times']:item['requires_input_decision']=True
                elif schema!='auxiliary_identity_only':
                    a=load_i2nav_local_ned(path) if schema=='i2nav_local_ned' else np.loadtxt(path,ndmin=2)
                    if schema=='tum_xyzw' and a.shape[1]!=8:raise ValueError('TUM xyzw expects 8 columns; verify actual file delimiter/schema')
                    item['metadata']={'rows':len(a),'time_min':float(a[:,0].min()),'time_max':float(a[:,0].max()),'backward_times':int((np.diff(a[:,0])<0).sum()),'coordinate_frame':'local_NED_ADIS_center'}
                item['identity_assurance']='official_checksum' if schema=='rosbag_v2' else 'local_identity_only_no_upstream_text_checksum'
            except (ValueError,OSError) as e:item.update(status='FAILED',error=str(e))
        records.append(item)
manifest={'goal_id':'LIO-GINS-R1','source_commit':'2ffdca6d56e6432d4daf27c070e570171548f32d','files':records,
          'official_sequence_metadata':{s:meta['sequences'][s] for s in ['building00','parking00']},
          'license':'official README: GPLv3, academic use only','raw_read_only_policy':True,'holdout_performance_opened':False,
          'backups':{'local_preserved':True,'remote_numeric_backed_up':False,'raw_data_backed_up':False}}
(out/'DATA_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
(root/'data/manifests/DATA_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'present':sum(x['status']=='PRESENT' for x in records),'missing':[x['filename'] for x in records if x['status']=='MISSING'],'failed':[x['filename'] for x in records if x['status']=='FAILED']},indent=2))
sys.exit(0 if all(x['status']=='PRESENT' for x in records if x['schema']!='auxiliary_identity_only') else 2)
