# 断点恢复

2026-10-11。当前P4 r01执行中，完整目标仍未完成。以 `git log -1`、`GOAL_STATE.json`、`RUN_REGISTER.csv` 和实际进程为准。

单条恢复检查命令：

```bash
.venv/bin/python scripts/resume.py
```

该命令读取状态、Git、实际项目进程及最后收据；有进程时exit3，禁止重复启动。不会重复读取75GiB原数据或开启性能。`--audit-data` 可显式重新校验数据。

- 原始16个文件在data/i2nav-dataset，bag SHA与固定官方值匹配；只读保留。
- 官方KF-GINS demo通过，真实B1有限噪声筛选通过，选择STD×2，水平RMSE3.702869m。两者不混为同一实验。
- Noetic/FAST-LIO由现有Bubblewrap用户命名空间运行，派生环境run `20261011T130509928405Z_P1_4c5d376c`；无sudo或宿主ROS/Python/网络配置改动。
- 首个全程1×frontend run `20261011T131528442554Z_P2_9d0fac69` launcher exit0、12440位姿；EOF时钟停住造成SIGTERM，最终原生计时缺失。完整位姿缓存run `20261011T134125698776Z_P2_0de7714e`明确timing_complete=false。
- 新1×frontend `20261011T134909303110Z_P2_626b9771`已exit0、EOF正常关闭并输出完整native计时。顺序驱动已完成：34项检查和112组强基线/场景组合均exit0。相同输入前端3D RMS差异3.60m，来源未证实，最终候选需固定参数在两个保留缓存复核。r01 driver 20261011T143431646773Z_P4_01709632正在执行12主配置，读stdout/progress和进程，不重复启动。
- 所有sealed outputs/rootfs不可改写，失败不得删除。当前候选修订1/3，parking00性能关闭，P4先等P3真实证据。
- 当前无必需人工操作，见USER_ACTION_REQUIRED。没有项目remote授权，仅本地checkpoint；原始数据及数值未验证异地备份。

后继动作：等r01封存读取candidate_screen.json及正常代价/逐事件结果，写决策卡；按实际失败原因只改一个机制执行r02/r03。开发增益、归因、文献及冻结门槛全部满足才开P5。无增益分支交内部方法/实验草稿和真实否定结论，留出关闭，不自动生产投稿稿。
