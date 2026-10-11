# 当前主张与证据

| 主张 | 状态 | 证据/边界 |
|---|---|---|
| 独立工作空间、原工作包保存、可恢复索引 | 支持 | P0 checkpoint、initial_workspace.json、完整性run exit0 |
| KF-GINS固定源码可在当前主机原生编译、官方demo输出有物理意义 | 支持 | P1 build/demo/独立健康检查；仅该官方demo输入/初始化 |
| 共同坐标、std、Joseph与一次GNSS更新等基础接口通过合成测试 | 支持于所测试条件 | 16项真实unittest，不能替代实测时间/标定/恢复验证 |
| Noetic镜像固定manifest存在 | 支持 | 匿名registry实际manifest与hash比对；没有验证layers、apt或build |
| 真实i2Nav定位管线已就绪 | 不支持/未执行 | 数据全部缺失、Docker不存在；P2未运行 |
| 新恢复机制超过强基线 | 未测试 | B4/B5/B6真实比较、P4和消融未运行 |
| 独立跨路线增益成立 | 未测试 | 未冻结、未打开parking00性能 |
| 恢复/一致性/滑窗单独具有新颖性 | 不支持此笼统主张 | 最近邻已有相关机制；需要具体增量与开发证据 |
| 完整目标完成/可投稿论文 | 不支持/未完成 | execution_complete=false；paper_ready=false；未生成稿件/作者名单 |
| 原始数据/数值已异地备份 | 不支持 | 仅本地保存；没有项目remote，也没有原始机器人数据 |
