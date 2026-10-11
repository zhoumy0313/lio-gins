# LIO-GINS-R1 逐项验收

**已完成本轮有界目标与负结果条件分支交付，科研分类NO_ADDITIONAL_GAIN。** 每项要求的证据及限制列在下表；不宣称正科学结果、干净机器重建通过、投稿或录用。

| 要求 | 状态 | 证据与实际边界 |
|---|---|---|
|P0/P1保护及环境/demo|complete|docs/reports/P0.md; docs/reports/P1.md; docs/reports/P1_rootless_environment.md；原10件身份及上游清洁由最终integrity审计；不等同算法精度|
|最小数据与身份|complete|data/manifests/DATA_MANIFEST.json; docs/reports/P1_data_received.md；16原件全SHA，两个bag官方匹配，仅本地一份|
|真实前端/原生基线与协议|complete_with_limits|docs/reports/P2_full_frontend.md; P2_initial_native_baseline.md；两条真实路线，明确单历元受控初始化；3.601m前端变化未解决|
|P3匹配强控制/共同代价|complete|docs/reports/BASELINE_REPORT.md；112配置场景对、Q/R/前端/初态共用，B6非完整DualACKF|
|P4有界机制/决策卡|complete|docs/reports/P4/r01.md; r02.md; r03.md; final_verification.md；最多3轮36主配置、淘汰/失败保留|
|科学冻结先于第一次测试|complete|freezes/LIO_GINS_R1_20261011T154403129394Z; docs/TEST_OPENED.json；当时原注册门槛全通过；后补反证时序真实披露，不倒改历史|
|P5完整矩阵及实际计时|complete_with_limits|docs/reports/P5_frozen_heldout.md；80对/210事件coverage1；native/frontend/backend分开；全部失败和消融保留|
|长等待强控制充分挑战|complete_negative|docs/reports/P4/late_control_decision.md；一轮4时长64对，仅开发且在测试访问后，60/90s优于P；不再搜索|
|P6论文条件分支|complete_conditional_internal_only|paper/versions/internal_results_r01; docs/reports/P6_internal_drafts.md；GOAL§17.3没证据交方法实验草稿，不交6页投稿全文/PDF|
|作者简报及十问|complete|docs/AUTHOR_BRIEF_ZH.md; docs/DEFENSE_QA_ZH.md；事实对应公式/范围/失败，无作者或正式投稿|
|干净checkout起点README|documented_with_limits|README.md；包含固定来源/项目umoci/新run路径捕获/全路线命令；完整clean-clone重建链未独立重跑，不宣称通过|
|一键full与cached及归档恢复|complete_with_limits|scripts/run_development.py; scripts/run_heldout.py; scripts/replay_frozen_backend.py；building组件/parking全组合已执行，B6/P缓存natural精确；不是新盲测或异地备份|
|13.1时间/IMU/坐标/杆臂/nav格式|checked|tests/test_common_interfaces.py; tests/test_candidate_rotation.py; tests/test_final_contracts.py; bag/text audit receipts；周边界/异常保留/单轴NED/quat/纯旋转，bag/text样本证据范围不夸全量|
|13.1排序/ID/hash拒复用|checked_with_explicit_contract|tests/test_final_contracts.py；乱序原入口拒绝；新开发copy稳定排序后同输出；ID重排数值不变，ID日志及byteSHA应变；cache改动拒绝|
|13.2零噪声/Joseph/R/disabled/一次更新|checked|tests/test_common_interfaces.py; test_final_contracts.py；闭式均值协方差及PSD、所有10种策略无GNSS传播一致、r03无管理精确B6|
|13.2未来/真值/标签隔离|checked|tests/test_causal_lio.py; test_anchored_recovery.py; test_final_contracts.py；未来删除不改过去、endpoint可用时间、外置未来标签无影响、标签输入拒绝、在线import图无评价器|
|13.2断点/健康/偏差/漂移/转弯/静止/reset|checked_with_limits|tests/test_motion_recovery.py; test_availability_recovery.py; test_anchored_recovery.py; test_final_contracts.py；断点/锚不洗白/UNRESOLVED/观测等价；r03纯转/静止；无标志数值reset不崩但错跳未解决，gap明确失败|
|13.3指标/真值独立重算/覆盖/公平|checked|outputs/20261011T164106339470Z_P7_269b03f9/final_metric_audit.json; tests/test_outer_evaluation.py；80对直接原轨迹/参考重算，最大8.882e-16m；同cache/init/输入/冻结配置，gap保留NaN/failed非dropna|
|13.3图表数字与SHA|checked|paper/working/claim_evidence_map.json; artifacts/final_figures/figure_identity.json；80对trajectory/update/config/gnss/cache/init binding，两图与所有点CSV SHA|
|独立状态旗标|complete|docs/GOAL_STATE.json; docs/CLAIMS_SUPPORTED.md；宽科学效益false，原窄注册差异true；execution与novelty/paper分开|
|原件/失败/版本保存与边界|complete_with_limits|docs/RUN_REGISTER.csv; docs/STATE_HISTORY.jsonl; artifacts/run_receipts; paper/versions；不覆盖/不删除/no remote/no旧VPR；SHA不是备份|
|最终全归档完整性与恢复入口|checked|outputs/20261011T164941656901Z_P7_24971931/stdout.log; outputs/20261011T165419513326Z_P7_6280e88b/delivery_audit.json; artifacts/delivery_checks/resume_pre_checkpoint.json；全归档1334run/379359files/10初始件，无失败；resume0无活跃实验；交付一致性审计全通过。文档快照对应审计前版本，之后仅完成状态索引收束|

交付审计run 20261011T165419513326Z_P7_6280e88b exit0；最终integrity 20261011T164941656901Z_P7_24971931 exit0；resume exit0。64项测试和80对原始重算不能替代上表明确的范围。README完整clean-clone链未独立重跑、前端数值变化、无标志reset及异地备份仍为公开限制，并未伪装为解决。

关闭状态再次核验：20261011T165650509097Z_P7_b6ca698e exit0，明确检查最终状态旗标分离及无pending条件项；源码冻结仍不变。
