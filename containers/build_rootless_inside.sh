#!/bin/bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890
printf '#!/bin/sh\nexit 101\n' > /usr/sbin/policy-rc.d
chmod 755 /usr/sbin/policy-rc.d
apt-get -o APT::Sandbox::User=root update
apt-get -o APT::Sandbox::User=root install -y --no-install-recommends fakeroot
# Single-ID user namespace: emulate package ownership metadata only inside this
# project filesystem. It never grants ownership or permissions on the host.
fakeroot apt-get -o APT::Sandbox::User=root install -y --no-install-recommends \
    build-essential cmake libeigen3-dev libpcl-dev python3-dev python3-numpy \
    ros-noetic-pcl-ros ros-noetic-eigen-conversions ros-noetic-tf \
    ros-noetic-geometry-msgs ros-noetic-nav-msgs ros-noetic-sensor-msgs \
    ros-noetic-message-generation ros-noetic-rosbag
dpkg-query -W > /opt/installed-packages.txt
cd /opt/catkin_ws
source /opt/ros/noetic/setup.bash
catkin_make -j4 -l4 -DCMAKE_BUILD_TYPE=Release -DPYTHON_EXECUTABLE=/usr/bin/python3
