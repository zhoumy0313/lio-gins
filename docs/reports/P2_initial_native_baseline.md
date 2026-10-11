# P2：真实接口与首轮原生GNSS/INS对照

2026-10-11；前置数据checkpoint `2f9667c`，初始化协议先于评价提交于 `a66a812`。主线仍为A，未转为KF-GINS算法修改。

- bag原始自定义IMU增量与文本256条交叉核对通过，run `20261011T124207100595Z_P2_17b89dca` exit0：六轴最大绝对差约5e-10（rad/m/s），文本舍入精度内；标准ROS速率乘实际dt并不完全相同，KF-GINS直接用增量，不再乘dt。该采样核对不代表全程丢包审计。
- `scripts/export_initial_condition.py` 按已登记协议只读取首参考状态，run `20261011T124056742603Z_P2_e310122b` exit0。首参考SOW9064.0045；首可用IMUSOW9064.006595，offset0.002095s，给定速度推进此偏移。原点来自过去F9P及一次杆臂补偿；reference不进入在线估计。
- `scripts/run_kf_robot.py outputs/20261011T124056742603Z_P2_e310122b` 由record_run记录，run `20261011T124229474286Z_P2_502acaa3` exit0；固定原KF-GINS commit，无算法补丁。GPS week由bag确定2364，输出week列0是上游占位值。
- 正确B1身份的离线评价 run `20261011T124632852515Z_P2_fa4e1b07` exit0；10Hz12009点覆盖100%，水平RMSE3.845226m、P95 6.959384m、最大19.117123m，垂向RMSE8.199717m。初版输出误标B2，保留原run；本报告与后继评价修正为目标矩阵B1（B2应为FAST-LIO）。数值、轨迹未改。
- B0原始F9P于1200个1Hz观测历元：天线参考点水平RMSE3.301377m；B1于同GNSS时刻的ADIS参考点水平RMSE3.820899m。B0参考天线由离线reference姿态变换；没有把F9P插值成10Hz真值。参考点不同，不能直接把这两项解读为融合收益。

评价属于已知初态、初始位置条件化误差；地理原点未知，未拟合全轨迹。不宣称无先验启动、绝对WGS84精度或方法改进。参考MM/INS与主线共享AT128信息，需保留依赖限制。

强基线状态仍未成立：需要KF-GINS参数敏感性、真实FAST-LIO缓存、统一对齐/时延、同传感器B3–B6。Noetic rootless构建正在真实下载依赖；无sudo/宿主软件安装。parking00性能关闭，候选预算0/3。

轻量证据 `artifacts/robot_baselines/`；原始轨迹、逐历元误差、日志、配置与SHA在对应outputs。下一步完成隔离FAST-LIO构建与真实building00运行。
