# P4 最终开发验证：通过，待路线入口一致性后冻结

真实命令：`.venv/bin/python scripts/record_run.py --phase P4 --purpose final_r03_fixed_parameter_ablations_and_two_frontend_cache_verification --timeout 2400 [inputs recorded] -- .venv/bin/python scripts/verify_final_candidate.py outputs/20261011T150927930407Z_P4_1dace17d`。
Driver20261011T151637778113Z_P4_bc2078b6 exit0，722.284495s。32主缓存消融组合、72敏感性缓存强控制/候选/消融组合，共104个新的独立backend/evaluation对完成，全部100%覆盖；复用既有P3和r03主缓存结果。没有新增主配置或机制调参。

| 同参数缓存 | B6目标宏RMSE | P目标宏RMSE | 改善 | 自然B6/P |
|---|---:|---:|---:|---:|
| 主缓存 | 3.074919 | 2.373985 | 0.700935m / 22.7952% | 2.586890 / 2.584657 |
| 敏感性缓存 | 2.893789 | 2.198809 | 0.694980m / 24.0163% | 2.070218 / 2.070369 |

两个缓存的最小改善0.694980m超过改善差0.005955m，二者均满足>=3%且>=0.1m、自然RMSE≤共同cap2.589027m、覆盖≥99%。这是同路线两次前端数值敏感性检查，没有独立路线统计意义，也未消除前端原始轨迹RMS3.60m变化问题。

无运动消融在两缓存全部8场景逐字节轨迹等于B6，主缓存无锚在全部8场景等于r02。主缓存时间资格不查运动分数3.026284m，无锚3.007852m；敏感性缓存两者相对P的差分别0.654959m/0.651513m。新增锚/运动接入贡献得到支持。去掉R衰减主缓存2.347952m比P略优，衰减是共同成熟保护而非新贡献，不能写消融证实其必要。保持预登记主候选，不根据消融重新挑参数或改名。

全自然/七类/逐事件/恢复、修正、拒绝和失败均在final_verification.json及各metrics/per_epoch/per_update中；受控10m偏移方向可能抵消自然误差，某些缓坡/跳变/正常恢复结果变差。正证据主要是稳定偏差恢复；不宣称全面优越。只能作有限应用系统机制定位，见configs/contribution_scope.json和RELATED_WORK_MATRIX.md。

下一步正在验证角色/路线入口的技术适配：固定全部10方法×8场景与既有轨迹及接入日志精确比较，合成测试、initializer/KF-GINS/cache数值一致；随后冻结源码/config/原始SHA/初始化/事件/指标/文献范围，再开启parking00固定矩阵。当前test_performance_opened=false，无freeze，不执行署名、账号、付费或投稿。
