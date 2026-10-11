# 传感器接口与实施边界

内部坐标为 NED，m；`R_A_B` 将 B 向量变换到 A，四元数 xyzw。外层状态是 ADIS 中心 3D 位置，FAST-LIO2 姿态为外部输入。共用 KF 使用分解求解与 Joseph 更新，Q 只进入协方差。NIS 使用完整 3D 残差，Huber 使用一次名义创新归一化后放大 R；这些是已有强对照的准备实现，无真实调参证据。

ADIS 文本为 rad/m/s 增量，原值进入 KF-GINS，不再次乘 dt。F9P 是 SPP，lat/lon 为度，std 为 m，只平方一次。零、负、非有限 std 拒绝，原行保留；任何以后采用的噪声下限须对所有方法共用并在 P3 记录。NavSatFix 方差不能套用 std 平方函数。

时间必须给显式 GPS week+SOW；官方 GPS−UTC=18 s 仅对适用采集日期使用，并须与 bag header 核对。KF-GINS 输出 week 列实际恒为 0（源码 writeNavResult），不能当真实 GPS week；官方 demo 周号由 reference/输入元数据取 2017。building00周号由bag及自定义原始IMU确认2364（UTC2025-04-27）。

`src/evaluation/reference.py` 将 KF-GINS LLH 11 列与 i2Nav local NED 10 列分开。在线 adapters/fusion 不加载 reference。评价保留缺失覆盖率，不跨真值空洞；机器人数据的重复时间处理须重新登记，不能套官方 demo 的规则。

固定 calibration 核实 GNSS 杆臂 `[0,-0.07,-0.365]` m，FRD。AT128 外参按原注释 `P_i=R_i_l P_l+t_i_l` 解读，不能凭 `T_lidar_imu` 字段名反向使用。真实开发IMU增量与文本256条交叉核对已通过；点云20帧时间字段/单调检查通过。初始化协议为configs/initialization_protocol.json中事先声明的单参考历元备用协议；地理原点仍未知。完整LIO与强基线未通过，pipeline_ready=false。

P2 候选时间策略为最多一个扫描周期的有界缓冲插值，必须输出测量时间、可用时间和延迟；还未在实测数据上固定/验证，因此不能声称实时。LIO reset/倒序/失效不得静默拼接。没有实现或标定新的运动验证恢复机制；r01–r03 搜索预算尚未使用。

初始化不读完整真值。优先官方/因果对准；若不可行，只按目标 §5.4 明确导出一个固定初始历元，算法侧不再读参考。若官方 local NED 地理原点缺失，按 §5.5 在查看误差前登记共用的一次初始平移，报告“初始位置条件化误差”。


P2真实核对：256个ADIS自定义增量与文本最大差约5e-10，GPS周2364；标准ROS速率与文本增量不是简单实测dt乘积。F9P前4条LLH和ENU协方差与文本std平方一致，约0.254ms时间差符合三位小数SOW舍入范围，不用真值调偏移。所有方法共用原文本时间。

Noetic/Bubblewrap构建和ROS启动检查已真实通过。新日志记录scan_end、ROS clock可用时刻、wall日志时刻、有效点数和平均点面残差；这些诊断不当作增量协方差。后端采用两端点有界插值，最大跨度0.15s，缓存记录max(scan_end,ROS clock+10ms时钟刻度)并取累计最大作为可用时刻分辨率上界，不能称真实现场测量延迟。尚在运行的真实前端未完成缓存验证，pipeline_ready仍false。

B6固定恢复属于成熟分阶段策略的局部对照：同一个名义创新决定Huber倍率，再乘有限平方衰减的R保护。不能先放大R再让Huber分数变小。该控制不读运动验证或真值，不冒充完整Dual-ACKF复现。开发事件/调参上限已事先登记configs/development_experiment_protocol.json；P候选尚未实现。
