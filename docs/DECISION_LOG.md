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

2026-10-11 P2关闭问题：首轮位姿完整但ROS Rate在EOF停钟时无法观察退出标志，最终SIGTERM造成原生计时导出缺失。原run/缓存保留并标记timing_complete=false。只增加EOF后的管理clock，不改估计器或播放时传感器；只读覆盖新launcher，sealed rootfs不修改。缺失timing文件的recorder预检查曾未封存退出证据，保留其exclusive配置目录并修复今后的预检查错误为FAILED/child未执行；旧退出码不补造。

P3屏选细化在首个外层精度结果前登记：共同Q四档，NIS四档、Huber四档、B6十二档（含15倍保护、0/2/5秒等待和5/15秒有限恢复）；以natural加三主要类别筛选，选中配置报告所有七类。LIO时刻插值跨度≤150ms，端点可用截止measurement+250ms，实际延迟保留；前端慢于预算会影响覆盖，而不是假装及时在线。

P2全程重放exit0（1286.7126s），EOF正常关闭，12440帧native timing完整；native处理均值17.3215ms、P95 22.7675ms、最大66.4257ms，范围不含输入预处理/发布/等待。34项接口/因果/滤波/独立评价检查exit0。重复比较脚本exit0只验证同输入/同帧/日志结构；并不证明数值一致。实际相同bag/binary两个局部轨迹3D差异RMS3.6013m、最大9.7876m，首次四舍五入位置差在80.199s，去掉初始坐标差异后仍有3.64m RMS；原因未证实。primary缓存在精度打开前按完整计时选定，不能改选更有利缓存。增加configs/frontend_sensitivity_protocol.json：最终候选与选中强对照在两缓存同参数重放、两者都满足原门槛，收益需超过收益跨缓存差异；不是独立路线复制。此前“检查通过”只能指执行/结构，不可把repeat结果写成数值稳定。

## 2026-10-11 15:43 UTC — P4科学门槛成立，冻结前适配通过

r03最后12配置耗尽总36主配置；不增加r04。固定参数同结构消融/两缓存证明目标增益22.7952%与24.0163%，正常/覆盖/差异门槛通过；保护衰减不被证实为新增贡献，缓坡等退化完整保留。贡献仅限定原始SPP锚接入的应用机制，不证明新KF/完整性或前端数值重复。57检查通过；80组合轨迹和日志精确一致、初始化/native/cache精确一致。153200969046类型错误exit1保留，154244545675校验复用完整sealed matrix后修复余项exit0。以这些证据科学冻结，再开启唯一parking00固定矩阵，禁止留出调参或事后推广消融。

## 2026-10-12 P5完成与后补反证

冻结parking00全部80对/210事件完成、原最强B4目标2.122390→P1.911108m（9.9549%），完整原表保留。后补长资格计划晚于首次测试访问，仅building00；90s在两个缓存目标2.285876/2.024895m均好于P且正常代价合格。撤回广义增量/充分归因支持，保留原窄集合事实。最终NO_ADDITIONAL_GAIN，停止36主配置后的探索，不切指标、不新留出、不新增r04、不生成投稿全文。依据GOAL§10.4/17.3交内部方法/实验草稿及P7恢复审计。

## 2026-10-12 P7条件结案

64项检查、80对原轨迹独立重算、B6/P原缓存字节恢复、1334run/379359文件完整性及交付一致性均exit0；resume0无实验进程。工程execution_complete=true仅本轮有界工作/负结果条件交付，研究分类NO_ADDITIONAL_GAIN，广义效益/新颖性/paper_ready=false。前端变化、无标志reset、clean-clone再构建未独立重跑和无异地备份明确保留限制，不作为已解决。无新候选、投稿、账号、费用或署名动作。
