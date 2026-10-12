# LIO-GINS S10：中等幅度持续 GNSS 偏差的历史锚点机制验证与短论文重构任务书

> **交给 Codex 的执行文档｜2026-10-12｜中文｜版本 v1.0**  
> **总体目标：** 基于已有 R1 → R2 → S8 → S9 全部证据，围绕“GNSS 失锁恢复后叠加 3 m 持续位置偏差”形成一个范围窄、机制清楚、有真实对照的研究故事，完成可交导师审阅的英文六页稿。先证明已有局部收益到底来自什么，再决定论文能作多强的主张。**不重启无边界调参，不根据结果挑路线或删失败。**

## 0. Codex 首先要理解的任务

这不是“把所有场景的指标改好”，也不是“替 R1 的 `NO_ADDITIONAL_GAIN` 翻案”。我们要在现有结果中辨认一个**较小但真实、可解释、可验证的收益机制**：

1. **实际问题：** GNSS 失锁后可能带着持续性位置偏差返回。对很大的偏差，普通创新门控（NIS）已经可能足够；对中等幅度偏差，门控可能仍放行。只看短窗口 GNSS 与 LIO 的相对运动，一段稳定的偏差也可能因为差分相消而不易被发现。
2. **已有思路：** P-r03 在同一位置 KF 外增加历史原始 GNSS/LIO 对应锚点；断点后按 LIO 相对运动外推锚点，比较返回 GNSS。锚点**仅做接入决策**，不是额外独立位置观测；不修改 FAST-LIO2，不引入真值到在线估计器。
3. **已有局部结果：** `loss30_bias3` 中，`building00`、`parking00`、`street00` 的 P 都比完全同结构的 `P_without_anchor` 低，但其他路线效果中性或恶化。`street00` 上 P 同时优于已测试的严格 NIS、各固定资格策略，且正常精度和正常接入时限合格。
4. **证据缺口：** 为什么有用？为什么另一些事件无效？3 m 注入到底有没有因为抵消原接收机误差而“碰巧”改善？是否可从不使用真值的历史锚点质量与 LIO 健康证据解释？这些必须回答。事后发现 3 m 局部优势，不能写作原实验的预注册主结果。
5. **目标论文：** 最终稿以一个具体的恢复偏差问题为中心，图像/事件证据与强基线相互支持，结论范围明确，保留全部负例。做到“给老师看、可讨论是否投稿”的完整程度。

**工作原则：先核查事实 → 后做只读机制分析 → 如有必要做有边界补充 → 再重写论文。不要倒过来先写胜利摘要。**

## 1. 仓库身份、分支与保护边界

- 仓库：`https://github.com/zhoumy0313/lio-gins`。
- 唯一的工作基线：`research/lio-gins-s9-multiscenario`，本任务书核查到的提交 `4f7a4b4c5b87040d7d7307f25a06cd785b1ff7b9`。执行时先 `fetch` 并确认该分支是否出现新提交，若有先阅读变更再决定基线；不要盲目将旧 SHA 当作最新状态。
- 历史链：`research/lio-gins-r1` → `research/lio-gins-r2-submission` → `research/lio-gins-s8-building01` → `research/lio-gins-s9-multiscenario`。旧报告和不利结果必须完整继承。
- 先执行 `git status --short`、`git branch -avv`、`git log -5 --oneline`、`python3 experiments/s9/health.py`（该 health 仅为工程参考；出错应核对既有诊断，不可冒充科学失败）。对未提交的改动绝对不要 reset、clean、stash 或覆盖。
- **新建独立的本地工作分支**，建议名 `research/lio-gins-s10-moderate-bias-paper`；不要修改旧四分支的冻结源码、配置、结果或论文。
- 原始 bag、F9P、IMU、reference、完整 `outputs_*`、cache 都按只读对待；新分析放新目录，新 run 使用独立时间戳，不覆盖旧目录。
- 新分支可以先本地提交；**推送新的远程分支需要明确用户授权**，不可把旧分支授权自动扩展成新分支授权。不执行 CMT 登录、署名、付费、版权确认或正式投稿。
- 不为这个任务修改宿主 ROS、GPU 驱动、全局 Python、网络代理或旧 VPR 项目；不下载未知第三方程序。优先复用已运行完成的本机结果，不重新跑整个 FAST-LIO2 前端。
- 原始已冻结 `P` 参数和 19 个方法配置保持不变。**本任务默认不开发新 r04，不做新的参数网格搜索。** 只有证据发现明确 bug，才能另起工程修复任务，保留修复前后研究身份，不把修复输出伪装成原始盲测。

建议新增并只在 S10 分支使用：

```text
docs/research_s10/
  STATUS.md
  CLAIMS_AND_LIMITS.md
  EVIDENCE_MATRIX.md
  MECHANISM_DIAGNOSIS.md
  INJECTION_BIAS3_AUDIT.md
  STRONG_BASELINE_CHECK.md
  PAPER_STORY_ZH.md
  AUTHOR_REVIEW_CHECKLIST.md
experiments/s10/
  build_evidence_matrix.py
  audit_bias3_injection.py
  diagnose_admission.py
  make_case_figures.py
  check_numbers.py
  tests/
artifacts/s10/
  evidence_matrix.csv
  event_attribution.csv
  injection_bias3_audit.csv
  admission_diagnosis.csv
  figures/
  manifest.json
paper/submission_candidate/s10/
  main.tex
  references.bib
  figures/
  main.pdf
  editorial_notes.md
```

如现有结构对论文版本有额外规则，应延续 `paper/versions/` 的只增不改风格；目录可以适当调整，但核心可交付物不能缺失。

## 2. 研究故事与假设：先固定口径，再分析

### 2.1 暂定题目

首选：**Historical-Anchor-Assisted GNSS Reacquisition under Moderate Persistent Position Bias**。

备选：**When Can Historical Motion Anchors Improve GNSS Re-entry? An Event-Level Evaluation of Moderate Position Bias**。

“Moderate”在本文**具体指向已有受控注入幅值 3 m**，不能擅自泛化为全部 1–5 m、真实城市多路径或自然硬件故障。`loss30_bias3` 是真实 F9P 数据上的**人为叠加偏差**，不是自然记录到的 3 m 故障。

### 2.2 需要回答的研究问题（RQ）

- **RQ1 — 判别盲区：** 对恢复后持续 3 m 的注入偏差，短窗口运动检查和严格 NIS 分别会接受哪些受扰 GNSS？历史锚点实际额外拒绝哪些观测？相应的定位误差改变了多少？
- **RQ2 — 机制归因：** `P` 与 `P_without_anchor` 除是否启用历史锚点外是否确实同配置/同数据/同初态/同后端？决定差异的关键接入时刻、锚点分数、年龄、健康状态和滤波修正在哪里？两者是否有一致且可定位的事件级差异？
- **RQ3 — 服务代价：** 在原先已经声明的正常精度约束和清洁 GNSS 重新接入 `≤15 s` 的条件下，与严格 NIS、Huber、Clock2/5/10/15/30/60/90 相比，在哪些**具体路线/事件**下 P 仍占优？不能将不符合服务要求的 60/90 s 策略从原始比较中删除。
- **RQ4 — 失效边界：** 为什么 `building01` 收益近零，而 `playground00`、`building02` 退化甚至造成清洁接入严重推迟？能否用**运行前可知、在线可计算**的锚点/运动健康信息提出一个可检验的适用条件？如果只有真值才能说明，应明确只能得到离线解释。

### 2.3 现阶段的假设层级

- **H1（已观察，待完整复核）：** 在 `street00/loss30_bias3`，P 的 90 s 事件宏 RMSE 低于同结构无锚消融、严格 NIS、已测试的固定时长资格控制；正常路线与清洁接入条件合格。
- **H2（机制假设）：** 短窗口差分会弱化窗口内近似常值的位置偏差，跨间断历史锚点在部分事件保留了可区分信息；额外拒绝与误差改善存在事件级对应关系。
- **H3（待检验解释）：** 当历史锚点或 LIO 相对运动不可靠时，锚点否决可能延误有用的 GNSS 接入，导致正常和受扰场景的退化。

严格分开三种状态：`observed_descriptive_gain`、`mechanism_evidence_supported`、`independent_confirmatory_gain_supported`。不能因为完成脚本或论文 PDF 就将其都置为 true。

**科学时序必须明确：** 原始 R1 / R2 / S9 的预登记主评估并不是专门针对这个 3 m 论文故事；S10 是在看过这些实验后形成的**事后细化 / 探索性假设**。不得把原 S9 `loss30_bias10` 主要结果回溯替换成所谓“事先选择的 3m 主要检验”。若新增未见数据，必须在打开新数据性能前登记新的 3m 假设、指标、对照与停止规则。

## 3. 已知事实：这些数值不必重新跑，但必须独立重算

统一统计量：每条路线 3 个固定事件各算**GNSS 重新出现后 90 s 水平 RMSE**，再对 3 个事件做等权平均（event macro），不是对整条轨迹做 RMSE，也不是合并三个事件样本后重新求 RMSE。

| 路线（数据角色） | `P_without_anchor` (m) | `P` (m) | P 相对无锚点的差异 | P 自然 RMSE / 上限 (m) | P 清洁接入最大延迟 | 边界 |
|---|---:|---:|---:|---:|---:|---|
| building00（已见开发） | 3.263 | 2.968 | 降低约 9.1% | 2.585 / 2.589 | 7 s | 同路线第二缓存只是敏感性检查 |
| parking00（已见回顾） | 3.087 | 2.297 | 降低约 25.6% | 2.362 / 2.412 | 7 s | 严格 NIS 有更低误差 |
| street00（S9 新路线） | 2.608 | 2.032 | 降低约 22.1% | 1.673 / 1.706 | 7 s | 强对照中 3m 的主要正例 |
| building01（S8 新路线，S9 前已见） | 1.868 | 1.868 | 基本持平 | 5.273 / 5.055 | 7 s | 自然精度不合格 |
| playground00（S9 新路线） | 5.401 | 6.597 | 恶化约 22.1% | 5.935 / 3.205 | 142 s | 自然与服务约束失败 |
| building02（S9 新路线） | 4.653 | 10.122 | 明显恶化 | 6.498 / 3.452 | 180 s 内有清洁事件未接入 | 自然与服务约束失败 |

上述均是已有归档的初步索引值；Codex 必须从 CSV/事件日志**独立重算到相同口径**并生成新的审计文件。计算 `improvement = (RMSE_no_anchor - RMSE_P) / RMSE_no_anchor`，所有原始未四舍五入数值都保留。

### 3.1 street00 的 `loss30_bias3`：论文候选核心事件

| 方法 | 3m 偏差 90 s 事件宏 RMSE (m) | 备注 |
|---|---:|---|
| 普通位置 KF (B3) | 2.766 | 不做偏差恢复接入保护 |
| Huber (B5) | 2.760 | 同位置 KF 鲁棒加权 |
| 严格 NIS11.3449 (NIS0) | 2.647 | 3m 注入时接纳 254/270 受扰行 |
| Clock2 | 2.608 | 与 P 共享短资格时间，但无历史锚点否决 |
| `P_without_anchor` | 2.608 | 主要归因消融；仅关闭历史锚点 |
| Clock60 | 2.325 | 清洁重新接入最大 65 s，原 15 s 预算下不合格 |
| Clock90 | 2.388 | 清洁重新接入最大 95 s，原 15 s 预算下不合格 |
| **P** | **2.032** | 自然精度 1.673 m；清洁重新接入最大 7 s |
| **`P_without_decay`** | **2.002** | 消融变体比 P 略好；不得声称 R 衰减必要 |

**不能漏掉的对照：** 同一 `street00` 上 `loss30_bias10`（10 m 注入）中，严格 NIS0 偏差宏 RMSE ≈2.387934 m，P ≈2.388016 m，二者基本相同；两者均拒绝全部 270 个受扰行。它是解释“中等幅度偏差为何更有研究价值”的重要**负/对照组**。

`street00/loss30_bias3` 的三次事件：

| 固定事件 | no-anchor (m) | P (m) | P 受扰接纳 /90 | P 首次受扰恢复后的真实接纳延迟 |
|---|---:|---:|---:|---:|
| Event 0，N | 2.388138 | 0.911555 | 12/90 | 25 s |
| Event 1，E | 1.694817 | 1.445671 | 7/90 | 7 s |
| Event 2，NE | 3.739729 | 3.739505 | 83/90 | 7 s |

**关键结论：** 两项事件改善，第三项几乎持平（差约 0.000225 m）。不能夸大成“三次显著提高”。尤其要避免把 Event 0 的主导改善误当作所有事件的稳定大幅增益。以上“受扰事件首次接入”和“失锁后正常无偏接入”是不同指标，绝不能混用。

**补充对照：** `building00/loss30_bias3` P 2.968 < no-anchor 3.263，但 Clock90 ≈2.509 更低，只是其清洁接入 95s 违反原服务预算；`parking00/loss30_bias3` P ≈2.297 < no-anchor ≈3.087，但严格 NIS0 ≈2.261 略低。不能把这两条写成“P 胜过一切”。

## 4. 现有文件与代码：先找到原始证据，不要重新造数据

### 4.1 汇总证据（Git 已包含）

- R2：`artifacts/r2/S3/summary_table.csv`、`artifacts/r2/S3/event_table.csv`；其中 `cache` 为 `primary`（building00 主缓存）、`sensitivity`（同路线第二缓存）、`parking`。
- S8：`artifacts/s8/C/summary_table.csv`、`artifacts/s8/C/event_table.csv`（building01）。
- S9：`artifacts/s9/C/summary_table.csv`，以及 `artifacts/s9/{street00,playground00,building02}/C/event_table.csv`、对应 `summary_table.csv`、`category_table.csv`。
- 科学协议：`configs/development_experiment_protocol.json`、`configs/s9/protocol.json`、`configs/s9/P.json`、`configs/s9/P_without_anchor.json`、`configs/s9/NIS0.json`、`configs/s9/Clock{2,5,10,15,30,60,90}.json`。
- 科研归因与限制：`docs/reports/P4/late_control_decision.md`、`docs/research_r2/EXPERIMENT_REPORT.md`、`docs/research_s8/EXPERIMENT_REPORT.md`、`docs/research_s9/EXPERIMENT_REPORT.md`、`docs/research_s9/PAPER_REVIEW.md`。
- 现有正式审阅稿：`paper/submission_candidate/s9/main.tex`、`generated_tables.tex`、`references.bib`、`main.pdf`。只用于继承，不直接覆盖。

### 4.2 逐历元/逐更新证据（本地未全部推送，需要找到保留的输出目录）

从各 `event_table.csv` 的 `backend_run` 字段找到该策略的不可变后端运行目录，再找：

```text
backend_run/trajectory.csv
backend_run/per_update.jsonl
backend_run/per_state.jsonl       # 部分方法提供
backend_run/backend_resolved.json
backend_run/backend_identity.json
```

必要时由 `artifacts/s9/<route>/technical_context.json`、`outputs_s9/`、`outputs_s8/`、`outputs_r2/` 既有 run 索引追溯：

```text
stress_run/event_manifest.json
stress_run/natural.csv
stress_run/loss30_bias3.csv
stress_run/loss30_bias10.csv
initialization_run/initial_condition.json
raw_reference/*_groundtruth.nav
```

注意旧 CSV 的绝对路径可能与当前 Codex 工作空间路径不同；必须先根据实际目录和 SHA 解析，**不可仅因为路径失效就假定原始证据不存在**。如果原始输出确实缺失，应在 `STATUS.md` 标为 `blocked_missing_raw_logs`，继续完成所有基于 Git 轻量结果可以做的部分，不能虚构事件曲线。

### 4.3 现有接入代码的关键字段

- `src/observation_manager/motion_recovery.py`：短窗口分数与状态机。
- `src/observation_manager/availability_recovery.py`：健康不足的成熟规则回退。
- `src/observation_manager/anchored_recovery.py`：历史锚点残差/分数/年龄、否决规则、晋升与冻结。
- `experiments/s9/street00/run_candidate.py`、`run_baseline.py`；R2、S8、另外两条 S9 路线对应脚本有相似结构。
- `per_update.jsonl` 已有或可能有：`original_gnss_id`、`measurement_sow`、`available_sow`、`accepted`、`nominal_nis`、`reason`、`motion_score`、`qualification_elapsed_s`、`motion_reason`、`local_health_verified`、`anchor_score`、`anchor_active`、`anchor_available`、`anchor_age_s`、`anchor_original_gnss_id_used`、`correction_norm_m`、`state`、`r_multiplier`。
- `experiments/s9/street00/reanalyse.py` 已实现固定 10Hz 全网格、各事件 10/30/60/90/180s 窗口、实际接纳与 180s 右删失；**应复用而非重新发明不一致指标**。
- `experiments/{r2,s9/street00}/injection_cancellation.py` 现有实现读取的是 `loss30_bias10.csv`；**它不能直接证明 3m 结果**。S10 需新建只读 3m 误差抵消诊断，不修改既有科学脚本、原件或 10m 审计。

## 5. 分阶段执行计划、操作及验收标准

### 阶段 A — 新分支、状态登记与数据追踪（优先立即完成）

**任务**

1. 安全检查工作树、最新提交、是否已有 S10 工作，防止重复执行；创建本地 S10 分支。
2. 从上述 6 条路线与 building00 第二缓存读取所有 `loss30_bias3`、`loss30_bias10`、`loss30_normal` 的完整逐事件表，固定方法名映射；明确 `NIS0=11.3448667301`、`NIS1=16.266236`、`NIS2=30.0`，`B4` 的较宽阈值不是“严格 NIS”。
3. 重算所有 3m 宏 RMSE、方法差异、自然成本、正常接入时间、每次事件受扰观测接纳数；建立 `evidence_matrix.csv` 和 `EVIDENCE_MATRIX.md`。
4. 建立 manifest：文件路径、Git SHA、数据 SHA、配置 SHA、run SHA、分析脚本 SHA、指标版本与事件身份。检查方法/缓存/初始化/参考一致，不允许只选运行成功的交集。
5. 若对账不一致，保留两套数字、展示源位置，先查修正原因，不能直接选有利数值。

**交付：** `docs/research_s10/STATUS.md`、`artifacts/s10/evidence_matrix.csv`、`artifacts/s10/manifest.json`；必要时新增只读 parser 单元测试。

**通过门槛：** 表中每个值能追到独立来源；`building00` 第二缓存没有被算作新路线；S9 三条新路线没有被删去；所有版本的 P/no-anchor 配置仅在锚点开关处不同的事实已核查。

### 阶段 B — 3m 人为偏差与真值误差抵消审计（必要）

**动机：** 旧 10m 审计已经发现有些人工扰动行反而降低原 GNSS 真实误差。3m 更容易受到这种效应影响，必须独立检查，不能仅把“接收的注入行数较少”当作真实更准确。

**任务**

1. 只读加载 `natural.csv`、`loss30_bias3.csv`、对应 `event_manifest.json`、受控单历元初始化与 groundtruth；沿用原 GNSS 原始行 ID、NED 坐标、天线杆臂和参考姿态约定，时间支持与已有评价器一致。
2. 对每条路线每个事件报告：未注入真实 GNSS 水平误差分布、注入后真实水平误差分布、注入反而减小实际误差的观测数、分方向误差、对齐样本数、可用性与参考独立性限制。
3. 与 `loss30_bias10` 做同口径对照，解释“3m 注入幅度”与“实际 3m 绝对误差”是两件事。
4. 对每种策略分别给出受扰观测接纳计数、被接纳观测的离线实际误差统计（明确是离线标签，不进入方法），区分被拒绝的观测是否真的更差。
5. 不用真值修正观测、权重、状态机或参数；本阶段只有离线解释。

**交付：** `artifacts/s10/injection_bias3_audit.csv`、对应每路线 JSON、`docs/research_s10/INJECTION_BIAS3_AUDIT.md`、一个可复用可审计的诊断脚本和输入 SHA。

**通过门槛：** 六路线 × 三事件结果完整，匹配原行 ID/时钟与不同参考来源；报告任何偏差抵消，不把“注入行接受率”称为真实故障检测率。

### 阶段 C — 逐事件机制诊断与最重要的解释图（核心任务）

**优先级 1：** `street00/loss30_bias3` 三事件。对照 `P`、`P_without_anchor`、严格 `NIS0`、`Clock2`、`Clock60/90`、`P_without_decay`；必要时列 B3/B5/B6。**优先级 2：** `building00`、`parking00` 的 3m 正例；**优先级 3：** `playground00`、`building02` 负例。

逐事件对齐下列量（必须按时间、GNSS 原始 ID、滤波器共享缓存配对）：

| 证据对象 | 需要解释的问题 |
|---|---|
| `nominal_nis` 与 NIS 阈值 | 为什么严格 NIS 接纳了这些 3m 受扰行？何时开始拒绝？ |
| `motion_score`、短窗可用性 | 常值偏差是否确实未造成明显的短窗矛盾？是否因为窗口缺失而成熟规则回退？ |
| `anchor_score`、`anchor_active`、`anchor_age_s` | 历史锚点在哪些时间触发否决？年龄/历史参考是否可能污染？ |
| `local_health_verified` 与健康判据 | 事件改善/恶化是否与 LIO 有效点数、平面残差、可用性有关？ |
| `accepted`、`state`、`motion_reason`、`reason` | 真实接入与隔离何时发生？是否属于锚点否决、普通 NIS、回退、恢复？ |
| `correction_norm_m`、`trajectory.csv` | 接纳后位置修正与真实定位误差变化能否在时序上对应？ |
| 原始 GNSS / 注入 GNSS / 离线参考 | 受扰 GNSS 在真实误差上是否更差？是否有偶然抵消？ |
| LIO 对应相对位移的离线误差 | 能否解释某些场景历史锚点外推偏离？不可作为在线判据。 |

**最低图表要求**

- **Fig-A：** 概念示意图：短窗口相对位移对近似常值位置偏差的盲区；历史锚点跨失锁段外推的约束。标明只有当前原始 GNSS 做一次 KF 更新。
- **Fig-B：** `street00/loss30_bias3` **全部三个固定事件**的 90s 误差 / 实际接入情况对照；不要只挑 Event 0。至少对 `P`、`P_without_anchor`、严格 NIS0、Clock90。可拆成主文一张图与补充完整图。
- **Fig-C：** 代表性机制轨迹：水平误差时间曲线 + P/NIS/锚点评分和阈值 + 接入/拒绝标记；只从真实既有日志生成。为确保可解释，选择规则必须在脚本中登记；优先同时给出固定顺序第一事件与至少一个负面事件。
- **Fig-D：** 六路线的 3m P–no-anchor 事件宏 RMSE 与正常成本/接入资格，明确展示 `building01` 中性和另外两条失败；不能只画三个正例。

**归因分析约束**

- P 与 no-anchor 才是“历史锚点是否有作用”的直接单因素对照；Clock2 是简化时间资格控制但要查状态实际差异；NIS、Huber、Clock60/90 是强基线，未必同结构单因素消融。
- 3m `street00`：Event 0 优势很大，Event 1 小幅优势，Event 2 约 0.000225m 基本无差异。必须用实测日志解释，不允许删去 Event 2、只报告 Event 0。
- `P_without_decay` 3m 宏 RMSE 比 P 略低；禁止将 R 衰减写作本次必需创新。
- 10m `street00` 严格 NIS 几乎与 P 持平；不能把它说成“传统门控在持续偏差下全面失败”。
- 不能从最终 RMSE 反推“锚点错误”是唯一原因；没有足够日志时写 `unresolved`。

**交付：** `docs/research_s10/MECHANISM_DIAGNOSIS.md`、`artifacts/s10/admission_diagnosis.csv`、`artifacts/s10/event_attribution.csv`、`artifacts/s10/figures/`（优先 PDF/SVG/PNG + source points CSV + 文件哈希）。每张图明确来自哪个 route/case/event/method/run。

### 阶段 D — 强基线公平性与可重复性审查

1. 建立一张**不会筛掉对手**的表：`P`、no-anchor、B3/B4/B5/B6、3种严格 NIS、Clock2/5/10/15/30/60/90、no-decay、纯 LIO。可把所有19策略放补充表，主文只保留与主张相关的关键行，但整表和全部不利结果仍随稿可查。
2. 对 `loss30_bias3` 同时展示：事件宏RMSE、每个事件RMSE、正常整程RMSE、已有自然成本上限、正常 GNSS 首次真实接入延迟、3m受扰观测接受数、覆盖、删失、90/180s 扩展窗。
3. 原有服务预算是 `clean T_admit≤15s`（测量时钟），同时独立展示 `available_sow` 缓存可用时钟的保守上界；都不是现场端到端真实延迟。原正常成本约束取 B4/B5/B6 最佳自然 RMSE 加 `max(2%,0.05m)`，保留原定义，不为 P 重新设门槛。
4. `Clock90` 不是无条件 90s 拒绝：局部健康不可用时存在成熟策略回退，必须报告真实每事件接入时间。
5. `street00` 3m 的亮点是“在已测试的标准固定策略和严格 NIS 中 P 最低，且满足清洁服务/正常成本”；但去掉 R 衰减的消融仍略优，必须在结果中说明。
6. 3m 仅是 S10 事后识别的候选论文故事；此前 R1/R2/S9 的原注册负面科学结论不能删除或改写。
7. 不把每个 GNSS 观测或每个窗口当 IID 独立样本求漂亮的 p 值；三次事件相关，同一 bag 的前端敏感性缓存不是独立路线。优先报告效果幅值、逐事件符号、预先可追溯的路线集合和明确限制。

**交付：** `docs/research_s10/STRONG_BASELINE_CHECK.md`；有一个程序可自动拒绝“主文数字与结果表不一致”“缺少负路线”“混淆原注册和事后分析”等错误。

### 阶段 E — 是否要做新的实验：有限决策树

**默认首选：先用已有完整结果和日志完成 A–D。** 若得到完整、可解释的机制证据，即可先进入导师审阅稿；不要因为论文更好看就反复搜索参数。

允许的新增研究方向，严格按从低风险到高风险排序：

**E1. 只读机制分析（推荐）**：从现有 3m/10m 所有既有事件重建 NIS、锚点和误差的时间关系；不用运行原生前端；不形成新的独立验证主张。

**E2. 受控偏差幅度敏感性（可选，只有具备时间且已登记完整网格时）**：若要检验 3m 是否只是碰巧最优，在同一已见路线用固定幅度集合，例如 `{0,1,2,3,4,5,6,8,10}` m（这是建议，不是既有实验）。**先**写定协议、所有幅度/方向/时间位置/策略/结果口径和运行预算，再批量执行缓存后端，不按中途结果删幅度或微调 P；全部公开。结果属于 **seen-data sensitivity**，不能作为独立测试、也不能为方法重新优化阈值。若时间不足直接跳过。

**E3. 真正独立验证（最有力，但不作为本轮完成导师稿的阻塞）**：若现有 i2Nav 数据集还有从未查看该方法定位性能、具备完整传感器和参考的路线，须在首次访问性能之前登记**3m 专题假设**、冻结路线选择、事件、方向、幅度、估计器、强对照、指标与结果判定，并留下可核验的提交/输入 SHA；之后一次性运行所有预设场景。不可把已经打开的六条旧路线重新称作新留出。若无法取得，明确记为 `independent_validation_not_available`。

**E4. 机制修订（默认不允许）**：如果最终证据表明当前机制被强 NIS 或长等待完全解释，优先收敛论文为窄范围分析；禁止未经新协议的新 r04/参数搜索。任何可能实现的新门控/健康适应策略都应作为**下一篇 / 下一阶段独立研究**，不是赶本轮截止日期的补丁。

### 阶段 F — 六页英文导师审阅论文重写

把现有 S9 作为事实来源，而不是照抄它的多场景大叙事。**只有 B–D 证据通过后，才锁定正文主张并写“提高多少”**。

推荐结构（IEEE 会议模板，六页含参考文献）：

| 章节 | 约页数 | 写什么 |
|---|---:|---|
| I. Introduction | 0.8 | GNSS 失锁恢复与中等持续偏差具体问题；瞬时创新、短窗差分盲区；本文轻量历史锚点；三条真实贡献 |
| II. Related Work | 0.5 | 鲁棒 GNSS 门控/失锁接入、LIO辅助、相邻 WinTA-GIL 与 Dual-ACKF；不声称已有内容首次提出 |
| III. Method | 1.1 | 公用 3D 位置 KF 最少公式、5 s 短窗、历史锚点判别、接入状态机；只更新原 GNSS 一次 |
| IV. Experiments | 1.0 | i2Nav 六路线角色（开发/已见/后续新路线）、3m/10m 人工扰动、固定 3 次事件、19策略含别名、自然/时效约束与已有参考限制 |
| V. Results & Discussion | 2.0 | 3m 核心局部收益与强基线、NIS vs 锚点机制图、3m/10m 差异、其他路线反例、合理适用边界 |
| VI. Conclusion / References | 0.6 | 一条有限结论、已知失败、下一步验证；参考文献 |

**贡献写法（待证据通过后，可使用这一层级）：**

1. 一种**已有实现、被重新聚焦分析**的历史 GNSS/LIO 锚点辅助恢复接入机制，不与已有滤波器重复融合历史测量。
2. 针对 GNSS 恢复后中等幅度持续偏差的事件级评估，结合误差、NIS/锚点决策、正常场景代价和清洁接入时限比较强基线。
3. 在部分数据和事件上定量显示轻量锚点的收益，并完整讨论因锚点/运动不可靠导致的拒绝时延或精度退化。**不要写成全部路线成功的可推广正定理。**

**论文标题/摘要的判定条件：**

- A–D 如果支持 street00 这一狭义故事但没有新独立确认：标题可用 `Historical-Anchor-Assisted GNSS Reacquisition under Moderate Persistent Position Bias: An Event-Level Case Study`；摘要明确属于已完成多路线实验的**post-hoc focused analysis**，不要叫“pre-registered moderate-bias primary evaluation”。
- 如果新增未见数据 E3 确认某个明确资格子类：标题可调整为 `... under [verified condition]`，但必须有事先固定的条件和所有结果。
- 如果 3m 注入误差抵消或机制不支持该主张：回退成方法局限与恢复策略比较的实验稿，不编写虚假“可靠改进”。

**最重要的图表优先级：** (a) 常值偏差与历史锚点结构示意；(b) street00 三次 3m 事件的 P/no-anchor/NIS/Clock 方法结果；(c) GNSS/anchor 状态与误差时间线；(d) 六路线正负结果汇总与合格标志。不要让“456 runs / 1197 events / SHA / freeze”占据摘要和结果主要段落，这些放 Reproducibility/补充证据索引即可。

**文献工作：** 复核 FAST-LIO2、i2Nav-Robot、KF-GINS、WinTA-GIL、Dual-ACKF 的原始来源及与本实现的差异；适当补上 GNSS 重新接入、鲁棒门控、失锁漂移及 GNSS/LIO 故障恢复最相关文献。不能把未运行的论文精度写成同条件 SOTA 对照；不复现不明公式；参考总量不要机械凑数。

**人工审核：** 作者姓名、排序、单位、基金、原创性/授权及真实 AI 使用披露留给人；新导师版可去掉 S9 PDF 显眼的红色内部状态横幅，但不要将 `formal_submission_ready` 置 true。会议官网目前全文截止 2026-10-15，英文 6 页 PDF，具体时区/匿名与模板变体还需作者核实。完成的是**导师审阅稿**，不是 CMT 正式提交。

## 6. 结果状态判定：不要模糊地报告“论文完成”

每阶段须在 `docs/research_s10/STATUS.md` 单独给出：

```text
execution_complete: true/false
source_data_traced: true/false
bias3_cancellation_audited: true/false
event_mechanism_explained: true/false
P_vs_no_anchor_local_gain_supported: true/false
P_vs_strong_controls_in_declared_scope_supported: true/false
independent_confirmatory_gain_supported: true/false
novelty_supported: true/false
full_six_page_review_draft_ready: true/false
human_author_review_complete: true/false
formal_submission_ready: true/false
```

**允许的科学结论强度：**

- **Level A（优先争取）：** 明确的狭义条件、事件级机制可定位、P 对同结构无锚点和已测试强基线的指标改善成立，且相关路线自然成本与服务要求合格；清楚标为探索性发现，若另有独立验证再提出确认性结论。
- **Level B：** 狭义局部收益有，但机制原因/独立重复尚不充分，或只有一些路线合格；写成事件级案例研究 + 方法限制，保留负例。
- **Level C：** 3m 注入存在明显误差抵消、前端/参考口径不能核对，或强基线复核推翻主要优势；不得发布“新方法性能提高”论断，转为诚实的实证分析或者请人决定是否转短摘要。

不能用重设 15s 时限、自然成本上限、只留好方向、只挑最佳幅度、升级获胜消融为正式算法等方式“修复”科学证据。若出现这些建议，直接停止并向用户报告替代方案。

## 7. 最小测试清单与质量门槛

- 所有新 Python 工具至少包含：路径/来源身份检查、必要输入列验证、数值有限性、缺测、事件计数、时钟对齐、输出去重、不覆盖老文件、错误中止可恢复；只做离线后处理。
- 数据行身份：`original_gnss_id` 每策略唯一，时间单调，严格区分 `measurement_sow` 与 `available_sow`，不能以“请求时间”冒充真正 `accepted=true` 更新时间。
- 指标单位：RMSE 水平 N/E；每事件固定 `post90` 10Hz 完整网格、三事件等权宏平均；右删失 `C180` 不填 180 当作实测延迟；`P95`、最大值、180s 扩展窗不冒充主要 RMSE。
- 注入行：对齐 `natural.csv` 与受扰 CSV 的相同原 GNSS ID，确认删除/偏差窗口边界、各事件 90 个受扰行；不是“接入越少就一定越准”。
- R2/S9 估计器源码和 frozen 参数的哈希不因 S10 分析改变；`P_without_anchor` 只关闭锚点，NIS/Clock 角色严格核对。
- P/no-anchor 在已有自然场景一致的地方必须复核完全相同指标。10m 中严格 NIS 与 P 接近、building02 3m 退化等反例均须出现在 `CLAIMS_AND_LIMITS.md`。
- 旧自动单元测试可复用 `python3 -m unittest discover -s tests -v`（实际依赖/运行环境先核对）；S10 新统计脚本加单元测试，验证事件宏平均、百分比、别名映射、删失和正常精度资格判断。不要在缺环境时伪造 pass。
- 每个论文数字/图点可追溯到 source CSV 或实际运行日志，输出 manifest/绑定索引，不能从写稿文字反向生成“实验数据”。
- LaTeX：论文不超过 6 页（含参考文献）；编译日志没有 unresolved references/overfull box，所有页人工或工具逐页检查，图中文字在最终缩放尺寸下可读；完整保留 TeX/Bib/矢量图/编译脚本与 PDF。
- 结论、摘要、标题、图表全篇统一；新方法名称没有暗示本文首次提出既有 NIS/窗口一致性/渐进 R 恢复；参考轨迹与前端可能共享感知信息、受控单个参考初始状态、前端重复运行 3.601m RMS 差异、人工偏差和缓存时间不是实时延迟等限制在适当位置保留。

## 8. 执行顺序与停止点（考虑 10 月 15 日截稿）

**今日优先级**

1. **A** 对账现有 3m 事件与全六路线，原始日志路径与 SHA 成功追踪。
2. **B** 3m 受扰 GNSS 真实误差抵消审计。
3. **C** 至少先完成 street00 三事件与严格 NIS/Clock/无锚消融的真实逐时诊断。
4. **D** 统一验证自然成本/服务资格和所有反例。
5. 机制成立则开展 **F** 论文重写；必要情况下 **E1** 作为补证。E2、E3 可排到导师审阅以后，除非已有现成数据且时间允许。

**停止规则：** 不得因为某个新事件不利就更换事件位置/方向、调整阈值或更改讨论故事。三次预设事件、六条路线和全部原注册强对照必须保留；若关键机制未被日志证实，只能降级结论，不能无限运行寻找正例。论文正文撰写与诊断可以并行组织，但最终结论需要待证据核验。

## 9. Codex 每次回复与最终交付

**先输出工作计划和当前真实状态，再开始执行。** 每完成一个阶段汇报四件事：

1. **做了什么**：实际命令、退出码、耗时及输出路径（失败也记录）；
2. **有何发现**：支持/不支持的具体指标或机制事实，明确是旧数据回顾还是新数据确认；
3. **是否满足阶段门槛**：列出证据文件、身份哈希、错误/缺失；
4. **下一步**：只推进尚未完成的阶段，避免重复跑已封存的前端/矩阵。

最终交付包至少包含：

- `docs/research_s10/PAPER_STORY_ZH.md`：一页中文故事（问题、已有方法弱点、历史锚点机制、正例、最强反例、贡献与限制）；
- `docs/research_s10/EVIDENCE_MATRIX.md`、`MECHANISM_DIAGNOSIS.md`、`INJECTION_BIAS3_AUDIT.md`、`STRONG_BASELINE_CHECK.md`：所有数字都有 run/文件身份；
- 三类关键图 + 数据点 CSV + 生成脚本 + SHA（方法示意、有效事件机制、跨路线正负/服务代价）；
- `paper/submission_candidate/s10/main.tex`、`main.pdf`、Bib 和所有图文件：导师审阅用六页英文论文；
- `docs/research_s10/CLAIMS_AND_LIMITS.md`：可以说什么、不可以说什么、哪些还未被证实；
- `docs/research_s10/STATUS.md` 和 `AUTHOR_REVIEW_CHECKLIST.md`：科学状态、导师/作者需要确认的信息、稿件和 Git 提交索引。

**最终回答必须用一句明确结论收束：** “在不改变已有冻结算法与参数的前提下，3m 窄范围故事是否具有经强基线和机制日志支持的真实收益；若成立，支持到什么条件/路线/实验层级；若不成立，主要阻碍是什么。”

---

## 10. 供 Codex 开始执行的首轮指令

> 请把本文件视为这轮工作的完整任务规范。首先检查 Git HEAD、工作树、原始结果和本机只读输入是否在位，然后执行阶段 A、B、C，不要先重写摘要，不要首先新增算法或调参数。A–C 完成后给出可审计的中间结果，再根据是否满足门槛推进 D、F。尽量自动完成一切不需外部权限的工作，缺数据/权限集中到一份清单。不要修改旧冻结实验、推送未授权新分支、直接投稿或声称已获得独立确认。
