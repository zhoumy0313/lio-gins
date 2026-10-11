# P1/P2：用户数据到位后的真实恢复检查

父checkpoint cd7343f；2026-10-11。16个原件约75GiB，保留用户目录，Git忽略原始数据，不移动/复制bag。

真实命令：`.venv/bin/python scripts/resume.py` → exit0，run `20261011T112420385892Z_P1_ef2f5c4e`，66.525s。两个bag完整SHA与官方值一致；8个辅助文本只记录身份，主线仍只用AT128/ADIS/F9P。

`.venv/bin/python scripts/record_run.py --phase P2 … -- .venv/bin/python scripts/audit_bag_interfaces.py` 初版exit1（lz4压缩未支持），run `20261011T123343300739Z_P2_c0543b3a`；补充压缩解码后exit0，run `20261011T123449847740Z_P2_ff316e8d`，3.221s。bag索引完整，开发256条IMU与文本时间最大差0.590微秒；20帧点云timestamp为float64 UNIX秒、ring uint16，未见逐点倒序。

bag率积分与文本增量差异仍需核对自定义原始IMU字段；不能声称已完成全程积分一致性。参考初始时间9064.0045，传感器先约28s，需明确初始化协议。

现有`unshare --user --map-root-user true`和Bubblewrap无网络测试exit0，具备无需sudo的隔离入口；项目内`apt download umoci=0.4.7+ds-2ubuntu0.1`及`dpkg-deb -x …`均exit0，没有宿主安装。锁定OCI第一次下载exit1，代理短响应未通过SHA；后继run用验证Range续传，构建结果尚未确认。

证据：`artifacts/data_audit/`与每个run的manifest/commands/SHA。parking00性能未打开，候选预算未使用。下一步完成rootless Noetic构建、IMU增量检查及预登记真实KF-GINS初始化。
