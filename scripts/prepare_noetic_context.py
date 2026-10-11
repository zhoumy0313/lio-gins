#!/usr/bin/env python3
"""Prepare a pinned AT128-only build context; no daemon or host package changes."""
import difflib
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

root=Path(__file__).resolve().parents[1]
out=Path(os.environ['LIO_GINS_RUN_DIR'])
context=out/'container_context'
context.mkdir(exist_ok=False)
deps=[]
for name,folder,role in [('livox_ros_driver','livox_ros_driver','message_definitions_only'),('FAST_LIO','FAST_LIO_original','attribution_and_diff_reference_only')]:
    repo=root/'third_party'/folder
    def git(*argv):return subprocess.check_output(['git','-C',str(repo),*argv],text=True).strip()
    if git('status','--porcelain'):raise RuntimeError(f'dirty dependency {name}')
    commit=git('rev-parse','HEAD')
    deps.append({'name':name,'url':git('remote','get-url','origin'),'commit':commit,'role':role,
                 'submodules':git('submodule','status','--recursive'),'built_as_original_system':False})
lockpath=root/'configs/dependencies.lock.json'
if lockpath.exists():
    frozen=json.loads(lockpath.read_text())['dependencies']
    if [(x['name'],x['commit']) for x in frozen]!=[(x['name'],x['commit']) for x in deps]:
        raise RuntimeError('dependency differs from frozen lock')
else:
    lockpath.write_text(json.dumps({'dependencies':deps},indent=2)+'\n')
up=root/'third_party/i2Nav-Robot-Baseline/FAST_LIO'
shutil.copytree(up,context/'fast_lio')
configpath=context/'fast_lio/config/i2nav.yaml'
text=configpath.read_text()
assert text.count('output_path: ""')==1
configpath.write_text(text.replace('output_path: ""','output_path: "/output"'))
file=up/'src/laserMapping.cpp'
original=file.read_text();modified=original
replacements={
 'fprintf(pose_fp, "%lf ", Measures.lidar_beg_time);':'fprintf(pose_fp, "%.9f ", Measures.lidar_end_time); // logged state is scan-end',
 'data[0] = Measures.lidar_beg_time;':'data[0] = Measures.lidar_end_time;',
 'fout_pre.open(DEBUG_FILE_DIR("mat_pre.txt"),ios::out);':'fout_pre.open(root_dir + "/mat_pre.txt",ios::out);',
 'fout_out.open(DEBUG_FILE_DIR("mat_out.txt"),ios::out);':'fout_out.open(root_dir + "/mat_out.txt",ios::out);',
 'fout_dbg.open(DEBUG_FILE_DIR("dbg.txt"),ios::out);':'fout_dbg.open(root_dir + "/dbg.txt",ios::out);',
 'cov_fp = fopen(cov_log_dir.c_str(), "w");':'cov_fp = fopen(cov_log_dir.c_str(), "w");\n    if (!pose_fp || !cov_fp) { ROS_ERROR("LIO-GINS output directory must exist and be writable"); return 1; }',
 'T1[time_log_counter] = Measures.lidar_beg_time;':'T1[time_log_counter] = Measures.lidar_end_time;'
}
for old,new in replacements.items():
    if modified.count(old)!=1:raise RuntimeError('upstream source changed; refuse ambiguous patch')
    modified=modified.replace(old,new)
patch=''.join(difflib.unified_diff(original.splitlines(True),modified.splitlines(True),fromfile='a/src/laserMapping.cpp',tofile='b/src/laserMapping.cpp'))
patchpath=root/'patches/logging/fastlio_scan_end_and_run_outputs.patch'
if patchpath.exists() and patchpath.read_text()!=patch:raise RuntimeError('refuse changing existing instrumentation patch')
patchpath.write_text(patch)
shutil.copy2(patchpath,context/'logging.patch')
r=subprocess.run(['patch','--batch','-p1','-i',str(context/'logging.patch')],cwd=context/'fast_lio')
r.check_returncode()
msg=context/'livox_ros_driver/msg';msg.mkdir(parents=True)
for name in ['CustomMsg.msg','CustomPoint.msg']:
    shutil.copy2(root/'third_party/livox_ros_driver/livox_ros_driver/msg'/name,msg/name)
shutil.copy2(root/'third_party/livox_ros_driver/LICENSE.txt',msg.parent/'LICENSE.txt')
(msg.parent/'CMakeLists.txt').write_text('''cmake_minimum_required(VERSION 3.0.2)
project(livox_ros_driver)
find_package(catkin REQUIRED COMPONENTS std_msgs message_generation)
add_message_files(FILES CustomMsg.msg CustomPoint.msg)
generate_messages(DEPENDENCIES std_msgs)
catkin_package(CATKIN_DEPENDS std_msgs message_runtime)
''')
(msg.parent/'package.xml').write_text('''<package format="2"><name>livox_ros_driver</name><version>0.0.0</version><description>Project message-only compatibility adapter from pinned Livox definitions; no driver or SDK.</description><maintainer email="codex@localhost">Codex checkpoint</maintainer><license>MIT</license><buildtool_depend>catkin</buildtool_depend><build_depend>message_generation</build_depend><depend>std_msgs</depend><exec_depend>message_runtime</exec_depend></package>
''')
shutil.copy2(root/'containers/Dockerfile.noetic',context/'Dockerfile')
shutil.copy2(root/'containers/run_inside.sh',context/'run_inside.sh')
manifest={str(p.relative_to(context)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(context.rglob('*')) if p.is_file()}
(out/'context_sha256.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'context':str(context),'logging_patch_verified_apply':True,'build_executed':False,'at128_only':True,'dependencies':deps},indent=2))
