#!/usr/bin/env python3
"""Build in a copied OCI filesystem using existing unprivileged Bubblewrap."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from context_integrity import verify_context

p=argparse.ArgumentParser();p.add_argument('base_run');p.add_argument('context_run');p.add_argument('--resume-from');a=p.parse_args()
root=Path(__file__).resolve().parents[1];out=Path(os.environ['LIO_GINS_RUN_DIR'])
base=Path(a.base_run).resolve();prepared=Path(a.context_run).resolve()
if not base.is_relative_to(root/'outputs') or not prepared.is_relative_to(root/'outputs'):raise ValueError('project runs required')
base_manifest=json.loads((base/'manifest.json').read_text())
if base_manifest['status']!='PASSED':raise ValueError('base pull was not verified')
context=prepared/'container_context';verify_context(prepared)
rootfs=out/'rootfs'
source=base/'bundle/rootfs'
if a.resume_from:
    previous=Path(a.resume_from).resolve()
    if not previous.is_relative_to(root/'outputs') or json.loads((previous/'manifest.json').read_text())['status']!='FAILED':raise ValueError('only a retained failed project build may be resumed')
    source=previous/'rootfs'
    # Check sealed real files before reusing a failed package cache/rootfs.
    for line in (previous/'SHA256SUMS').read_text().splitlines():
        expected,name=line.split('  ',1);path=previous/name
        if not path.is_symlink():
            h=hashlib.sha256()
            with path.open('rb') as f:
                for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
            if h.hexdigest()!=expected:raise ValueError('failed build input modified: '+name)
subprocess.run(['cp','-a','--reflink=auto',str(source),str(rootfs)],check=True)
ws=rootfs/'opt/catkin_ws/src';ws.mkdir(parents=True,exist_ok=True)
for name in ['fast_lio','livox_ros_driver']:
    shutil.copytree(context/name,ws/name,dirs_exist_ok=True)
    for path in (ws/name).rglob('*'):
        if path.is_file():os.utime(path,None)
shutil.copy2(root/'containers/build_rootless_inside.sh',rootfs/'opt/build_rootless_inside.sh')
shutil.copy2(context/'run_inside.sh',rootfs/'opt/run_inside.sh')
packages=['fakeroot','build-essential','cmake','libeigen3-dev','libpcl-dev','python3-dev','python3-numpy','ros-noetic-pcl-ros','ros-noetic-eigen-conversions','ros-noetic-tf','ros-noetic-geometry-msgs','ros-noetic-nav-msgs','ros-noetic-sensor-msgs','ros-noetic-message-generation','ros-noetic-rosbag']
probe=subprocess.run(['dpkg-query','--admindir='+str(rootfs/'var/lib/dpkg'),'-W','-f=${db:Status-Status}\n',*packages],capture_output=True,text=True)
reuse=probe.returncode==0 and probe.stdout.splitlines()==['installed']*len(packages)
argv=['bwrap','--unshare-user','--uid','0','--gid','0','--die-with-parent','--new-session','--bind',str(rootfs),'/',
      '--clearenv','--setenv','PATH','/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin','--setenv','LANG','C.UTF-8',
      '--setenv','PROJECT_REUSE_INSTALLED_PACKAGES','1' if reuse else '0',
      '--proc','/proc','--dev','/dev','--ro-bind','/etc/resolv.conf','/etc/resolv.conf','--chdir','/',
      '/bin/bash','/opt/build_rootless_inside.sh']
(out/'rootless_build_identity.json').write_text(json.dumps({'base_run':str(base),'prepared_run':str(prepared),'argv':argv,'base_pull_identity':json.loads((base/'pull_identity.json').read_text()),'network':'host namespace during package download only; no host network changes','host_privilege_escalation':False,'rootfs_ownership':'single UID mapping; fakeroot for package metadata','context_manifest_sha256':hashlib.sha256((prepared/'context_sha256.json').read_bytes()).hexdigest()},indent=2)+'\n')
subprocess.run(argv,check=True)
binary=rootfs/'opt/catkin_ws/devel/lib/fast_lio/fastlio_mapping'
if not binary.is_file():raise ValueError('missing built FAST-LIO executable')
identity={'runtime':'bubblewrap_user_namespace','build_run':str(out),'rootfs':str(rootfs),'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'base_oci_digest':json.loads((base/'pull_identity.json').read_text())['upstream_manifest_sha256'],'prepared_run':str(prepared),'built':True}
(out/'derived_rootfs_identity.json').write_text(json.dumps(identity,indent=2)+'\n')
(root/'containers/derived_rootfs.local.json').write_text(json.dumps(identity,indent=2)+'\n')
print(json.dumps(identity,indent=2),flush=True)
