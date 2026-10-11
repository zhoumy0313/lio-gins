# LIO-GINS-R1 最终交付

**科研结论：NO_ADDITIONAL_GAIN。** 环境、官方demo、数据、真实前端/KF-GINS及匹配强控制先完成；候选3轮/36主配置保留。原开发门槛成立并科学冻结后开启parking00完整矩阵。后补长等待强控制在两个开发缓存都优于P，正常代价合格，因此新增运动锚机制优势未成立。原注册停车场9.9549%差异保留为窄集合事实。没有r04、主指标切换、停车场重调或投稿全文。

## 接口与成果

- [README](../README.md)：源checkout环境重建步骤、原始数据RO接入、锁定源码、真实全前端和缓存后端入口及限制。完整clean-clone链未作为新测试重跑；实际组件、完整停车场组合及本机归档恢复已验证。
- [科学最终决策](reports/P4/late_control_decision.md)、[完整冻结测试](reports/P5_frozen_heldout.md)、[主张边界](CLAIMS_SUPPORTED.md)、[方法说明](METHOD_SPEC.md)、[最近邻机制表](RELATED_WORK_MATRIX.md)。
- 原数据16件保留，bag SHA与官方一致；独立分支和固定源码/子模块，补丁分build/logging/plumbing/research。原初始10文件通过身份核验；旧VPR等未修改。
- 全部exclusive outputs/缓存/失败/注册表/科学冻结与论文历史版本保留。freeze源码b6259cf，归档2274156；P5 checkpoint8604050，P6 checkpointfbba11c；P7归档提交见Git日志和RESUME（避免自引用SHA）。
- `paper/working` 和 `paper/versions/internal_results_r01`：内部英文方法/实验/结果局限及80对claim map；先前草稿版本未改。`artifacts/final_figures`是实际Matplotlib图、点CSV及输入/输出SHA。
- [2–3页内作者中文解释](AUTHOR_BRIEF_ZH.md)、[10个事实问答](DEFENSE_QA_ZH.md)、[恢复入口](RESUME.md)、[逐项验收](COMPLETION_AUDIT.md)。

## 真正执行及验证

| 阶段/命令 | 真实退出码 | 核心证据 |
|---|---:|---|
| P0环境与原工作包保护 | 0；Docker/Podman探测127保留 | reports/P0.md，初始工作包SHA |
| P1原生KF-GINS demo/健康检查 | 0（首次严格参考检查失败保留） | reports/P1.md；10Hz RMSE0.012209m，仅官方demo |
| P1完整数据审计/隔离Noetic构建 | 0/0 | 数据审计112420385892；构建130509928405，原生binarySHA固定 |
| P2完整building00前端/缓存 | 0/0；EOF缺native计时的首run保留 | 完整12440位姿/计时；两个缓存3D差异3.601m未解释 |
| P3 `complete_development_controls.py` | 0 | 141054205503，112对、全部coverage1，统一正常代价预算 |
| P4 3轮screen、固定消融/双缓存、80对迁移 | 最终0；失败和诊断保留 | r01/r02/r03及final_verification/route_transition报告，36主配置 |
| P4 `freeze_development.py` | 0 | 154403074900，科学freeze15:44:03 UTC，首次访问15:44:46 UTC |
| P5 `run_heldout.py` | 0 | 154446522435，80对/210事件，完整前端12238帧；无重调 |
| 后补开发 `audit_long_wait_control.py` | 0 | 161516459969，64对；90s目标2.285876/2.024895m优于P2.373985/2.198809m |
| P6 `plot_final_reports.py` | 0 | 163107886415，两图及完整点CSV/SHA；内部草稿版本 |
| P7 `replay_frozen_backend.py` B6/P natural | 0/0 | 163106760681/163820527256，轨迹及更新日志字节一致、指标相同 |
| P7 `unittest discover -s tests -v` | 0 | 164802218803，64项，19.8249s；完整详细日志与合成fixture保留 |
| P7 `audit_final_metrics.py` | 0 | 164106339470，80对原始轨迹/原参考直接重算，最大差8.882e-16m；输入及冻结文件身份通过 |

所有缩写run可在RUN_REGISTER.csv找全ID；精确argv/cwd/起止/exit在对应outputs与轻量receipt。合成fixture中的故意失败不当作真实算法成功，所有日志原样保存。最终全归档完整性及resume实际结果登记在COMPLETION_AUDIT/GOAL_STATE。

## 不能从交付推导的结论

原有限对照改善不证明超过合理长时间策略，当前positive_effect/independent_effect/novelty/paper_ready=false。原生B1停车场76.5613m是转移配置失败，不作为主要增益分母。参考共享LiDAR，初态只用一个参考状态；非绝对WGS84/无先验部署。人工压力不是现场多路径。native处理时延和缓存时延不是完整现场端到端时延。

无标志数值LIO重置会传播错误跳变；缺失跨度明确FAILED/coverage不足。相同bag前端数值重复性未解决；clean-clone完整再构建未执行、Docker方案未验证。它们是明确工程边界，不包装为已解决。

无必需人工输入；见USER_ACTION_REQUIRED。原数据只有本地一份，异地raw/numeric备份未验证，SHA不是备份。没有授权remote/对外发布；仅本地checkpoint。没有旧VPR修改、sudo/宿主ROS/Python/网络/驱动变更、账号、署名、付费或正式投稿。新的研究或出版动作需要另定范围，本轮不自动延长探索。
