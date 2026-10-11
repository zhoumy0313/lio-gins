# LIO-GINS-R1 — 当前状态

2026-10-11，Asia/Shanghai。P0 已完成；P1 无阻塞任务已完成，真实数据和容器运行时仍缺。完整目标未完成。

- KF-GINS 固定源码原生编译、官方 demo 和独立健康检查 exit0；672923 行，10 Hz 覆盖100%，水平RMSE 0.01220946 m。仅为官方demo。
- 最新共同接口合成测试16项通过，exit0。源码/原工作包/已封存实验完整性通过。没有真实i2Nav基线精度或候选收益。
- 已固定三个指定上游与必要消息依赖，核实Noetic官方manifest digest，准备Dockerfile、独立日志补丁和受限运行入口；Docker构建检查BLOCKED/127。
- 10个预定building00/parking00文件均MISSING。数据元数据审计exit2；公开下载已按限额停止，不进行账号操作。
- P2/P3未运行，P4预算0/3，P5留出未打开，P6未写投稿稿。execution_complete/positive_effect_supported/novelty_supported/paper_ready全部false。

详情：[P1报告](reports/P1.md)、[统一人工清单](USER_ACTION_REQUIRED.md)、[运行索引](RUN_REGISTER.csv)、[状态JSON](GOAL_STATE.json)。

数据/运行时具备后执行：`.venv/bin/python scripts/resume.py`，然后按目标P2完成时间、标定、初始化和两条真实基线。旧VPR与系统设置未改；仅本地checkpoint，无remote和异地备份。没有后台运行中的实验。
