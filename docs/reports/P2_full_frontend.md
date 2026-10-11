# P2：真实前端、完整计时和数值敏感性

2026-10-11。KF-GINS独立基线及共同首历元初始化见P2_initial_native_baseline.md。FAST-LIO为固定官方i2Nav AT128/ADIS适配，仅构建/消息依赖及日志补丁。P2真实运行和接口检查已执行；管线科研就绪仍待P3与前端敏感性复核。

| 检查 | run | 真实结果 |
|---|---|---|
| 首个完整1×ROS bag回放 | 20261011T131528442554Z_P2_9d0fac69 | launcher exit0，1300.9774s，12440/12443位姿；EOF停钟导致native节点被SIGTERM，最终计时缺失 |
| 首轮完整位姿缓存 | 20261011T134125698776Z_P2_0de7714e | exit0；无>150ms间隔；timing_complete=false，供敏感性重放 |
| 新launcher挂载尝试 | 20261011T134703603252Z_P2_133938a0 | exit1：不能在只读/opt创建新helper；原输出保留 |
| 早停启动尝试 | 20261011T134801072586Z_P2_479d01b3 | -15（runner返回143）：发现/clock非latched，主动早停修正EOF bootstrap；部分输出保留 |
| 完整1×回放与正常EOF关闭 | 20261011T134909303110Z_P2_626b9771 | exit0，1286.7126s；12440位姿+12440计时记录，无SIGTERM升级 |
| 新缓存与计时逐帧验证 | 20261011T141044340351Z_P2_9dd3f300 | exit0；timing_complete=true |
| 相同输入/二进制重复比较 | 20261011T141044817378Z_P2_c2f0e582 | 脚本exit0，但发现数值不一致：局部3D差异RMS3.601288m、最大9.787640m |
| 接口/滤波/因果/独立评价检查 | 20261011T141045393982Z_P2_cc6927ed | unittest exit0，34项；含已知(3,4)m误差→水平RMSE5m与缺测覆盖保留 |
| 未封存目录只读审计 | 20261011T135946876914Z_P2_00317a14 | exit0；一个历史输入预检查失败仅留配置、无原退出码；不补造收据 |

实际主命令（均由record_run封存完整argv、输入和源代码快照）：

```bash
.venv/bin/python scripts/run_lio.py data/i2nav-dataset/building00/building00.bag
.venv/bin/python scripts/build_lio_cache.py outputs/20261011T134909303110Z_P2_626b9771
.venv/bin/python scripts/compare_frontend_repeats.py outputs/20261011T131528442554Z_P2_9d0fac69 outputs/20261011T134909303110Z_P2_626b9771
.venv/bin/python -m unittest discover -s tests -v
```

完整前端bag SHA与官方一致，原件只读，仅bag挂载，不挂真值或整个home。原生计时均值17.321483ms，P50 17.581010ms，P95 22.767489ms，最大66.425680ms；这是native t5−t0（IMU处理至增量地图），不包括输入预处理、回调、发布和等待。总wall含文件哈希、ROS启动与按1×播放，不能当逐帧纯CPU耗时。缓存可用时间为ROS时钟采样加10ms分辨率裕量，不冒称现场端到端延迟。

首轮缓存间隔最大0.125356s，位移速度中位1.42m/s、最大2.48m/s；四元数只对六位小数序列化误差作明确归一化。没有把配准残差或轨迹离散度当增量协方差。

**重要未解问题**：两个run扫描起止时刻全部相同，初始状态一致，约80.2s开始数值分叉。去掉共同初始坐标差异后，完整后续3D差异仍约3.64m RMS。因此没有登记“数值可重复”。固定源包含异步ikd-tree重建，但当前只是原因假设，不能断言故障根因或用改算法掩盖。新缓存在打开外层精度前已按完整计时选定，不能再按更低误差更换。

`configs/frontend_sensitivity_protocol.json`要求最终候选及选中B3/B4/B5/B6在两缓存上固定参数重放，不对旧缓存重新调参。两份缓存都需满足主要改善和正常代价门槛，改善必须超过其跨缓存变化；只有两个输入重放，不能算独立路线统计证据。未完成此复核前禁止科学冻结。

历史目录20261011T133756615798Z_P2_813a276b保留缺失timing输入的配置，无原退出码；审计明确这一证据缺口。未来record_run输入预检查错误会封存FAILED，executed=false。完整保存已有失败、不改sealed run或rootfs。

P3顺序驱动正在运行预注册共同Q、NIS/Huber及十二档固定恢复。候选0/3，parking00性能未打开，所有科学成功字段仍false。下一步完整读取强对照及代价，之后仅围绕实际剩余问题开展有界机制尝试。
