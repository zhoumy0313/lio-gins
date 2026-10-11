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

p=argparse.ArgumentParser();p.add_argument('base_run');p.add_argument('context_run');a=p.parse_args()
root=Path(__file__).resolve().parents[1];out=Path(os.environ['LIO_GINS_RUN_DIR'])
base=Path(a.base_run).resolve();prepared=Path(a.context_run).resolve()
if not base.is_relative_to(root/'outputs') or not prepared.is_relative_to(root/'outputs'):raise ValueError('project runs required')
base_manifest=json.loads((base/'manifest.json').read_text())
if base_manifest['status']!='PASSED':raise ValueError('base pull was not verified')
context=prepared/'container_context';verify_context(prepared)
rootfs=out/'rootfs'
subprocess.run(['cp','-a','--reflink=auto',str(base/'bundle/rootfs'),str(rootfs)],check=True)
ws=rootfs/'opt/catkin_ws/src';ws.mkdir(parents=True)
for name in ['fast_lio','livox_ros_driver']:shutil.copytree(context/name,ws/name)
shutil.copy2(root/'containers/build_rootless_inside.sh',rootfs/'opt/build_rootless_inside.sh')
shutil.copy2(context/'run_inside.sh',rootfs/'opt/run_inside.sh')
argv=['bwrap','--unshare-user','--uid','0','--gid','0','--die-with-parent','--new-session','--bind',str(rootfs),'/',
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
