# LIO-GINS Codex 工作包

这是研究计划与执行约束，不含已经实现的定位算法或实验结果。

## 放置位置

把本包文件复制到新 Ubuntu 工作空间根目录：

```text
你的新空间/
├── AGENTS.md
├── START_HERE.md
├── .gitignore.recommended
├── configs/
└── docs/
    └── GOAL_LIO_GINS_R1.md
```

如已有同名文件，先合并/保留旧版本，不直接覆盖。`.gitignore.recommended` 是建议内容，由 Codex 与现有 `.gitignore` 合并。

主文档也可单独放进 `docs/` 使用；其余文件只帮助代理维持任务边界与证据组织。

## 给 Codex 的启动指令

> 读取 `AGENTS.md` 和 `docs/GOAL_LIO_GINS_R1.md`，以 `LIO-GINS-R1` 为目标按 P0→P7 自主推进。先完成环境、官方 demo、数据与基线，再做有界方法探索；开发证据成立后才冻结并打开留出结果。保留全部实验和论文版本，每阶段提交 checkpoint。缺少的数据/权限集中列成一次性清单，继续能做的任务。不要修改旧 VPR 工作空间，不执行署名、付费或正式投稿。

## 用户需要提供的内容

首批为 building00 原始 bag、ADIS IMU、F9P GNSS、参考轨迹文本；另备 parking00 同类文件作为留出数据。公开入口和完整文件清单已写在目标文档。

若代理需要，补充原始 local NED 参考地理原点与初始化信息。无需重装 Ubuntu，无需机器人外带采集，无需把整个 i2Nav 数据集下载下来。

本科论文可放 `docs/reference/`，只作结构参考；包含个人资料，不默认推公共仓库。

## 重要方案选择

主线不叠加 FAST-LIO2 和 KF-GINS 的两个高频后验。它使用 LIO+接收机 GNSS 的轻量全球更新；KF-GINS 作为 GNSS/INS 对照。

研究增量落在“可疑观测隔离—运动验证—渐进恢复”，而不是软件名称或一个新缩写。主文档包含最新相近工作与文献差异要求。

## 本包文件

- `docs/GOAL_LIO_GINS_R1.md`：完整目标、数据、数学接口、阶段、实验、权限、归档、论文叙事。
- `AGENTS.md`：工作空间级代理规则。
- `configs/project_intent.yaml`：计划意图，不是已完成实验配置。
- `configs/sources.lock.json`：已核查的上游提交；本地 clone/build 仍待执行。
- `docs/templates/`：阶段报告、请求用户输入、论文主张证据模板。

所有实施进度以在用户 Ubuntu 上实际执行的结果为准。
