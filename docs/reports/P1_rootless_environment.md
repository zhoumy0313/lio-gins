# P1：无需sudo的Noetic隔离环境

2026-10-11。现有用户命名空间/Bubblewrap实测可用，改用项目内OCI文件系统与Bubblewrap，不安装Docker或宿主ROS。

`apt download umoci=0.4.7+ds-2ubuntu0.1` / `dpkg-deb -x` 仅项目内工具；镜像拉取run `20261011T123536145200Z_P1_aa57b6d1` exit0，128.790s。每层长度/SHA核对；官方linux/amd64 digest保持4f01fa743be43da0e14ddf2ac29b5118d9c0eb4057c9761c13303b8a52fa9c4f。Docker v2→OCI只改变描述符媒体类型，原压缩层/config字节与SHA不变。

保留的失败：首拉取短响应不完整；构建wrapper调用API参数错误；5个APT下载失败；fontconfig root:staff chown不可映射导致依赖配置失败；宿主Humble环境污染及Noetic setup遇set-u；消息兼容包占位邮箱非法。每次另建run，复制以前失败的文件系统后再修复，不改旧封存目录。

最终构建run `20261011T130509928405Z_P1_4c5d376c` exit0，49.750s（依赖复用），`catkin_make -j4 -l4` 输出100%完成。构建清空继承环境；Noetic setup期间关闭未定义变量检查；包维护者仅为兼容包技术占位，不是论文署名。

约束：单UID rootless解包/安装不能保持多用户系统所有权；font目录采用可用的映射组，fakeroot仅为包元数据尝试。Ubuntu/ROS签名和包SHA验证未关闭，包版本保存于 `/opt/installed-packages.txt`。依赖版本、固定源码、编译产物、文件与符号链接身份封存；这不是Docker镜像构建结果，不能冒称Docker路径已验证。

运行时：网络/进程命名空间隔离、只读rootfs、只读单一原bag、独立可写output、清空宿主ROS环境、capabilities清除，无整个home和Docker socket。日志补丁分别保存scan-end时间、可用时刻/配准健康；不改算法与官方点数/噪声/迭代配置。

P1环境/demo/数据门槛完成；P2必须继续检查真实运行覆盖/时序/初始化和同输入基线。科学成功字段均false。

P2启动检查补充：只读rootfs无挂载点、无容器hosts/hostname及对非挂载/etc执行remount的失败均保留。改用私有临时顶层根、原OCI子树只读、顶层remount只读，显式注入localhost与lio-replay主机名。冒烟run `20261011T131414920017Z_P2_17e494e3` exit0，ROS master、FAST-LIO进程、原bag索引均通过。之前启动run不代表已成功回放。
