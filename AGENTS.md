# LIO-GINS 工作空间规则

## 当前目标

先读 `docs/GOAL_LIO_GINS_S8_BUILDING01_SUBMISSION.md`、`docs/research_s8/STATE.json`，并保留 R2 协议。
当前完整目标是 `LIO-GINS-S8-BUILDING01`，按 A→E 执行；R1固定于c12a42a，全部旧源码/实验/草稿和NO_ADDITIONAL_GAIN保持不变。当前项目不是旧VPR的新版本。
主线：LIO 相对运动传播 + 接收机 GNSS 位置更新 + 运动验证的观测恢复管理；KF-GINS 为独立 GNSS/INS 对照。

## 自动执行

按 S8 目标文档 A→E 自主推进；创建真实状态文件并保留历史。遇到缺少数据、权限或账号，执行其余不受阻任务，集中写入一次性 `docs/research_s8/USER_ACTION_REQUIRED.md`（根清单仅作S8入口）。
不要虚构 Goal 注册命令。当前客户端可以读文档并执行任务即可；上下文中断后读状态、Git、进程与日志恢复。

## 修改边界

- 仅在用户指定的新工作空间中修改；保留已有未提交更改，不触碰旧 VPR、SSH、FlClash、驱动与全局 ROS/Python。
- 上游固定 commit；适配补丁、日志补丁、研究机制分开；不冒充原始算法作者。
- 原始数据只读。新 run 不覆盖；旧论文版本、失败及日志不删除。
- 没有这个项目的已授权 remote 就仅本地提交，不新建公共仓库、不复用旧 VPR remote。
- sudo/权限扩张、系统网络/驱动变更、账号操作、付费、删除原数据和正式投稿要先获授权。

## 研究与输出

- 先完整固定等待2/5/10/15/30/60/90和NIS/Huber强对照，R2最多一次有证据的局部修订、最多8配置。
- building00/parking00均已见；新路线优先building01，方法/服务/评价/输入冻结提交后才开独立测试；不无限搜索。
- 无论结论如何都交完整≤6页英文源稿/可审阅PDF/图表/证据映射/投稿检查单；没有增量则实证案例稿，不虚构正向贡献。论文自S0与实验同步推进。
- 用户已授权zhoumy0313/lio-gins的R2分支，每阶段checkpoint并推送，先检查敏感内容与体积，禁止force/push旧R1分支。
- 真值仅用于明确的初始化协议/离线评价；不进入在线可信度或更新权重。
- 每条 GNSS 只更新一次；差分作监测，不重复当独立量测；不高频注入 KF-GINS 后验。
- 论文可以按机制组织为框架，但实现必须注明 FAST-LIO2/KF-GINS；小幅改进不保证录用。
- `execution_complete`、`positive_effect_supported`、`novelty_supported`、`paper_ready` 分别登记。
- 所有图表数字追到 run/config/input SHA；人工扰动、自然数据、缓存重放、真实在线计时分开。

## 每阶段回报

给出完成项、真实命令/退出码、关键结果、失败或阻塞、证据路径和下一步。不要只回“已完成”。

## S8 补充

新分支 research/lio-gins-s8-building01 已获授权推送，每阶段 checkpoint；R1/R2 分支不推送。P-r03 和19个固定策略不得更改。完整科学冻结成功推送且 ls-remote SHA 精确相同后才打开 building01 方法与精度；不使用 R2 ANALYSIS_FREEZE_ONLY 替代。仅一次完整矩阵，完整保留负结果。
