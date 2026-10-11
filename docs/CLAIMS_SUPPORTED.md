# 当前主张与证据

| 主张 | 状态 | 证据/边界 |
|---|---|---|
| 独立空间和原始工作包保留 | 支持 | P0 checkpoint、initial_workspace.json；仅本工作空间修改 |
| 固定KF-GINS可编译，官方demo有物理意义 | 支持 | 官方demo原生运行及独立健康检查；不是building00实验 |
| 两路线原始数据到位且bag身份正确 | 支持 | 全16文件P1审计exit0，两个bag SHA与固定官方值匹配；仅本地一份 |
| Noetic隔离环境已真实构建并可启动 | 支持 | rootless build130509928405及ROS smoke131414920017 exit0；不是Docker build验证，单UID文件所有权有近似 |
| building00原生GNSS/INS基线运行 | 支持于声明初始化 | B1噪声STD×0.5/1/2全部覆盖100%；选×2 RMSE3.702869m；共同初始平移，未声称绝对WGS84误差 |
| building00完整AT128/ADIS轨迹缓存 | 支持于首轮位姿接口 | 131528442554输出12440/12443；cache134125698776 exit0，最大间隔0.125356s；最终原生计时缺失，重放验证进行中 |
| 真实同输入强基线全部可靠 | 尚未完成 | P3预注册Q、NIS、Huber、12档固定恢复；未运行真实性能筛选；不得仅凭exit0登记PIPELINE_READY |
| 新恢复机制超过匹配强基线 | 未测试 | 候选修订0/3；需要事件收益、正常代价、重复及消融 |
| 独立跨路线增益 | 未测试 | parking00只做元数据与SHA，未冻结、性能关闭 |
| 一致性/滑窗/恢复本身新颖 | 不支持笼统主张 | 最近邻已有相近机制；B6为局部适配，不冒称完整Dual-ACKF复现 |
| 参考系统独立于LiDAR | 不支持 | MM/INS使用AT128，与当前LIO共享传感器；必须披露 |
| 人工压力是现场多路径/真实失锁 | 不支持 | 派生自原始F9P，七类21事件是受控扰动，故障标签仅评价可读 |
| 完整目标已完成或论文可投稿 | 不支持/未完成 | execution_complete、positive_effect_supported、novelty_supported、paper_ready分别false |
| 数值/原始数据已异地备份 | 不支持 | 当前仅本地保存，SHA不是备份，无项目remote授权 |
