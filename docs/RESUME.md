# 断点恢复

日期：2026-10-11。P0 checkpoint `7dd6292`；最新归档checkpoint以 `git log -1` 为准，报告在 `docs/reports/P1.md`。尚无科学冻结SHA或候选方法结果。

读取 `AGENTS.md`、完整目标、`docs/GOAL_STATE.json`、`CURRENT_STATUS.md`、`RUN_REGISTER.csv`、Git及进程。当前无运行中实验。已封存输出禁止改写；若有进程，读取其process.json/PID/日志而不重复启动。

当前输入需求只见 `docs/USER_ACTION_REQUIRED.md`。data/raw和data/reference均无实际机器人文件；Docker/Podman未安装。不得sudo、操作账号或触碰旧VPR。不得复用官方demo的IMU/噪声/初态作为机器人配置。

单条下一步命令（在本工作空间）：

```bash
.venv/bin/python scripts/resume.py
```

该命令只做恢复读取和真实文件元数据审计，文件缺失时exit2/BLOCKED，新run保留。已有数据通过身份检查后，按目标继续P2的隔离构建、bag时间/点格式、IMU增量交叉检查、共同合法初态与两真实基线。最新准备好的ROS上下文为 `outputs/20261011T052215556145Z_P1_a2b55b2f/container_context`，包含独立消息生成依赖构建补丁，未实际build；旧上下文保留。

最近demo run `20261011T050704118893Z_P1_533dad03`；独立健康run `20261011T051218350449Z_P1_8d97e56b`；最新测试run `20261011T051219512804Z_P1_8272e056`。所有数值来自官方demo/合成，禁止写成机器人数据增益。

P3真实强基线前不探索P4；开发收益和消融/文献/正常代价门槛通过并freeze后才开启P5留出性能。当前六个科研就绪/增益字段均false，候选预算0/3。P6/P7的完整稿件与最终交付不能跳过证据门槛；当前只有部分恢复交付。
