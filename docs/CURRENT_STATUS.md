# LIO-GINS-R1 — 当前状态

2026-10-11。数据已取得并验证；完整目标尚未完成。P0 完成，P1 容器构建进行中，P2 真实接口检查已开始。

- `data/i2nav-dataset` 的16个原件只读保留；两个bag SHA与固定官方值完全一致。审计exit0：`20261011T112420385892Z_P1_ef2f5c4e`，无缺失/失败文件。
- building00 IMU248928条、F9P1244条，全部有限、时间无重复/倒序，F9P标准差均有效。
- 两个bag索引各12个连接；building00 AT12812443帧。256条开发IMU样本确认GPS周2364，UTC2025-04-27，18秒转换与文本时间最大偏差0.590微秒。20帧点云字段和逐点时间单调检查通过；不是全程时间/轴向审计。
- 原生KF-GINS官方demo先前通过；真实building00首轮KF-GINS通过：10Hz覆盖100%，水平RMSE3.845226m；初始化协议事先登记，仅首参考历元。还未达到完整强基线状态，无候选收益。
- Docker/Podman仍缺，但现有Bubblewrap用户命名空间与无网络隔离测试exit0。锁定Noetic OCI rootless构建已通过，run 20261011T130509928405Z_P1_4c5d376c exit0；隔离ROS启动/原bag索引冒烟检查20261011T131414920017Z_P2_17e494e3 exit0。回放早期挂载点/localhost元数据失败保留；修复后全程回放已启动，尚未完成。无sudo/宿主软件及网络配置变更。
- P3强基线仍未齐备，候选修订0/3，parking00性能仍关闭，所有科学成功字段false。

证据：[数据及接口审计](../artifacts/data_audit)、[状态JSON](GOAL_STATE.json)、[运行索引](RUN_REGISTER.csv)、[人工清单](USER_ACTION_REQUIRED.md)。旧数据缺失报告属于历史；以此页和状态JSON为当前索引。

B1预登记噪声STD×0.5/1/2的水平RMSE分别4.102491/3.845226/3.702869m，均覆盖100%；按规则选择×2。仅开发基线校准，无候选收益。见artifacts/robot_baselines/KF_noise_screen.json。
