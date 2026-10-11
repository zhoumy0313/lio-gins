# LIO-GINS-R1 当前状态

2026-10-11 15:20 UTC。P0–P3完成；P4已完成r01–r03共36个主配置，正在最后的固定参数消融和双缓存复核。当前无必需人工操作，parking00性能仍关闭。

r01因正常代价被全部淘汰；r02恢复正常代价但收益0.067067m/2.1811%未过门槛。r03单缓存目标宏RMSE2.373985m，相对B6 3.074919m改善22.7952%，自然2.584657m在统一cap内，coverage100%。该结果尚未验证重复或归因，科学状态false。全七类事件、自然路线和接入失败保留，不增加新机制/调参。

当前真实进程：最终验证driver `outputs/20261011T151637778113Z_P4_bc2078b6`，读stdout/progress和实际进程，不重复启动。55项完整检查exit0；前一个目录输入预检exit127保留。

P1 16原件与两个官方bag SHA通过，官方KF-GINS demo/隔离Noetic构建通过；无sudo或全局改动。P2完整building00 1×前端exit0、12440/12443位姿和原生计时，均值17.3215ms/P95 22.7675ms；两次相同输入局部轨迹差异RMS3.60m未解决，不宣称数值重复。P3 112个匹配基线/场景组合全exit0/100%覆盖，B1原生STD×2 RMSE3.702869m。

共同初始化读首参考历元并平移到共同局部原点，结果不是无先验启动或绝对WGS84准确度。参考MM/INS共享AT128。缓存后端计时不含前端。原始数据只有本地一份；SHA不是异地备份。仅本地checkpoint，无新remote、署名或投稿。

证据入口：docs/reports/P2_full_frontend.md、docs/reports/BASELINE_REPORT.md、docs/reports/P4/r01.md/r02.md/r03.md、GOAL_STATE.json、RUN_REGISTER.csv。方法与实验草稿为内部版本，不是投稿稿。最终验证全部门槛通过才考虑P5，否则留出继续关闭并交付真实受限结论。
