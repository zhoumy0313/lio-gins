# FAST-LIO2 源码审计与未验证项

实际基线固定于 i2Nav-Robot-Baseline `6c602f8d974fbe5be1183771541c90057e9e3bb6`；原方法归属 hku-mars FAST_LIO，参考 commit 见 `configs/dependencies.lock.json`。该参考 clone 的 ikd-Tree 子模块未初始化，仅作阅读；实际适配版已内含 ikd-Tree。所有上游 tracked source clean；没有算法补丁。

官方配置确认为 AT128 `/hesai/at128/points` + ADIS `/adi/adis16465/imu`，lidar_type=4、128线、timestamp_unit=0（秒），在线时间同步关闭。保留官方 point_filter_num=4、三个迭代与 0.5 m surf/map 滤波参数，没有削弱前端精度。PCD 保存原配置即关闭。

`preprocess.h` 的 Hesai 点格式是 float xyz/intensity、double timestamp、uint16 ring。`hesai_handler()` 从逐点绝对 timestamp 减 header stamp，秒换为内部毫秒；同步器以最后保留点 curvature/1000 推出 scan-end。逐点时间是否有序、header 是否 scan-start、过滤后最后点与原始末点差异，必须在实际 bag 检查，不能只据源码宣称已验证。

`state_point.pos/rot` 是 IMU pose，点变换先由 lidar 外参到 IMU，再由状态到局部 world；ADIS 是当前 IMU。输出 ROS odometry 的 stamp 是 scan-end，但 `dump_lio_state_to_log()` 的 trajectory/STD 时间用了 scan-begin。单独的 `patches/logging/fastlio_scan_end_and_run_outputs.patch` 只修日志时间并把 debug 输出导向独立 run，增加文件打开检查。补丁已对复制源码成功应用，上游原件保持不变。尚未在 ROS 编译或实测中验证。

AT128 不需运行 Livox 硬件驱动，但 CMake/头文件依赖 `livox_ros_driver/CustomMsg`。构建上下文只复制锁定 MIT 消息定义，生成同名 message-only 兼容包；不是完整驱动/SDK，不能宣称可用于 Livox 数据。适配范围与许可证保留在上下文中。

Noetic 官方 linux/amd64 registry manifest 已核实 digest，见 `containers/base_image.lock.json`。容器 recipe 使用该 digest、记录容器 apt 包清单、最多 -j4；原 bag 只读、独立输出可写、无 host network/privileged/home/socket 挂载。运行脚本仍未实测，bag播放结束后的前端排空及覆盖率必须核查；不能把 rate=1 的回放 wall time 直接当算法计算时延。

构建尝试 `python3 scripts/build_noetic.py <prepared-run>` 实际退出127：Docker不存在。没有拉取 layer、没有 build，也没有 ROS 前端轨迹。此阻塞需要用户提供已可用的容器运行时或明确授权系统服务安装。

续检补充：共同源同时包含 `livox_ros_driver/CustomMsg.h` 与 `fast_lio/Pose6D.h`，但可执行目标原先没有依赖相应生成目标。`patches/build/fastlio_generated_message_dependencies.patch` 单独增加 catkin exported-message dependencies，保留算法实现与参数。新上下文为 `outputs/20261011T052215556145Z_P1_a2b55b2f/container_context`，构建入口实际核验83个文件后才检查运行时；修改/缺失/额外文件或符号链接拒绝构建。新增3项完整性测试通过，实际ROS编译仍未验证。旧上下文及日志补丁保留。
