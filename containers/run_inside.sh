#!/bin/bash
set -euo pipefail
source /opt/ros/noetic/setup.bash
source /opt/catkin_ws/devel/setup.bash
export ROS_HOME=/output/ros
export ROS_MASTER_URI=http://127.0.0.1:11311
export ROS_IP=127.0.0.1
mkdir -p "$ROS_HOME"
if [[ $# -ne 1 || ! -f "$1" ]]; then
    echo 'Supply a verified bag under the read-only /input mount.' >&2
    exit 2
fi
cp /opt/installed-packages.txt /output/installed-packages.txt
roscore > /output/roscore.log 2>&1 &
core_pid=$!
cleanup() {
    [[ -z "${lio_pid:-}" ]] || kill -INT "$lio_pid" 2>/dev/null || true
    kill -INT "$core_pid" 2>/dev/null || true
}
trap cleanup EXIT
ready=false
for _ in $(seq 1 30); do
    if rosparam list >/dev/null 2>&1; then ready=true; break; fi
    sleep 1
done
[[ "$ready" == true ]] || exit 3
rosparam set use_sim_time true
roslaunch fast_lio mapping_i2nav.launch rviz:=false > /output/fastlio.log 2>&1 &
lio_pid=$!
# Host preparation fixes the copied YAML output_path to /output before build.
sleep 3
kill -0 "$lio_pid"
rosbag info --yaml "$1" > /output/bag_info.yaml
rosbag play --clock --delay=2 --rate=1.0 "$1" --topics /hesai/at128/points /adi/adis16465/imu > /output/rosbag_play.log 2>&1
sleep 3
kill -INT "$lio_pid"
wait "$lio_pid"
lio_pid=''
[[ -s /output/trajectory.csv ]] || exit 4
