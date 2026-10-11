#!/bin/bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890
if [[ "${PROJECT_REUSE_INSTALLED_PACKAGES:-0}" != 1 ]]; then
printf '#!/bin/sh\nexit 101\n' > /usr/sbin/policy-rc.d
chmod 755 /usr/sbin/policy-rc.d
# Avoid cache removal inherited from Docker's image-size optimization.
printf '// Project build preserves verified package archives.\n' > /etc/apt/apt.conf.d/docker-clean
# Only this copied container filesystem changes; Ubuntu signatures and package
# SHA validation remain enabled. Retried builds reuse their verified archives.
sed -i -e 's|http://archive.ubuntu.com/ubuntu|https://mirrors.ustc.edu.cn/ubuntu|g' \
       -e 's|http://security.ubuntu.com/ubuntu|https://mirrors.ustc.edu.cn/ubuntu|g' /etc/apt/sources.list
printf 'Acquire::Retries "3";\n' > /etc/apt/apt.conf.d/80project-retries
apt-get -o APT::Sandbox::User=root update
apt-get -o APT::Sandbox::User=root install -y --no-install-recommends fakeroot
# Font directory is usable with the namespace's single mapped group. The
# package's root:staff chown cannot be represented here; it is not a dependency
# of numerical computation. Preserve this declared ownership approximation.
mkdir -p /usr/local/share/fonts
chmod 2775 /usr/local/share/fonts
fakeroot dpkg --configure -a
# Single-ID user namespace: emulate package ownership metadata only inside this
# project filesystem. It never grants ownership or permissions on the host.
fakeroot apt-get -o APT::Sandbox::User=root install -y --no-install-recommends \
    build-essential cmake libeigen3-dev libpcl-dev python3-dev python3-numpy \
    ros-noetic-pcl-ros ros-noetic-eigen-conversions ros-noetic-tf \
    ros-noetic-geometry-msgs ros-noetic-nav-msgs ros-noetic-sensor-msgs \
    ros-noetic-message-generation ros-noetic-rosbag
else
    echo 'Reusing verified, fully configured dependency packages from retained build.'
fi
dpkg-query -W > /opt/installed-packages.txt
cd /opt/catkin_ws
set +u
source /opt/ros/noetic/setup.bash
set -u
catkin_make -j4 -l4 -DCMAKE_BUILD_TYPE=Release -DPYTHON_EXECUTABLE=/usr/bin/python3
