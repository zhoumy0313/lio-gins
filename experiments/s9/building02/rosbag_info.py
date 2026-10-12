#!/usr/bin/env python3
"""Run one verified building00 bag in a restricted container and exclusive recorder output."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from gate import metadata_access

p=argparse.ArgumentParser();p.add_argument('bag');p.add_argument('--freeze');a=p.parse_args()
root=Path(__file__).resolve().parents[3];bag=Path(a.bag).resolve()
seq=bag.stem;role='s9_prospective_heldout';metadata_access(seq);access=None
locations=json.loads((root/'configs/data_locations.json').read_text())
expected_bag=(root/locations['dataset_root']/seq/bag.name).resolve()
if bag!=expected_bag:p.error('bag must be the registered development original')
audit=json.loads((root/'artifacts/s9/building02/data_manifest.json').read_text());item=next(f for f in audit['files'] if f['schema']=='rosbag_v2');st=bag.stat()
assert st.st_size==item['size_bytes'] and st.st_mtime_ns==item['mtime_ns'] and st.st_ctime_ns==item['ctime_ns']
bag_sha=item['sha256']
out=Path(os.environ['LIO_GINS_RUN_DIR'])
rootless=root/'containers/derived_rootfs.local.json'
lock=root/'containers/derived_image.local.json'
if rootless.exists():
    image=json.loads(rootless.read_text());rootfs=Path(image['rootfs'])
    build_manifest=json.loads((Path(image['build_run'])/'manifest.json').read_text())
    if build_manifest['status']!='PASSED':raise ValueError('rootless build not completed and sealed')
    binary=rootfs/'opt/catkin_ws/devel/lib/fast_lio/fastlio_mapping'
    if hashlib.sha256(binary.read_bytes()).hexdigest()!=image['binary_sha256']:raise ValueError('frontend binary changed')
    (out/'container_hosts').write_text('127.0.0.1 localhost lio-replay\n::1 localhost ip6-localhost\n')
    (out/'container_hostname').write_text('lio-replay\n')
    argv=['bwrap','--unshare-all','--hostname','lio-replay','--uid','0','--gid','0','--die-with-parent','--new-session','--cap-drop','ALL',
          '--clearenv','--setenv','PATH','/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin','--setenv','LANG','C.UTF-8',
          '--tmpfs','/']
    # Build mount points in a private temporary root, then make its top-level
    # read-only. Every original OCI subtree remains separately read-only.
    for entry in sorted(rootfs.iterdir()):
        if entry.name in {'proc','dev','tmp','input','output'}:continue
        if entry.name=='etc':
            argv+=['--dir','/etc']
            for child in sorted(entry.iterdir()):
                if child.name in {'hosts','hostname'}:continue
                if child.is_symlink():argv+=['--symlink',os.readlink(child),'/etc/'+child.name]
                else:argv+=['--ro-bind',str(child),'/etc/'+child.name]
            argv+=['--ro-bind',str(out/'container_hosts'),'/etc/hosts','--ro-bind',str(out/'container_hostname'),'/etc/hostname']
        elif entry.is_symlink():argv+=['--symlink',os.readlink(entry),'/'+entry.name]
        else:argv+=['--ro-bind',str(entry),'/'+entry.name]
    argv+=['--ro-bind',str(root/'containers/run_inside.sh'),'/opt/run_inside.sh',
           '--proc','/proc','--dev','/dev','--tmpfs','/tmp','--dir','/input',
           '--ro-bind',str(root/'containers/shutdown_clock.py'),'/tmp/shutdown_clock.py',
           '--ro-bind',str(bag),'/input/'+bag.name,'--bind',str(out),'/output','--remount-ro','/','--chdir','/',
           '/bin/bash','-c','source /opt/ros/noetic/setup.bash; rosbag info --yaml /input/'+bag.name+' > /output/rosbag_info.yaml']
elif lock.exists():
    image=json.loads(lock.read_text())
    argv=['docker','run','--rm','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges',
          '--user',f'{os.getuid()}:{os.getgid()}','--tmpfs','/tmp:rw,nosuid,nodev,size=1g',
          '--mount',f'type=bind,src={bag},dst=/input/{bag.name},readonly',
          '--mount',f'type=bind,src={out},dst=/output',image['image_id'],'/input/'+bag.name]
else:
    print('BLOCKED: no verified isolated frontend environment',file=sys.stderr);sys.exit(2)
(out/'frontend_input_identity.json').write_text(json.dumps({'bag':str(bag),'sequence':seq,'role':role,'performance_opened':False,'reference_access':False,'freeze_id':access['freeze_id'] if access else None,'sha256':bag_sha,'image':image,'sensors':['AT128','ADIS16465'],'timing_kind':'rosbag_replay_wall_and_logged_frontend_processing','replay_rate':1.0,'runtime_overlay_sha256':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [root/'containers/run_inside.sh',root/'containers/shutdown_clock.py']},'shutdown_clock_policy':'advance clock only after EOF to wake Rate.sleep; no sensor messages'},indent=2)+'\n')
print(json.dumps({'argv':argv}),flush=True)
sys.exit(subprocess.run(argv).returncode)
