# LIO-GINS-R1 当前状态

2026-10-11。完整目标未完成，当前P3强基线筛选中。当前无必需人工操作。

- P0保护独立空间完成；原用户工作包及旧VPR不变，仅本地checkpoint。
- P1官方KF-GINS demo通过，16原始文件齐备、两个bag SHA匹配；Noetic/FAST-LIO在已有Bubblewrap用户命名空间中编译运行，无sudo/宿主ROS/Python/网络变更。
- P2 building00 B1原生噪声STD×0.5/1/2均100%覆盖；预登记选择×2水平RMSE3.702869m。共同首参考历元初始化，未知地理原点，结果称初始位置条件化误差。
- P2完整1×FAST-LIO回放正常关闭exit0，1286.7126s，12440/12443位姿与12440原生计时；均值17.3215ms、P95 22.7675ms，不含输入回调/发布/等待。缓存、时间/位姿行对应和34项接口/因果/离线评价检查exit0。
- **前端数值敏感性尚未解决**：相同输入/二进制两轨迹局部3D差异RMS3.60m、最大9.79m，去掉初始坐标差异后仍存在。脚本执行成功不是数值稳定。最终候选及选中强基线必须在两缓存固定参数复核；当前不得科学冻结。
- P3 run `20261011T141054205503Z_P3_e03a0b15`执行预登记Q四档、NIS/Huber各四档、固定恢复十二档；完整结果待封存。原生前端已结束，没有并行重前端。
- 候选修订0/3，parking00性能仍关闭；execution_complete、positive_effect_supported、novelty_supported、paper_ready分别false。setup_r01是内部实验设置草稿，无投稿结论。

证据：docs/reports/P2_full_frontend.md、GOAL_STATE.json、RUN_REGISTER.csv、USER_ACTION_REQUIRED.md。旧缺数据/环境阻塞报告是历史，按此页和真实进程恢复；不重复启动。
