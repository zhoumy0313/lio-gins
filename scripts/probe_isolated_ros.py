#!/usr/bin/env python3
"""Probe ROS launch on the already verified bag without starting full playback."""
import argparse,json,os,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('previous_frontend_run');a=p.parse_args();previous=Path(a.previous_frontend_run).resolve();out=Path(os.environ['LIO_GINS_RUN_DIR'])
argv=json.loads((previous/'stdout.log').read_text().splitlines()[0])['argv']
i=argv.index('--remount-ro')
if argv[i+1]=='/etc':del argv[i:i+2]
# Keep the sealed previous hosts/hostname files as read-only inputs; redirect
# only the writable output bind to this new exclusive probe directory.
for i,v in enumerate(argv):
 if v=='--bind' and argv[i+1]==str(previous) and argv[i+2]=='/output':argv[i+1]=str(out)
program='''set -e
source /opt/ros/noetic/setup.bash
source /opt/catkin_ws/devel/setup.bash
export ROS_HOME=/output/ros
export ROS_MASTER_URI=http://127.0.0.1:11311
export ROS_IP=127.0.0.1
mkdir -p "$ROS_HOME"
python3 -c 'import socket; print(socket.getaddrinfo("localhost",11311))'
roscore > /output/roscore.log 2>&1 &
core_pid=$!
cleanup() { kill -INT "$core_pid" 2>/dev/null || true; }
trap cleanup EXIT
for n in $(seq 1 30); do
 if rosparam list >/dev/null 2>&1; then break; fi
 sleep 1
done
rosparam list
rosparam set use_sim_time true
roslaunch fast_lio mapping_i2nav.launch rviz:=false > /output/fastlio.log 2>&1 &
lio_pid=$!
sleep 3
kill -0 "$lio_pid"
rosbag info --yaml /input/building00.bag > /output/bag_info.yaml
kill -INT "$lio_pid"
wait "$lio_pid"
echo 'isolated ROS + FAST-LIO launch and bag index probe passed'
'''
argv=argv[:-3]+['/bin/bash','-c',program]
(out/'probe_argv.json').write_text(json.dumps(argv,indent=2)+'\n');subprocess.run(argv,check=True)
