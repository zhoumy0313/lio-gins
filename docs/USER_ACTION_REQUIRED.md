# 一次性人工行动清单 — LIO-GINS-R1

2026-10-11更新。building00/parking00已由用户放入 `data/i2nav-dataset`，16文件和两个官方bag SHA全部校验通过；数据请求已解决，无需移动或再提供文件。

1. **隔离运行时：正尝试项目内替代，暂不要求系统操作。** Docker/Podman不存在，但现有Bubblewrap和用户命名空间实测通过。正在用项目内umoci解包锁定Noetic OCI；若rootless构建/运行通过，本项即可解决。若不可行，才需用户提供可用运行时或明确授权安装/启动Docker及必要服务。已备好的Docker方案位于 `containers/Dockerfile.noetic`、`containers/run_inside.sh`、`scripts/build_noetic.py`。系统权限边界来自 [AGENTS.md](/home/aaron/lio_gins/AGENTS.md) “sudo/权限扩张…要先获授权”和目标§15.2；未执行sudo、服务安装或用户组更改。
2. **可选元数据：** 如已有，提供官方local NED地理原点、该机器人KF-GINS初始化/IMU参数。固定仓库中的外参与IMU模型可以自行读取。原点未知时按目标§5.5预先固定共同初始平移；只报告初始位置条件化误差。初始化不足时使用明确登记的单历元known-initial-state备用协议，不把参考送进在线算法。

不需要账号、支付、作者信息或投稿权限。parking00只检查身份和元数据，性能在开发证据和冻结通过后才开启。原始数据现仅本地一份，SHA清单不是备份。
