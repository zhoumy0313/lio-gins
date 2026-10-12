# LIO-GINS · S8 — building01 前瞻性验证与 UPINLBS 2026 投稿交付

> **执行目标**：基于已完成的 R2，利用用户新提供的 `building01` 官方原始数据开展一次事先冻结的跨路线验证；客观判断是否能支撑一个**范围明确的 GNSS 失锁/恢复观测接入方法或实证研究**，并在 2026-10-14 前准备完整、人工可审阅的 6 页以内会议 PDF。实验质量与可追溯性优先于“必须出现改善”。
>
> **目标代号**：`LIO-GINS-S8-BUILDING01`; **创建日期**：2026-10-12，Asia/Shanghai。
>
> **历史基点**：`zhoumy0313/lio-gins` 的 `research/lio-gins-r2-submission`，起始 HEAD `8ef95ce597433a8b45c90ec1d13eb57ec4355555`。检查当前远端是否更新，有更新先审阅再确定基点；R1 分支 `research/lio-gins-r1` 的 `c12a42a3484458e1737e63201792e1122fc99c0d` 不得改动。

## 0. 总指令与授权范围

你是执行代理 Codex。完整阅读 `AGENTS.md`、`docs/GOAL_LIO_GINS_R2_SUBMISSION.md`、`docs/research_r2/STATE.json`、`docs/research_r2/PROTOCOL_FREEZE.md`、`docs/research_r2/REPRODUCE.md`、`docs/research_r2/EXPERIMENT_REPORT.md`、`docs/research_r2/PAPER_REVIEW.md`，再执行本文件。

1. 先审计 Git、现有活动进程、历史 sealed runs、现有数据和用户新文件。**不得覆盖、删除或篡改 R1/R2 冻结、论文版本、失败运行、原始数据**。旧项目 VPR 不涉及。
2. 从 R2 最新干净提交建立**新工作分支** `research/lio-gins-s8-building01`。此项任务明确授权在已存在的 `zhoumy0313/lio-gins` 仓库推送**该新分支的源码、轻量结果、冻结记录与论文版本**；不推送原始数据、全量缓存、密钥或任何未经许可的资料；不 force push。
3. 不调整已完成 R1/R2 的 P-r03、B2–B6、固定时钟、严格 NIS 和参考评价定义；不修改原始测量，**不根据 building01 的结果选参数/删除事件/重定义目标**。
4. 先解决新路线的数据/时钟/坐标/前端接口，建立**新路线的完整科学冻结**并提交推送。在首次独立定位误差、与方法优劣相关的数据被读取或展示之前，必须有成功的远端 `git ls-remote` SHA 核验。已有 `freezes/r2/analysis_*/analysis_freeze.json` 明确属于 `ANALYSIS_FREEZE_ONLY`，**不能冒用为独立测试授权**。
5. 普通代码/脚本、非 sudo 隔离环境、日志、固定对照、科学图表和论文迭代自主完成。需 sudo、账号/验证码、付费、扩大仓库可见性、署名、基金确认、版权协议、正式 CMT 提交等一律由用户决定。
6. 不因为“独立测试完成”就自动标记 `new_method_increment=true`、`paper_ready=true`。分别跟踪 `data_verified`, `freeze_pushed`, `heldout_opened`, `independent_effect_supported`, `novelty_supported`, `review_pdf_ready`, `formal_submission_ready`。
7. 若独立实验与 P 假说不符，仍须完成真实报告及限定贡献的完整论文稿，但**不得伪造或放大正向效果**。作者可以选择有限应用/实证研究投稿，接受风险由作者和导师决定。

## 1. 输入、路径与初始命令

以 `/home/aaron/lio_gins` 为项目根目录。用户称数据已准备，**尚不等于已经在项目期望路径且通过校验**。期待只读原件：

```text
data/i2nav-dataset/building01/
  building01.bag
  building01_ADIS16465_IMU.txt
  building01_F9P_GNSS.pos
  building01_groundtruth.nav
  building01_trajectory.csv
```

原目录不同可使用相对清晰、可追踪的只读链接或修改专用路径配置，避免复制整个数十 GB 的 bag。逐个检查 `is_file`、字节数、真实格式、单调/重复时间、非有限数据、坐标/量纲、文本行数与首末时间、交集、参考可用率。**官方 `building01.bag` SHA-256**：

`60931a01bbc0eb05154e895349be24212cb43b6c795c4c91cbb801c7db73b257`

该 SHA 来自 `i2Nav-WHU/i2Nav-Robot/sha256sum/sha256sum.json`；官方未发布相应文本 SHA，则只登记本地文本 SHA，不假装官方已认证。对 bag 执行流式哈希与 ROS1 bag-v2 magic 校验。保留额外辅助文件，不强求视频、深度或不相关观测。

最早执行以下**只读**检查；若实际脚本接口不同，以 `--help` 和源码为准，不猜运行参数：

```bash
cd /home/aaron/lio_gins
git status --short
git branch --show-current
ls -lh data/i2nav-dataset/building01/
sha256sum data/i2nav-dataset/building01/building01.bag
python3 experiments/r2/record_run.py --stage S8 --purpose building01_presence_audit --input experiments/r2/audit_new_data.py --timeout 120 -- python3 experiments/r2/audit_new_data.py
```

**不要依赖 `scripts/resume.py --audit-data` 检查 building01**：当前它调用的 R1 `scripts/audit_data.py` 只循环 building00/parking00。现有 `experiments/r2/audit_new_data.py` 只审核**是否存在/文件大小**，不足以证明已验证实际内容。请在新分支新增/扩展新路线专用身份与元数据审计，不回写旧 manifest 造成其 SHA 变化。

## 2. 可复用的固定基础

- 宿主 Ubuntu 22.04，FAST-LIO2 在**已经实测成功的 Bubblewrap/rootless Ubuntu20.04+ROS Noetic**隔离环境运行；**不要重装操作系统，也不要为这项任务重新部署 Docker**。
- FAST-LIO2 使用固定 i2Nav AT128/ADIS16465 适配，点云 `/hesai/at128/points`、IMU `/adi/adis16465/imu`；旧代码/编译环境中独立的 build/logging 兼容补丁如实记载。
- 原始 ADIS `.txt` 已为角增量(rad) / 速度增量(m/s)，不要再次乘 dt；F9P `.pos` 经纬度(deg)、高程(m)、标准差(m)。GNSS观测仅一次 Kalman 更新；缓存的差分/锚只作观测接纳判断。
- 官方参考为 ADIS 中心 local NED；building01 属于室内外、GNSS available、MM/INS 参考。参考构建用到 AT128 地图匹配，非所有传感器均独立。单个首参考状态用于既定受控初态，其余仅供评价；不宣称无真值初始定位或绝对 WGS84。
- 对照保留相同 LIO 轨迹、外层 3D 位置 KF、Q/R、杆臂、初始化、事件和期待网格：P-r03、B2/B3/B4/B5/B6、Clock2/5/10/15/30/60/90、NIS11.3449/16.2662/30 以及已登记必要消融。别把重复的 P-time-only/Clock2 计为额外独立算法。
- `building00`/`parking00` 全部是**已见数据**；R1 `parking00` 冻结记录不能变为 R2/S8 新独立测试。`building01` 只能打开一次预先封存的完整测试矩阵。

## 3. 阶段 A — building01 数据与技术可行性审计（不打开定位性能）

目标交付：`docs/research_s8/DATA_AUDIT.md` 与 `artifacts/s8/data_manifest.json`，同时记录来源及源 SHA。

**检查点**：

- 5 个必需原件均真实存在，bag SHA 与官方一致（若不一致，明确阻塞，不能自动修“预期哈希”）。
- 使用隔离 Noetic `rosbag info` 检查类型/消息率、点云逐点时间、传感器 IMU、GNSS 与原始文本；记录经纬高度和时间转换的合法性。
- **从新 bag 与文本独立确认 GPS week、UTC/GPS 关系和 SOW**；不得默认沿用 building00/parking00 的 week=2364，亦不可把 KF-GINS 输出的周号占位符当真实时标。
- 通过 `/data`/单文件只读挂载；不访问整个 home、私有文件夹或 Docker socket；隔离宿主 ROS2 环境，保留前端每帧有效点数、残差、可用时刻等诊断。
- 在看性能前仅审计 GNSS 实际测量覆盖、原始参考时间跨度、必要事件的前后共同时间范围、数据质量和初始位姿是否可用。`building01` GNSS available 只是数据集属性，**不保证固定 150/450/750s 事件全具备闭合窗口**。
- 审计输入起点、事件及完整 10/30/60/90/180s 后验窗口是否落在真实可用数据支持内；无效事件和时间跨度必须用已登记规则处理，不根据方法误差选择。
- 使用现有成功隔离环境做一次**无真值比较**的 FAST-LIO 完整回放及 LIO 缓存校验；前端要求覆盖、时钟递增、消息种类与输出量正确。不凭误差挑缓存。必要时第二次前端回放作预先固定的复现敏感性检查。

若缺文件或时间/格式无法适配：写 `docs/research_s8/USER_ACTION_REQUIRED.md`，精确列出仍需用户提供的项和示例输出；其它可独立完成的任务继续执行；不得以虚构轨迹或旧路线改名替代。

## 4. 阶段 B — 新路线适配与**前瞻冻结**

**技术障碍已知**：`experiments/r2/run_seen_baseline.py` 和 `run_seen_candidate.py` 直接拒绝 `building01`；`freeze_analysis.py` 明确写入 `new_heldout_opening_authorized=false`，且其 `ANALYSIS_FREEZE_ONLY` 是旧路线归档。**绝不能直接替换 building00/parking00 路径、关闭 role 校验或将旧布尔字段直接翻为 true 来绕过保护。**

在 `experiments/s8/` 新增最小、可单元测试的**新路线角色隔离入口、科学冻结生成/校验、真实 run 控制器、最终报告生成器**。优先复用 R2 的同一核心公式和 19 组配置，而不是复制修改新机制。只允许纯接口/兼容性修复，需证明旧 building00/parking00 运行结果及所有策略校验与之前一致。

冻结输入包括：`building01` 五原件 SHA、数据 schema/时间与 GPS week、传感器/杆臂/校准、前端 build/binary/配置/缓存身份、用于唯一初始化的首参考行规则、角色/访问边界、所有 baseline/候选/消融配置、7 类事件生成规则与固定时刻/方向、主场景(clean30/bias10)、后 90/180s 等窗与采样频率、评价 RMSE/覆盖/删失/真实接入时钟、服务预算 15s（包括 5/10/30/60/90s 敏感性）、自然整程代价、科学声明边界、相关源码和测试 SHA。

在首次计算 `building01` 的定位误差/各策略优劣前：

1. 生成 `freezes/s8/building01_<timestamp>/scientific_freeze.json` 和校验和，保存 source/config/data 身份。
2. Git 提交**完整冻结**，推送 `research/lio-gins-s8-building01`，对比 `git ls-remote` 精确 SHA，持久化 `FREEZE_PUSH_RECEIPT.json`。
3. 只有核验成功才解除 S8 独立测试访问；后续任何源码/参数变化不得冒充原始盲测。若之后发现纯技术故障，可保留错误和更正收据并对整组方法公平重跑、标记非首次测试；**不得因为结果不佳而修改方法/指标**。

## 5. 阶段 C — building01 一次性完整独立矩阵

用同一个 building01 FAST-LIO 缓存、同一个初始化、相同 GNSS 输入和脚本定义运行**完整固定策略×全部 8 类实验条件**，包含全部 7 类预设受控 GNSS 扰动加 natural。原生 KF-GINS 基线有时间则用相同输入和既定冻结配置独立运行；其配置失配失败如实披露，不作收益基准。

主要检验**事先定义的有限问题**：

- `loss30_normal` 的**首次真实 `accepted=true` GNSS 更新时间**（非状态切换或错误恢复时间）：清洁回归的 `t_admit-t_return ≤15s`，同时展示按缓存可用时间计的保守上界，并明确都不代表现场 wall-clock 端到端时延。
- `loss30_bias10` 的注入偏差回归后 90s 水平 RMSE（所有 3 个固定时刻和 N/E/NE 方向的**等权事件宏平均**），再展示 10/30/60/180s 窗与全部事件单项结果。
- 90s 内接受了多少注入行以及实际对应的离线位置误差；受控偏差叠加真实 F9P，有可能抵消原有误差，不能把被接受的注入行等价成真实错误检测率。
- 自然整程 RMSE 与预定自然代价门槛、clean90 定位误差、P95/Max、输出覆盖/失败/删失。不得只展示最优事件/成功交集。
- 完整简单控制：包括固定较长等待(如 Clock60/90)与严格 NIS(尤其NIS30)；即使它们违背 15s预算，也要展示原始误差与成本。不能选择一个明显较差的 baseline 作为分母。
- 所有结果同缓存配对比较；对已有未解 3.601m 前端重放差异披露。若加做第二次 building01 前端回放，预先登记、同样的方法/参数全部重放；不得挑较好的 LIO 输出当主要数字。

**正向证据判断**：如果 P 在新路线的预定 clean 15s、自然代价和覆盖要求内，与全部有资格的固定强控制相比，其 `bias90` 主要 RMSE **有实际且可归因的改善**，并有对应消融/事件证据，则支持一个**场景限定、非普适的新路线改善主张**；大小无需很大，但必须不是舍入噪声、隐藏代价或单个挑选事件导致。若 P 仅对部分事件有改善，报告完整分布，只允许更窄、由前瞻事件类型事先定义的结论。不能把已见数据的 43.6% 降低搬成新路线效果。

若不成立：如实写“独立路线未重复该改善”，保留所有数值和完整六页稿，确定是否转换为**实证对照/失败边界论文**；由作者和导师决定是否投稿。禁止再次把 building01 当开发集调参却仍称它是第一次独立验证。

结果目录建议：`outputs_s8/<unique_run_id>/`（原始封存）和 `artifacts/s8/`（轻量图表/报告）。产出逐事件 `event_results.csv/json`、完整配置索引、主表、跨路线对照、参考/输入 SHA、完整真实日志、独立重算抽查和缺失记录。子执行退出码、源 SHA、资源计时和可恢复机制按 R1/R2 规范。

## 6. 阶段 D — 论文六页内投稿版本

以 `paper/submission_candidate/r2/main.tex` 为原始参照**复制新版本**到 `paper/versions/s8_r01/`，不得覆盖 r2_r03 或旧 PDF。再根据真实新路线结果生成最终候选 `paper/submission_candidate/s8/`。保留可编译 TeX、BibTeX、SVG/TikZ/矢量图、配置/输入/实验 SHA、分页/字体审计和完整论文 PDF。

投稿故事统一为：“GNSS 恢复是否应立即接入？短等待易接入偏差、长等待延迟有效修正。本文在统一 LIO 预测 + 接收机 GNSS 位置更新条件下，评估利用局部运动和历史参考约束的观测接入机制，报告**在指定时效与自然代价条件下**的误差折中。”不能把 FAST-LIO2/KF-GINS 已有实现改写成原创算法。应突出研究问题、信息流、差异机制、强基线与全类事件结果。

若 building01 支持场景限定贡献：标题/摘要聚焦**独立路线验证的具体改善**，不说普遍优越、新的 21D ESKF、实际多路径识别或毫秒级现场实时性。至少有一张跨路线主表：building00开发、parking00既有回顾性、building01新独立；区分 seen 与 held-out。把特别不利的 NIS30/Clock90 和 no-decay 消融纳入主表或醒目正文。

若 building01 不支持：论文仍是完整可审阅 PDF，但不得悄悄删掉独立负结果；修订主张为“恢复策略的条件性经验分析”，可附面向作者的 Full Paper vs 1–2 页 Abstract-only 的不同证据与传播价值建议，**不等同于两种投稿均会被录用**。

**必要的人类审核事项**：

- 确认截至 2026-10-15 的**精确时刻与时区**、IEEE会议模板的具体变体/页面边距、投稿匿名要求、AI 使用政策与 CMT 表单实际要求；`IEEEtran[conference]` 的成功编译不代表会方已确认其是最终模板。
- 6 页上限（保守地计入参考文献/披露）；移除内部红色 NOT_SUBMISSION_READY 标记**只能在作者审核并满足实际提交条件后**。未确认匿名性前，不要擅自添加作者/单位/公开仓库链接；AI 生成代码与文字披露应依实际适用规则。
- 作者排序/所属单位/基金资助/合作署名、学术原创性、非一稿多投、必要授权与版权，由人最终核定，不代替作者作决定。
- 候选 PDF 应交付“作者审阅版”和独立 `SUBMISSION_CHECKLIST.md`；**不擅自登录或点击 CMT Submit**。

原定 2026-10-15 Full Paper 截止；时间紧迫时按如下优先级：**今天** 完成真实数据核验和冻结；**明天** 完成唯一独立矩阵及科学结论；**10 月 14 日** 完成人工可审阅 PDF、引用/模板/截止时区核实及导师审核，留出最终投稿操作的时间。真实截止时区未核实前不能假定北京时间 10 月 15 日午夜。

## 7. 阶段 E — 验收、断点恢复与交付

新增 `docs/research_s8/STATE.json`、`RUN_REGISTER.csv`、`PROTOCOL_FREEZE.md`、`EXPERIMENT_REPORT.md`、`CLAIM_EVIDENCE_MAP.json`、`PAPER_REVIEW.md`、`USER_ACTION_REQUIRED.md`、`AUTHOR_BRIEF_ZH.md`、`SUBMISSION_CHECKLIST.md`。完成并提交每阶段 checkpoint，推送新分支并核验 SHA。保存旧实验/失败、原始时钟、代码差异、所有方法/事件（含失败）、绘图数据及引用。

终态严格分离以下状态：

```json
{
  "data_verified": false,
  "science_freeze_pushed_before_test": false,
  "new_route_test_executed": false,
  "independent_case_specific_effect_supported": false,
  "novelty_supported": false,
  "full_review_pdf_ready": false,
  "formal_submission_ready": false,
  "formal_submission_performed": false
}
```

上述均为初始化字段，**真实执行后由证据驱动更新**，不得以“计划阶段已完成”自动设置为 true。最终报告用一页中文告诉作者：实验到底证明了什么、最强对照具体是多少、哪些事件失败、跨路线是否成立、投稿需要人决定的事项和精确 PDF/TeX 路径。

## 8. 已核实的外部来源与论文入口

- i2Nav-Robot 官方数据：<https://github.com/i2Nav-WHU/i2Nav-Robot>
- i2Nav 官方原始 bag 校验：<https://github.com/i2Nav-WHU/i2Nav-Robot/blob/main/sha256sum/sha256sum.json>
- i2Nav 基线源：<https://github.com/i2Nav-WHU/i2Nav-Robot-Baseline>
- KF-GINS 官方源：<https://github.com/i2Nav-WHU/KF-GINS>
- UPINLBS 2026：<https://upinlbs2026.com/>；官网列出 **Full Paper deadline October 15, 2026**，最多6页；具体时区及匿名规则仍需在正式投稿界面进一步核实。
- CMT：<https://cmt3.research.microsoft.com/UPINLBS2026>（授权由人处理）。

**停止条件**：不因新路线显示不理想就不断重新启动候选搜索或重写论文为“无条件优越”；不因代码跑完就承诺可录用。任务最终成功是：新路线资料完整核验、一次独立评价真实可追踪、完整六页可审阅 PDF、所有负例与强对照真实披露，并将最后的投稿判断交给人类作者。
