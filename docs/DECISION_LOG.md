# Decision log

- 2026-10-11: Start architecture A in the new workspace. No project remote exists; local checkpoints only. No original data present. Preserve all supplied files.

- 2026-10-11 P1: Keep architecture A. No silent switch to GNSS/INS-only research; official demo is not robot-data evidence. No candidate search or holdout evaluation.
- Official demo reference has 2799 equal-time pairs with non-identical rows. Preserve raw input and failed health check; use first-row policy only for demo and report last-row sensitivity (horizontal RMSE 0.01220946 vs 0.01216766 m).
- AT128 logging timestamp differs from scan-end state: keep a separate instrumentation patch, applied only in copied build context. Compilation/replay pending.
- B6 must include an explicitly labeled local adaptation of known recovery covariance protection. Novelty unverified; no manuscript claims or author list.
- Public data access exhausted bounded probes. New Docker/system service requires user authorization under AGENTS/goal; all user actions consolidated once.

- P1 continuation 02: Verify original FAST-LIO CMake consumes generated Livox and Pose6D headers; add explicit exported-message target dependencies in a separate build patch. Reject changed prepared inputs before container build. No algorithm change, no new data/permissions, no heldout results. Same external blocker revalidated for the second consecutive goal turn.

- Third consecutive goal-turn blocking audit: actual raw/reference directories are empty, no runtime/derived image and no live project job. User action unchanged. Mark blocked rather than repeating automatic continuations or claiming P2–P7 completion; preserve full LIO-GINS-R1 scope and evidence gates.


2026-10-11数据恢复：保留data/i2nav-dataset原件并忽略Git；完整bag SHA与官方匹配。现有用户命名空间可用，选择项目内锁定OCI+Bubblewrap替代缺失Docker，不安装宿主服务。rootless多UID所有权近似及所有构建/启动失败保留，原算法参数不变。

2026-10-11 P2初始化：官方机器人初始配置/地理原点未公开查得，选择目标§5.4的首参考单历元known-initial-state备用协议；初始F9P位置、姿态/速度一次给定、共同初始平移，协议在任何机器人性能前提交a66a812。不能宣称解决无先验启动或绝对WGS84精度。

2026-10-11 B1开发校准：预声明STD倍数0.5/1/2，全部覆盖100%，选×2的自然水平RMSE3.702869m；该选择仅开发，全部其他配置和首轮误标B2的历史输出保留，更正B1身份。不是算法新增收益。

2026-10-11 P3预注册：LIO全球误差尚未打开前登记共同Q四档、NIS/Huber有限阈值与B6最多12档、7类人工GNSS压力试验各3固定起点/方向、自然输入质量分段、主要目标与代价约束。只修改派生观测；在线代码不能读取event_manifest或reference。候选机制预算0/3。
