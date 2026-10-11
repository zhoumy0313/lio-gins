#!/usr/bin/env python3
"""Extend a verified context with time/health logging only; no estimator changes."""
import argparse,difflib,hashlib,json,os,shutil,subprocess
from pathlib import Path
from context_integrity import verify_context
p=argparse.ArgumentParser();p.add_argument('prepared_run');a=p.parse_args();root=Path(__file__).resolve().parents[1];out=Path(os.environ['LIO_GINS_RUN_DIR']);prepared=Path(a.prepared_run).resolve();verified=verify_context(prepared);context=out/'container_context';shutil.copytree(prepared/'container_context',context)
f=context/'fast_lio/src/laserMapping.cpp';original=f.read_text();s=original
replacements={
 'FILE *pose_fp, *cov_fp;':'FILE *pose_fp, *cov_fp;\n    FILE *interface_fp = fopen((root_dir + "/interface_events.csv").c_str(), "w");\n    if (!interface_fp) { ROS_ERROR("interface log cannot be opened"); return 1; }\n    fprintf(interface_fp, "scan_begin_unix,scan_end_unix,availability_ros_clock_unix,logged_wall_unix,effective_points,mean_abs_plane_residual_m,velocity_x,velocity_y,velocity_z\\n");',
 'dump_lio_state_to_log(pose_fp, cov_fp);':'dump_lio_state_to_log(pose_fp, cov_fp);\n                fprintf(interface_fp, "%.9f,%.9f,%.9f,%.9f,%d,%.9f,%.9f,%.9f,%.9f\\n", Measures.lidar_beg_time, Measures.lidar_end_time, ros::Time::now().toSec(), ros::WallTime::now().toSec(), effct_feat_num, res_mean_last, state_point.vel(0), state_point.vel(1), state_point.vel(2));\n                fflush(interface_fp);',
 'fout_out.close();':'fclose(interface_fp);\n    fout_out.close();'
}
for old,new in replacements.items():
 if s.count(old)!=1:raise ValueError('ambiguous instrumentation target')
 s=s.replace(old,new)
patch=''.join(difflib.unified_diff(original.splitlines(True),s.splitlines(True),fromfile='a/src/laserMapping.cpp',tofile='b/src/laserMapping.cpp'))
patchpath=root/'patches/logging/fastlio_availability_and_health.patch'
if patchpath.exists() and patchpath.read_text()!=patch:raise ValueError('do not overwrite a different instrumentation patch')
patchpath.write_text(patch);shutil.copy2(patchpath,context/'availability.patch');subprocess.run(['patch','--batch','-p1','-i',str(context/'availability.patch')],cwd=context/'fast_lio',check=True)
shutil.copy2(root/'containers/run_inside.sh',context/'run_inside.sh')
manifest={str(p.relative_to(context)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(context.rglob('*')) if p.is_file()}
(out/'context_sha256.json').write_text(json.dumps(manifest,indent=2)+'\n');(out/'parent_context.json').write_text(json.dumps({'parent_run':str(prepared),'parent_identity':verified,'patch':'logging_only_time_health_not_observation_management'},indent=2)+'\n');print(json.dumps({'context':str(context),'logging_only':True,'files':len(manifest)}))
