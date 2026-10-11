# LIO-GINS-R1 — 当前状态

2026-10-11。数据已取得并验证；完整目标尚未完成。P0 完成，P1 容器构建进行中，P2 真实接口检查已开始。

- `data/i2nav-dataset` 的16个原件只读保留；两个bag SHA与固定官方值完全一致。审计exit0：`20261011T112420385892Z_P1_ef2f5c4e`，无缺失/失败文件。
- building00 IMU248928条、F9P1244条，全部有限、时间无重复/倒序，F9P标准差均有效。
- 两个bag索引各12个连接；building00 AT12812443帧。256条开发IMU样本确认GPS周2364，UTC2025-04-27，18秒转换与文本时间最大偏差0.590微秒。20帧点云字段和逐点时间单调检查通过；不是全程时间/轴向审计。
- 原生KF-GINS官方demo先前通过；尚未形成真实路线精度或候选收益。真实KF-GINS将先登记初始化和评价条件。
- Docker/Podman仍缺，但现有Bubblewrap用户命名空间与无网络隔离测试exit0。正在拉取锁定Noetic OCI并尝试项目内rootless构建；没有sudo/全局安装/网络配置变更。真实进程和日志见最新P1输出目录。
- P3强基线仍未齐备，候选修订0/3，parking00性能仍关闭，所有科学成功字段false。

证据：[数据及接口审计](../artifacts/data_audit)、[状态JSON](GOAL_STATE.json)、[运行索引](RUN_REGISTER.csv)、[人工清单](USER_ACTION_REQUIRED.md)。旧数据缺失报告属于历史；以此页和状态JSON为当前索引。
