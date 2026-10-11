# 一次性人工行动清单 — LIO-GINS-R1

2026-10-11；P0 完成，P1 已完成无阻塞工作；真实 P2 基线尚未开始。后续按同一清单更新解决状态，不重复请求、不无限重试。

## 1. 必需：提供最小真实数据

官方 [OneDrive](https://1drv.ms/f/c/7da41598f6f07e02/EgJ-8PaYFaQggH3CBQAAAAABlmP45s_NHaBuLd3xXk04AA?e=sMNBhd) 两次匿名访问均 TLS EOF；[百度网盘](https://pan.baidu.com/s/1UGZI-LvoTKxH6GN6JbzMZw?pwd=hs6p) 返回提取码/验证码交互页。没有取得对象列表、文件体积或真实数据；分享网页不当作 bag。停止自动重试，未登录账号、未绕过验证码。证据：`outputs/20261011T050602052413Z_P1_d8cc1b68/access_attempts.json`。

请将下列原件放入本项目，或提供无需账号的授权直达下载路径和已知体积（先下载小文本，保留至少80 GB磁盘余量）：

| 开发 building00 | 路径 |
|---|---|
| building00.bag | `/home/aaron/lio_gins/data/raw/building00.bag` |
| building00_ADIS16465_IMU.txt | `/home/aaron/lio_gins/data/raw/building00_ADIS16465_IMU.txt` |
| building00_F9P_GNSS.pos | `/home/aaron/lio_gins/data/raw/building00_F9P_GNSS.pos` |
| building00_groundtruth.nav | `/home/aaron/lio_gins/data/reference/building00_groundtruth.nav` |
| building00_trajectory.csv | `/home/aaron/lio_gins/data/reference/building00_trajectory.csv` |

parking00 同样五个文件，使用相同目录、替换文件名前缀。取得后只校验身份/元数据，开发证据和冻结通过之前不打开其算法性能。最低启动可先提供 building00 三个文本；完整主线必须有其原始 bag，不能用别人 FAST-LIO 轨迹替代。

## 2. 必需：可用的隔离容器运行时

Docker/Podman 均不存在。Noetic 官方 tag 的 registry digest 已真实核实，构建上下文和日志补丁已准备；实际构建检查 exit127/BLOCKED，尚未拉镜像层或运行 FAST-LIO。

请提供现有、用户可用的 Docker 运行时，或明确授权安装/启动 Docker 及必要系统服务。当前 recipe 使用 Docker CLI；若只提供 Podman，可在项目内适配命令。待审文件为 `containers/Dockerfile.noetic`、`containers/run_inside.sh` 与 `scripts/build_noetic.py`；不要求 CUDA、GPU Toolkit 或 ROS1↔ROS2 bridge。

此权限需求来自 [AGENTS.md](/home/aaron/lio_gins/AGENTS.md) 的“sudo/权限扩张、系统网络/驱动变更、账号操作、付费、删除原数据和正式投稿要先获授权”，以及 [目标§15.2](/home/aaron/lio_gins/docs/GOAL_LIO_GINS_R1.md:870) 的“安装/启动需sudo的新系统服务、加入 docker 组等权限提升”。因此本次没有执行系统安装、sudo 或组权限更改。

## 3. 如已有，可一并提供的元数据

local NED 真值地理原点/导出定义、该机器人 KF-GINS 官方初始化配置、AT128/ADIS 时间语义补充。固定公开仓库已提供杆臂与外参，无需重复提供；WinTA-GIL 原文已可访问，当前也不需要重复提供。没有地理原点时可按目标§5.5事先登记所有方法共用的一次初始平移，但只报告初始位置条件化误差，不能声称绝对WGS84精度。

恢复命令：`.venv/bin/python scripts/resume.py`。它先检查状态/Git/进程，再只审计新文件，不运行留出评价。所有当前结果仅本地保留，未配置 remote，也没有异地数据备份。
