# 断点恢复

当前P4最终验证运行中，完整目标尚未完成。先运行一条恢复检查：

```bash
.venv/bin/python scripts/resume.py
```

读取状态、Git、实际项目进程及收据；有项目进程时exit3，不重复实验，不自动打开留出或重新读取75GiB原数据。可选`--audit-data`才会重新数据校验。

当前driver：outputs/20261011T151637778113Z_P4_bc2078b6。主筛选r03 outputs/20261011T150927930407Z_P4_1dace17d已exit0，12组最终主配置完成；3轮共36，禁止继续调参。主缓存有22.7952%目标收益，但尚未通过同参数消融、第二缓存和文献定位门槛。等待真实final_verification.json及manifest；不能凭stdout部分结果freeze。

P0–P3真实命令/失败及版本见RUN_REGISTER.csv和阶段报告。Noetic已在rootless Bubblewrap构建，registry containers/derived_rootfs.local.json；Docker替代recipe未验证。完整前端EOF已正常关闭，相同输入前端变化未解决。所有sealed outputs/rootfs、原始数据和失败只读保留。

最终验证不支持时：写决策、claims、DELIVERY、作者简报与10问答；只交内部方法/实验草稿，不写负结果投稿稿、不打开parking00、不另起无限项目。通过时：先明确应用范围/代码数据参数科学冻结，才开留出。

当前无需人工数据/权限；用户提供文件全部匹配官方身份。未知地理原点用已声明共同初始平移，不作绝对WGS84主张。数据及数值只有本地保留，无已授权remote，不修改旧VPR、宿主ROS/Python/SSH/网络/驱动。

最新后继：P4全部门槛和80组合精确适配通过；freeze LIO_GINS_R1_20261011T154403129394Z（科学源码b6259cf，封存2274156）。P5 parent outputs/20261011T154446522435Z_P5_ae13844a正在运行，frontend outputs/20261011T154448421191Z_P5_cf163fe4；首次开启见TEST_OPENED.json。先resume.py及进程/日志，不重启。禁止改冻结source/config。原生前端结束后driver会自动完成cache、GNSS副本、B1和10方法全八场景，读取最终heldout_matrix.json及manifest后再离线完整汇总。
