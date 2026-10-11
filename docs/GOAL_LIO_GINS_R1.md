# LIO-GINS-R1：面向 GNSS 退化与恢复的分层定位研究
## Codex 全目标推进文档、实验协议与工作规范

- **Goal ID**：`LIO-GINS-R1`
- **文档日期**：2026-10-11，Asia/Shanghai
- **执行位置**：用户在 Ubuntu 22.04 上新建的独立工作空间；Mac 仅作远程控制与审阅端。
- **文档性质**：研究计划与执行约束。文中的候选机制、参数范围、预期作用都不是已验证结果。
- **起点**：公开源码与公开数据。既有 VPR 工作空间保持不动。本科论文只提供结构与思路，不继承其数值结论。
- **主交付**：真实可复现的定位管线、具有明确证据的改进或否定结论、完整实验记录，以及在证据成立时形成的 6 页内会议稿。
- **操作原则**：先获得可用基线和有意义的开发证据，再进入新方法与独立测试。不要把“程序跑完”“文件很多”“PDF 生成”当成科研目标完成。

---

# 0. 给执行代理的总指令

读取本文件及工作空间根目录 `AGENTS.md`，登记本目标后，按 P0→P7 推进。普通代码修改、局部实验、文献核查、数据校验、报告与草稿整理可以自主完成，不需每一步询问用户。

**主线固定为：局部激光惯性运动传播 + 接收机 GNSS 绝对位置校正 + 运动一致性及恢复过程的观测管理。**

FAST-LIO2 是局部运动实现；KF-GINS 是独立的 GNSS/INS 对照，也可作为受控备用路线的实现平台。**第一版不把两个滤波器的高频后验位置再次作为独立观测相加。** 本选择有意收敛上一篇讨论中的多种可能，避免同时修改三套滤波系统。

任务成功的候选标准是：在事先选定的 GNSS 退化/恢复条件下，相对使用相同传感器的合理强基线获得可重复、可解释的改善，并报告正常条件代价。幅度可以小，但必须能归因于新增机制。录用由审稿决定，不在本 Goal 中保证。

必须遵守：

1. **科学目标与工程目标分别登记**。`execution_complete` 不等于 `positive_effect_supported`，后者也不自动等于 `novelty_supported`。
2. **未出现有依据的开发改进，不提前打开留出路线的性能结果。** 不要像“失败后仍跑完一次独立测试，再写一篇失败稿”那样消耗新数据。
3. **允许有界的开发迭代**。首个候选失败后，先诊断，允许至多两次针对同一研究问题的修订；不是一失败就写结论，也不是无限试公式。
4. **先解决真实问题，再完善论文叙事**。不能为了一个预写标题反复挑场景、删对照、改真值或换统计口径。
5. **保留全部已生成成果**。原始数据只读，实验目录不可覆盖；可复用不可变缓存，不为每个参数组合复制全部点云和数据。
6. **人类操作边界**：系统驱动/全局网络/权限改动、账号登录和服务条款、付费、创建远程仓库或扩大可见性、署名、版权签署与正式投稿，需要用户处理或明确授权。
7. 本文件给的是普通 Codex 项目目标，不假定存在某个特定的“注册 Goal”产品命令。若客户端有长任务功能可用；否则使用本文状态文件断点续做。

---

# 1. 研究定位与论文叙事：先把目标讲清楚

## 1.1 拟解决的具体问题

面向有 LiDAR、IMU 和 GNSS 的地面移动平台，研究 GNSS 从可用到退化、短时失锁再恢复的过程。局部里程计提供连续运动；全球观测提供长期参考，但质量会变化。

本轮关注的不是“再增加一个传感器后是否更好”，而是：

> **如何利用不受当前全球修正直接影响的局部运动证据，管理可疑 GNSS 的降权、隔离和重新接入，减少异常全球观测引起的定位误差，同时避免长期拒绝恢复后的有效观测。**

可检验的研究假设：同样的 LIO/GNSS 输入下，仅看当前绝对创新的门控，与额外观察短时相对运动和恢复历史的策略，可能在误接收、误拒绝及重接入代价上存在差异。

这是待验证假设，不是对所有现有方法的断言。若合理设置的 NIS/Huber/固定恢复策略已经解决问题，不得称它们失效。

## 1.2 论文可以怎样命名

工作名称：**运动一致性与恢复感知的局部—全局定位框架**。

候选英文题目：

- `Motion-Verified GNSS Reacquisition for Robust LiDAR–Inertial Global Localization`
- `Motion-Consistency-Guided Global Updates for Hierarchical LiDAR–Inertial Localization`

当最终贡献只成立于 GNSS 重接入，应选第一类聚焦题目。若没有恢复阶段证据，就删去 `Reacquisition`。不要在标题里提前写 `Optimal`、`Integrity-Guaranteed`、`All-Weather` 或 `State-of-the-Art`。

`LIO-GINS-R1` 只是工程目标名；不是证明系统有新颖性的算法缩写。

## 1.3 正文的表达原则

摘要和方法总览先讲**问题、输入、估计层次和新增决策机制**，而不是先列仓库名称。但在相关工作和实现细节中，必须准确写明 FAST-LIO2、KF-GINS 及数据来源、版本与修改范围。

合适的表述模板（结果未完成前用“研究/检验”，完成后据证据修改）：

> 本研究构建由局部运动传播、全球观测可信度监测及恢复更新组成的分层定位流程。与仅依赖当前绝对创新的更新策略不同，候选方法利用过去局部位移与 GNSS 位移的一致性约束观测重新接入。我们在相同传感器输入和统一初始化条件下，对比固定融合、创新门控、鲁棒降权及固定恢复策略，检验其在 GNSS 退化和恢复区段的作用。

不能写成：

> 我们首次提出 LiDAR/IMU/GNSS 融合；将两个成熟后验结果加权即可证明新框架；提出一个新名字便解决了鲁棒性；只要百分比提高就能录用。

## 1.4 贡献归属分层

| 层次 | 内容 | 论文处理 |
|---|---|---|
| 已有基础 | LIO、GNSS/INS、KF/ESKF、NIS、鲁棒降权、分阶段恢复等 | 引用，不宣称发明 |
| 本项目实现 | 统一格式、时间/坐标、缓存、日志、ROS 容器 | 可复现性与实现，不自动算算法创新 |
| 候选增量 | 局部运动证据怎样控制隔离和重接入，且区别于最近邻方法 | 必须说明差异并用同结构消融支持 |
| 实验发现 | 某类异常或恢复场景中的精度、误伤、恢复时间变化 | 必须给完整场景与失败条件 |

若最终只验证了已知方法组合的工程收益，可以写应用或系统研究，但不能把组合包装为首次理论方法。

## 1.5 最近邻工作已经存在，必须优先读

本次核查发现 `WinTA-GIL`（2026，arXiv:2607.04879）已研究 LIO/GNSS 窗口对齐、运动几何一致性触发，以及恢复后的航向修正。它与当前方向很近；其作者单位包含武汉大学测国重。[S8]

另外，2026 年 `Robust Urban INS/GNSS Positioning Under Degraded GNSS Conditions Using a Dual-Adaptive Cubature Kalman Filter` 已包含正常/退化/失锁/恢复分阶段的更新调节。[S9]

因此，**“滑窗”“一致性”“恢复状态机”“调协方差”都不能分别直接认定为新意**。P1 就建立具体机制对照表：输入、修改状态、观测使用次数、是否估计航向、恢复触发、正常代价、数据和代码。原文不可得时登记为未核实，不猜公式。

本计划默认不实现 WinTA-GIL 的反复航向窗口优化，不把“动态 Procrustes”作为主贡献。若与组内已有工作同题，优先沟通可区别的问题与可用基线；不要等全文写完才查重。

---

# 2. 固定研究架构与信息流

## 2.1 主线 A：本轮优先实现

```text
AT128 点云 + ADIS16465 IMU
            │
            ▼
     FAST-LIO2 局部前端 ─────► 局部位姿、增量、可用性/配准诊断
            │                                 │
            │                         局部运动一致性监测
            ▼                                 ▲
      三维位置 KF 传播 ◄───────────────────────┤
            │                         F9P 原始定位结果
            │                                 │
            └────────► GNSS 可信度与恢复管理 ──┘
                              │
                              ▼
                     全球位置 KF 观测更新
                              │
                              ▼
               全球参考位置 + LIO 姿态 + 状态标志

ADIS16465 IMU + 同一 F9P 定位结果 ─► KF-GINS（独立对照）
独立评价器读取参考轨迹；算法侧不读取参考轨迹。
```

这里“原始定位结果”指接收机提供、未经本项目 KF-GINS 处理的 GNSS 位置，不是原始伪距/载波相位。i2Nav-Robot 不公开这些卫星原始观测。[S1]

**框架贡献的载体是全球观测管理层，不是重写 FAST-LIO2。** KF-GINS 在主线 A 中是 GNSS/INS 对照，不是必须被二次融合的后验信息源；论文不能把对照算法画成主方法内部模块。

## 2.2 与毕设的关系

保留“局部相对运动—全球绝对参考—轻量后端”的思想。原论文第 3 章、图 3.1 和图 3.4 可作为自己的结构设计参考。

必须改进的研究规范：

- 只用允许的初始化数据建立坐标变换，不用全轨迹配准给在线方法预知未来。
- 原三维位置、固定旋转、单位观测矩阵的外层模型，本质上可用线性 KF 描述，不要仅为了高级感称为全状态 ESKF。
- KF-GINS 本身是 21 维误差状态 GNSS/INS 算法；不要把外层 3 维模型与它混为一谈。[S3]
- 本科中的结果和参数未在当前环境重跑，不可抄进新论文；旧表不能用来证明新框架有效。
- 官方 i2Nav 数据是轮式平台；没有新四足数据时，标题、摘要不能宣称在四足机器人上验证。[S1]

## 2.3 不做后验信息重复融合

主线 A 不把 `KF-GINS.position` 当成每 5 ms 一条新的独立 GNSS 测量。原因不只在共享 IMU，还在后验包含历史 GNSS 信息及其时间相关性。

若为了重现毕设实现 `legacy_posterior_fusion`：仅列为次要历史对照，公开输入相关性假设；不可将其当最优 KF，也不可让它阻塞主线。第一轮非必需。

LIO 与 GNSS 更新后的估计之间也可能有时间相关性；外层 Q/R 是工程近似，不宣称协方差严格一致或统计最优。参考系统也有相关性限制，见第 4 节。

## 2.4 备用 B：仅在雷达数据或部署实质性受阻时

可先在 KF-GINS 原生 `GIEngine::gnssUpdate()` 中实现成熟 NIS、Huber 对照并验证输入与评价。若最终没有 LiDAR 数据，只能形成 GNSS/INS 鲁棒更新研究，题目必须相应缩小。

从 A 转到 B 要记录 `ARCHITECTURE_DECISION.md`。不允许无记录地一会儿在 KF-GINS 内加更新、一会儿在外层加更新、最后把不同版本混成一张结果表。

---

# 3. 源码、系统环境与部署顺序

## 3.1 已核查的上游版本

| 资源 | 本次核查版本/内容 | 用途 |
|---|---|---|
| `i2Nav-WHU/KF-GINS` | `8291a93e49de513fe9d21f819500d39082ded611` | GNSS/INS 基线与官方 demo |
| `i2Nav-WHU/i2Nav-Robot` | `2ffdca6d56e6432d4daf27c070e570171548f32d` | 数据说明、标定、bag SHA |
| `i2Nav-WHU/i2Nav-Robot-Baseline` | `6c602f8d974fbe5be1183771541c90057e9e3bb6` | 已适配 AT128 的 FAST-LIO2 |
| `hku-mars/FAST_LIO` | 执行时记录准确 commit | 方法原出处与代码差异参考 |
| `i2Nav-WHU/awesome-gins-datasets` | 执行时记录准确 commit | 无雷达备用、IMU 参数与格式学习 |

实际拉取后重新验证 commit，记录 URL、版本、许可证、子模块版本与修改补丁。上游有更新不等于应立即升级；冻结后禁止悄悄跟随 main。

## 3.2 不重装 Ubuntu

保留 Ubuntu 22.04、现有 SSH、FlClash、Codex、驱动和 Python 工程。

- KF-GINS：原生 CMake/C++ 编译。Eigen、yaml-cpp、Abseil 已包含在其 ThirdParty，不先重复安装一批全局依赖。[S3]
- FAST-LIO2：优先 Ubuntu 20.04/ROS Noetic 隔离容器，头less 运行。先验证官方镜像 tag 实际可取，再固定 digest，不捏造镜像哈希。
- ROS Noetic 已于 2025-05-31 结束支持。容器用于离线复现，不对公网暴露 ROS 服务，不移除宿主 ROS2。[S10]
- 这一管线主要使用 CPU；不把 NVIDIA Container Toolkit、CUDA 重装或 Jetson 部署列为前提。
- 初期不需要 ROS1↔ROS2 bridge、真实雷达、RViz、Nav2、可视化应用或数据库。

## 3.3 首次命令应由脚本生成并记录

在安装前检查：`pwd`、Git 状态、CPU/RAM/磁盘、现有 Docker/Podman、Python、CMake、编译器及网络。`nvidia-smi` 仅作信息采集，缺少 GPU 不直接判本项目不可做。

KF-GINS 建议命令模式（输出配置必须改到本轮目录）：

```bash
cmake -S third_party/KF-GINS -B build/kf-gins-original -DCMAKE_BUILD_TYPE=Release
cmake --build build/kf-gins-original -j4
# 可执行文件实际位置按上游 CMake 检查；不能凭猜测记录成功。
# 使用复制并改为本轮独立 outputpath 的官方 demo YAML 运行。
```

上游 CMake 可能把 bin/lib 写回其源码目录；把这些生成物加入排除项，记录而不是误判源码改变。若调整输出目录，仅作为构建补丁保留，不混入算法增益。

容器自行构建可复现 Dockerfile，记录 apt 包与镜像 digest。禁止直接照抄需要 `--privileged`、挂整个 home、`xhost +` 的示例。只挂项目必要目录；原始数据只读、输出可写；不挂 Docker socket 给不可信容器。

容器内 `127.0.0.1:7890` 不自动等于宿主 FlClash。先验证代理路径，必要时采用受控宿主网关设置；不要修改全局路由、关闭 TLS 或把订阅写入 Dockerfile/Git。

## 3.4 FAST-LIO2 的实际配置：不要再次认错传感器

官方 `FAST_LIO/config/i2nav.yaml` 实际使用：[S2]

```yaml
common:
  lid_topic: /hesai/at128/points
  imu_topic: /adi/adis16465/imu
  time_sync_en: false
preprocess:
  lidar_type: 4
  scan_line: 128
  timestamp_unit: 0
```

**先以 AT128 + ADIS16465 跑通。** 它不是 Mid-360 配置。

`config/mid360.yaml` 是另一个模板，其话题、FRD/FLU、外参不能原样套本数据。Mid-360 替换只可在主线稳定后作受控补充，且所有对照统一换前端，不能拿不同传感器/前端配置证明后端创新。

检查 `preprocess.cpp/.h` 的 AT128 点类型、逐点时间单位、帧起止时刻、IMU 轴向、输出 pose 的物理参考点。初期只允许加日志、输出与必要适配；不随意调低点数、改变去畸变或降低基线精度。

---

# 4. 数据取得与选择

## 4.1 只取必要序列，不下载约 450 GB 全集

按官方元数据事先选择：[S1、S4]

| 序列 | 首要角色 | 官方场景 | 本轮用途 |
|---|---|---|---|
| `building00` | 开发 | 室外，GNSS degenerated，1201 s | 方法开发、异常/恢复诊断 |
| `street00` | 可选开发控制 | 室外动态，1380 s | 验证非目标条件代价；不预设其所有 GNSS 都正常 |
| `parking00` | 留出路线 | 室内外，1141 s | 参数冻结后的跨路线验证 |
| `playground00` | 可选后续扩展 | 室外、structureless，1786 s | LIO 几何挑战，不冒充无困难的正常对照 |

最低可启动数据：building00 的文本；最低完整主线：building00 的 bag+文本；最低跨路线验证：再加 parking00 的 bag+文本。

## 4.2 下载入口与人工交接

官方入口：

- 百度网盘：<https://pan.baidu.com/s/1UGZI-LvoTKxH6GN6JbzMZw?pwd=hs6p>
- OneDrive：<https://1drv.ms/f/c/7da41598f6f07e02/EgJ-8PaYFaQggH3CBQAAAAABlmP45s_NHaBuLd3xXk04AA?e=sMNBhd>
- 入口变化时以固定上游 README 后续人工核实为准；不要编造对象直链或把分享网页 HTML 存成 bag。

Codex 可枚举公开可访问文件及体积，能直接下载则下载；涉及登录、验证码、接受条款或失败超过两次原路线及一次合理备用路线，就生成 `docs/USER_ACTION_REQUIRED.md`。同时继续编译、demo、解析器和合成测试，不反复等网络。

请用户/伙伴课题组提供的最小清单：

```text
building00.bag
building00_ADIS16465_IMU.txt
building00_F9P_GNSS.pos
building00_groundtruth.nav
building00_trajectory.csv
（同样一套 parking00，先保存不看性能）
可选：street00 对应文件、OEM7_GNSS.pos、MID360_IMU.txt
```

优先下载小文本与元数据，再下载大 bag。bag 中相机、雷达等暂不使用，后续可创建派生裁剪 bag；原 bag 不覆盖、不删除。

本轮取原始 `.bag` 与实际文本文件，不能用别人跑好的轨迹替代自己的 FAST-LIO baseline。别人结果可作调试参照，必须注明来源。

## 4.3 校验

官方给出的原始 bag SHA-256（下载后与固定仓库再次核对）：[S5]

```text
building00.bag  700ad92d3c856b7ac9c6b0a79d2553bba1144a6dd3b688ad35f3cd77f20e80cb
parking00.bag   83a2101058b3a3ff4400d4cfc2bd3d48ed97714738c0734aa6d65dc29a7ce6ea
street00.bag    fcc12aa908224c0a2aaadc237bd7e8270281e41bef94babe00c5396521c9745a
```

文本没有上游 checksum 时记录本地 SHA，注明仅为本地身份校验，不声称验证了上游真实性。检查 bag 索引、话题类型、计数、时间跨度、丢包和 header stamp，别只检查文件能否打开。

创建 `DATA_MANIFEST.json`：来源、下载方式、原名、大小、SHA、许可证、角色、路径、时间范围、GNSS有效数、IMU频率、点云频率、真值覆盖、异常统计。

## 4.4 必须保留的参考真值限制

官方说明参考位置/速度/姿态投影到 **ADIS16465 中心**。building00、parking00 的参考来自导航级 IMU 与基于 AT128 的地图匹配后处理；部分室外序列来自 OEM719/导航级 IMU 后处理。[S1]

因此：

- 参考不是本研究的 FAST-LIO 输出，但 AT128 主线与参考可能共享点云信息，误差不保证独立；论文写明这一点。
- 主输入选 **F9P SPP**，不要同时把 OEM719 或 groundtruth 当作另一条“干净 GNSS”喂给主方法。
- OEM719 RTK 可另设输入级别实验，所有方法使用相同输入，记录与参考的依赖；不能混在主表。
- 官方没有发布预建地图和原始卫星观测。本轮不做基于私有地图的定位，也不做伪距紧组合。[S1]
- “官方标称约 2 cm”不等于每个历元的独立误差都正好 2 cm；小于参考可信精度的微小改善不能强作结论。

---

# 5. 时间、坐标、标定与初始化契约

**这些是运行门槛，不是靠事后轨迹好看来调的参数。** 每一个最终数据接口必须有单位、轴向、参考点和时间语义。

## 5.1 时间

- i2Nav 文本时间为 GNSS 周内秒 SOW；bag header 通常为 UNIX 秒。[S1]
- 建立 `week + sow` 的统一绝对时间，内部允许相对起点秒提高精度。记录原始时间和变换。
- 官方针对该数据给出 GPS−UTC=18 s 的转换，核查采集日期适用性；不能把 18 s、时区 8 h 和 IMU 延迟混用。
- 用同一 ADIS 数据的 bag 与文本序列交叉核对时间及增量积分；不得靠最大化对真值的拟合来调时间偏移。
- ROS bag 记录时间不等于测量时间，优先依据明确的 header/逐点时间语义。
- 缺包、重复、倒序都保存，不把异常 Δt 默默替换为中位数，不把整段时间压缩。
- GNSS 与 IMU 非同步时保留真实时间；KF-GINS 的插值与反馈顺序必须遵守原源码，不在外面重复插值一次。

## 5.2 IMU 与 GNSS 格式

`*_ADIS16465_IMU.txt` 已经是 `[t, Δθx, Δθy, Δθz, Δvx, Δvy, Δvz]`，单位 rad、m/s，**不可再次乘 Δt**。

来自 `sensor_msgs/Imu` 的角速度/比力才需按实际采样积分并验证；不凭文件后缀猜是哪一种。

F9P `.pos` 为 `[t, lat, lon, altitude, stdN, stdE, stdD]`；纬经是度，标准差是米。协方差用标准差平方；NavSatFix covariance 本来是方差，不能再平方。

KF-GINS `.nav` 输出是经纬高格式；i2Nav-Robot `*_groundtruth.nav` 则是 local NED。两个 `.nav` 必须用不同 schema，禁止一个通用解析器按相同列数读取。[S1、S3]

F9P 是 SPP，不能写成 RTK。若某些 `std=0`、NaN 或质量缺失，保持原值，输入到过滤层时使用事先声明的噪声下限/无效规则，并让所有对照共用这套清洗。

## 5.3 坐标、杆臂和外参

统一内部导航系选择 NED，位置单位 m。定义 `R_A_B` 表示 B 系向量旋到 A 系，`t_A_B` 表示 B 原点在 A 中的位置；所有函数和文件遵守同一约定。

官方 GNSS 杆臂是 ADIS16465→天线，表达于 FRD：`[0.0, -0.07, -0.365] m`。使用前读取固定 `calibration.yaml` 并验证。[S6]

- 查清 FAST-LIO 导出的 pose 是 IMU 中心还是雷达中心；必要时一次变换到 ADIS 中心。
- 任何矩阵/四元数必须检查单位正交、det=+1、xyzw/wxyz 顺序及二者一致性。
- 字段名 `T_lidar_imu` 不能代替旁边的坐标变换公式；依据 `P_i=R_i_l P_l+t_i_l` 解释。
- Mid-360 的 IMU 在此数据中已由 FLU 转为 FRD；不要二次翻转。
- 不用同一数值外参同时连接 ADIS 与 Mid-360 内置 IMU；它们是不同参考中心。
- 不确定地理原点、椭球高/正常高或局部 NED 定义时，先请求原点/导出规则，不凭“轨迹差不多”找平移补丁。

## 5.4 初始化分为两种协议，不许混写

**主协议：因果/给定标定初始化。**

使用官方配置或仅初始允许时段的传感器观测建立公共起点、重力方向、局部到 NED 的旋转。初始时间窗建议上限 90 s，实际规则在看正式误差前确定。位置来自可用 GNSS；静止段估计横滚/俯仰及可估计的零偏；航向必须来自足够运动、外部已知初始航向或明确的初始对准方法。低成本 IMU 静止并不自动给出可靠航向。

若用初始 GNSS/LIO 轨迹对齐，限定为初始化段、无尺度的刚体变换，固定后进入评价；记录运动长度、可观测条件和残差。不能每个待评价区段重新对齐。由 GNSS 位置轨迹估计航向时，低速、多路径和近静止可能使结果不可靠，必须显式判初始化失败。

**受控备用协议：已知初始状态的导航比较。**

若官方没有可复用初始对准而时间有限，允许在打开正式性能前统一规定：只从参考导出一个固定初始历元的状态，给所有比较方法同等初始条件，之后参考只用于评价。独立测试也同样执行；论文明确是 known-initial-state benchmark，不宣称解决了无先验全局启动。用 `initial_condition.json` 记录来源和读取的唯一历元，初始化导出器与在线算法隔离。

两种协议分别报告，不把后一种伪装成前一种。选定方式之后不能根据测试误差换初始化。

## 5.5 参考原点与评价对齐

优先从官方元数据/数据提供者取得 local NED 地理原点，使 GNSS/KF-GINS 与参考在同一个坐标中评价。

若确实无法取得，允许以预定初始历元进行**所有全球方法共享、仅一套固定平移**的局部参考评价；清楚标为“初始位置条件化误差”，不能据此宣称绝对 WGS84 定位精度。不能为每个方法分别最小化全程误差。

允许另给 FAST-LIO 的标准全轨迹刚体对齐 ATE 作为前端健康检查，但它是**离线 gauge-aligned 里程计指标**，必须与全球定位主表分开，不能拿它和原始全球 RMSE 直接排名。

---

# 6. 最小滤波实现：先正确，再加观测管理

## 6.1 局部传播

设外层状态为 ADIS 中心的三维位置 `p`，LIO 同中心局部位置为 `l_k`，初始化后固定局部到 NED 旋转为 `A`：

\[
\hat{\mathbf p}_k^- = \hat{\mathbf p}_{k-1}^+ + A(\mathbf l_k-\mathbf l_{k-1}),\qquad
P_k^-=P_{k-1}^+ + Q_k.
\]

这是均值传播，不能把随机噪声样本 `w_k` 加进估计均值。

第一版 Q 使用统一、开发集标定的低维参数模型，例如时间项加路程项；同一套 Q 用于所有外层对照。LIO `P_pose(k)+P_pose(k-1)` 不是当然正确的增量协方差；相邻状态相关，不能用无说明的拼接声称严格传播。

LIO 重启、时间跳跃、配准失效必须有状态标记，不把重启后位移当真实运动。第一版遇到无法恢复的 LIO 中断，明确输出不可用并计入覆盖/失败，不悄悄用真值或另一滤波器跳接。

## 6.2 天线位置观测

GNSS 量测为天线位置 `z^G`，LIO 姿态提供 `R_n_b`，杆臂为 `ell_b`：

\[
h(\mathbf p_k)=\mathbf p_k+R^n_{b,k}\boldsymbol\ell_b,
\qquad \mathbf r_k=\mathbf z^G_k-h(\hat{\mathbf p}_k^-).
\]

在本三维状态模型下，姿态作为外部输入，位置 H=I。姿态/杆臂不确定性的影响计入测量模型近似并披露；不声称同时估计完整姿态与偏置。

更新：

\[
\Omega_k=HP_k^-H^T+R_k^{\mathrm{eff}},\quad
K_k=P_k^-H^T\Omega_k^{-1},\quad
\hat{\mathbf p}_k^+=\hat{\mathbf p}_k^-+K_k\mathbf r_k.
\]

使用分解/线性求解，不手写显式逆；使用 Joseph 协方差更新并检查数值对称/正定：

\[
P_k^+=(I-K_kH)P_k^-(I-K_kH)^T+K_kR_k^{\mathrm{eff}}K_k^T.
\]

**上游 KF-GINS 当前代码已经是 Joseph 形式。** 新外层采用这一数值做法属于实现要求，不能当创新，也不能在论文写成“我们修复了 KF-GINS 没使用 Joseph”。[S7]

## 6.3 不重复更新

每条 GNSS 测量有唯一 ID，只进入一次被选定的绝对位置更新。用于运动一致性监测的 GNSS 差分仅作观测管理证据，不再作为第二条独立测量重复注入。

不同时注入 `z_G`、`KF-GINS posterior(z_G)` 和由二者差分得到的伪量测。如果以后需要此类多量测设计，先推导共享信息和联合协方差，另开协议，不混入本轮。

## 6.4 因果时间与输出延迟

全部算法按测量时间排序，不使用真值修时。前端实际 scan-end pose 和传感器时间必须明确。

GNSS 历元处的 LIO 状态可选：

1. 用该时刻及以前已可用的状态/速度作短时传播，超过声明的最大外推间隔判不可用；或
2. 用最多一个扫描周期的有界缓冲，待后一个 LIO 状态已到达后做插值并按固定延迟回放更新。

P2 固定一种策略，所有比较方法共用；选择 2 时记录观测时间、可用时间和输出延迟，不能把使用下一帧数据的零延迟结果叫严格实时。不要为了对齐方便直接用完整未来轨迹的插值器而不记录延迟。

---

# 7. 候选增量机制：运动验证与渐进恢复

## 7.1 先实现必要的强对照

候选之前必须有：

- 固定/接收机标称协方差的 LIO+GNSS 位置 KF。
- 相同模型的 NIS 门控。
- 相同模型的 Huber 或等价规范鲁棒观测降权。
- 同样基础上的固定等待/固定恢复协方差衰减策略。

NIS：

\[
D_k=\mathbf r_k^T(HP_k^-H^T+R_k)^{-1}\mathbf r_k.
\]

阈值维数要与残差维数对应。主目标是水平可靠性，可先对水平 2 维做门控，垂向按共同策略更新；是否这样做须在开发前登记并对照保持一致。非高斯 GNSS、近似 Q/R 下，名义卡方门限不是已经校准的置信保证。

同样调 Q/R 下限、初始化和阈值预算，不能把没调好的原始 KF-GINS 默认参数当唯一对手。

## 7.2 两种不同的运动证据

短时运动一致性：

\[
\mathbf d_{k,W}=(\mathbf z^G_k-\mathbf z^G_{k-W})-
(\mathbf p^{L,a}_k-\mathbf p^{L,a}_{k-W}),
\]

`p^{L,a}` 为对齐并补偿到**天线中心**的 LIO 位置。`W` 为时间窗口，不是数组行号。仅使用过去与当前观测；GNSS 缺测不跨空洞伪造样本。

锚定偏差：

\[
\mathbf a_k=\mathbf z^G_k-
\left[\mathbf z^G_{\mathrm{anchor}}+
(\mathbf p^{L,a}_k-\mathbf p^{L,a}_{\mathrm{anchor}})\right].
\]

anchor 必须是先前经过持续验证的观测；其选择不读真值。隔离期间不跟着每个可疑 GNSS 更新 anchor，否则异常可以“洗白”。锚定不确定度随时间、路程和局部前端可信程度增长。

差分共用样本、有时间相关性，不能把多窗口统计量当独立证据相乘或声称精确卡方自由度相加。第一版作为可解释诊断分数与固定规则使用。

## 7.3 第一版状态机

| 状态 | 含义 | 动作 |
|---|---|---|
| `NORMAL` | GNSS 与局部运动通过当前检查 | 规范鲁棒位置更新；合格持续足够久才刷新锚 |
| `ISOLATED` | 数据无效或运动明显不一致 | 拒绝对应 GNSS，继续 LIO 传播；保存异常原因 |
| `OUTAGE` | 超过声明间隔无 GNSS | 仅 LIO 传播，Q 正常增长；不创建虚假 GNSS |
| `RECOVERING` | GNSS 重新出现且积累了所需验证证据 | 有限降权、渐进更新；失败则回到隔离 |
| `UNRESOLVED` | 当前证据无法区分全球偏移与里程计漂移 | 明确低可信，不自动跳成已恢复 |

状态由可用性、接收机信息、局部运动一致性及过去状态产生，**不由注入故障脚本的标签产生**。

恢复协方差可先采用一个简单、可消融的时间衰减：

\[
R_k^{\mathrm{eff}}=\gamma_k R_k,\quad
\gamma_k=1+(\gamma_0-1)\exp(-s_k/\tau_r),\quad \gamma_0\ge1.
\]

`s_k` 是已持续通过运动验证的恢复时间；不一致时停止累计或重置，规则必须明确。此公式本身是已有思想，不是主张新颖性的充分条件。真正要验证的是**由局部运动证据决定验证、刷新锚和重接入的具体作用**。

不同时随意缩放 K、裁剪残差、重置状态、缩放 R 四套机制。先只使用 R 降权与显式拒绝，保持公式和实现对应。

## 7.4 明确的可辨识性边界

如果 GNSS 在恢复后带有一个稳定常量偏移，而 LIO 增量正确，单纯差分可能仍完全一致。**不能用“运动一致”证明绝对位置正确**。

因此必做两项对照：

- 可信 GNSS 恢复，前期局部轨迹已积累一定漂移。
- GNSS 带持续位置偏差恢复，局部轨迹相对正确。

保留锚与其不确定度可提供有限判断，但长失锁后两种情况未必可区分。没有外部绝对参考时，不宣称消除所有持续偏差；无法区分时报告失效边界，不强行自信更新。

大创新也可能来自合法的漂移校正；单次 NIS 超阈值不一定是 GNSS 错。候选需要证明它比合理的宽松/恢复门限更好，而不是刻意让传统门控锁死。

## 7.5 LIO 自身不可靠时

第一版用可核实的基本可用性、配准残差/有效点数等日志做诊断；不能把一段运动轨迹的位置离散度当 LIO 估计协方差。

阈值只能在开发数据确定。若局部证据失效，停用它对 GNSS 的额外否决或标记不可用，采用事先规定的成熟鲁棒策略；不得在看到真值后指定“这段信 GNSS、那段信 LIO”。

不把可疑退化指标的另一个新算法同时列为本轮第二个创新点。

---

# 8. 基线与消融矩阵

## 8.1 必需的主比较

| ID | 方法 | 输入 | 用途 |
|---|---|---|---|
| B0 | F9P 位置 | F9P | 接收机参考水平；杆臂规则明确 |
| B1 | KF-GINS 正确配置 | ADIS+F9P | 传统 GNSS/INS 对照 |
| B2 | FAST-LIO2 | AT128+ADIS | 局部运动对照；全球主表仅初始对齐 |
| B3 | 基础分层 KF | LIO+F9P | 隔离“加入 LIO”本身的收益 |
| B4 | B3+NIS | 相同输入 | 基本异常拒绝 |
| B5 | B3+Huber/规范鲁棒降权 | 相同输入 | 更强鲁棒对照 |
| B6 | B5+固定恢复策略 | 相同输入 | 区分“等待/渐进恢复”与新证据的作用 |
| P | B5+运动验证的恢复管理 | 相同输入 | 候选新机制 |

只拿 P 比 B1 或 B2 不够；算法贡献优先比较 B4/B5/B6。不是强迫 P 在所有场景全面领先，而是明确目标事件收益与代价。

若 B6 已与 P 一样好，就不能把渐进恢复换个名字当新机制。至少一种最接近文献机制要做到可核对的实现/适配；完整系统无法复现时明确局部适配范围，不假冒官方复现。

## 8.2 必需消融

保持初始化、Q/R、输入、事件和主体滤波不变：

- 去掉局部运动验证，保留同样的恢复衰减。
- 去掉锚，保留短时一致性。
- 去掉恢复衰减，只保留同样拒绝/重新接入规则。
- 原 P 与简单短时阈值或固定等待相比。

不要为了“有消融”写十个随意因子。若某模块不是最终算法的一部分，删掉对应虚构消融。

## 8.3 可选而非主线前提

KF-GINS+NIS/Huber、毕设式后验融合、Mid-360 替换、OEM719 输入级别、LIO-SAM/GTSAM 新基线均只在时间许可和直接相关时加入。不要因此推迟主线的同传感器强对照。

---

# 9. 实验设计：自然退化 + 受控扰动 + 正常代价

## 9.1 开发与留出

- building00：开发路线。可看真值评价、拟合有限噪声参数、分析失败；明确不是独立结果。
- 可选 street00：开发控制路线；用于检查不必要降权的代价。
- parking00：第一次正式性能结果保留到 P5 freeze 后。提前做文件、时间、标定、标签覆盖检查及编译兼容检查可以；不得提前看算法精度图和挑参数。

第一次新数据元数据审计就检查：GNSS 有效样本数、初始化可行性、IMU/点云覆盖、参考重叠长度、是否有有意义的退化/恢复区段。数据不能支撑目标任务时，在性能开启前登记替换理由，不能等涨分失败后换测试场景。

## 9.2 自然场景划分

自然事件只由接收机状态、观测缺失、接收机标准差等**预先固定的非方法特定规则**或官方场景元数据产生，所有方法共用同一 event manifest。

不能用“本方法比 baseline 好的地方”定义退化区；不能用真值误差超过阈值筛选后只展示有利区间。基于真值的错误分析可以另标 post-hoc，但不能代替主评价。

如果接收机状态字段不足，就写“全路线性能 + 预注册受控异常试验”，不要假装已验证自然多路径故障类型。

## 9.3 受控扰动（只修改实验副本）

先在开发集确定有限协议；默认建议类别：

| 类别 | 建议范围 | 验证点 |
|---|---|---|
| 单/短簇跳变 | 水平 3/10 m；1–3 历元 | 瞬时异常抑制 |
| GNSS 缺失 | 10/30/60 s | 失锁传播、恢复行为 |
| 突然恢复正常 | 缺失后恢复原始 GNSS | 合法全球修正是否被长期拒绝 |
| 带持续偏差恢复 | 原始 GNSS 上加 3/10 m 常偏 | 运动一致性的盲区 |
| 缓慢偏移 | 有界线性渐变，幅度预声明 | 单次门控可能不敏感的情形 |
| 不注入异常 | 原始数据 | 代价与误伤 |

不把所有幅度×时长×方向做巨大笛卡尔积。默认每类固定 3 个不重叠起点、3 个预先固定种子或方向；重用相同起点/噪声于全部方法。若起点无实际 GNSS 或不足恢复时长，按预定规则跳到下一个合法点并记载，不看真值选最有利区间。

至少保存：原始 GNSS hash、派生数据 hash、开始/结束/幅度/方向/随机种子，以及应用条件。算法仅读派生观测，不读故障类别/时刻标记。

这些叫**真实轨迹上的人工 GNSS 压力测试**，不是实测多路径、真实信号遮挡或传感器现场故障。不能从 groundtruth 合成“完美 GNSS”后仍叫真实输入。

## 9.4 别把无 GNSS 期间的相同传播误当新机制

如果各外层方法只有 GNSS 更新策略不同，则彻底无 GNSS 时的传播式相同。失锁段差异可能来自失锁前状态，不代表恢复模块在缺测时新增了信息。

做“相同失锁初态”单元/控制实验检查这点。对原理没有新增的信息，不写额外贡献。

## 9.5 主指标与代价

在 P3 结束时、P4 大规模搜索前固定一个主要目标，默认：

> **退化—恢复事件窗口的水平位置误差积分或 RMSE，相对 B6 的变化；同时约束正常段误伤与完整路线可用性。**

主表同时列：

- 全路线水平 RMSE、P95、最大误差、可用输出比例。
- 目标事件水平 RMSE/P95、事件平均误差积分。
- 从恢复第一个 GNSS 到误差持续落入预定门限的时间；超时记未恢复，不删。
- 纯全球修正量 `||p_plus−p_minus||` 的最大值/分位数；不要把机器人真实运动量误称定位跳变。
- 正常 GNSS 的拒绝比例、误拒绝（只在有已知人工故障标签的试验中有完整定义）、损害事件数量。
- 实际 wall time、每个全球更新耗时和前端完整处理耗时；缓存后端重放与完整前端分开。

位置误差基准、时间采样、初始化排除段及垂向是否单列必须统一。F9P 低频位置不能无说明地插值成高频真值。

## 9.6 比较口径

用同一输出时钟的固定评价网格（建议 10 Hz，必要时 GNSS 历元单列），真值按允许间隔插值；禁跨真值空洞。所有方法保留运行失败/缺测时刻和覆盖率，不能靠只取成功交集隐藏失败。

聚合按序列/事件报告配对变化，再给宏平均；不要让最长路线掩盖另一条路线退化。相同连续轨迹的多个采样点和重复运行不是独立场景样本。

实用改进幅度没有统一录用门槛。事前可用 3–5% 作为继续探索的工程信号，但不是显著性或录用标准。少量百分比必须大于数值不稳定、初始化偶然性或参考精度的影响，并给绝对米值及代价。

---

# 10. 开发迭代与科学决策规则

## 10.1 不再预先锁死一个公式

P4 允许最多三轮**机制层面的**尝试：

1. `r01`：短时运动验证 + 固定恢复衰减，与 B6 比较。
2. `r02`：若 r01 误接收稳定偏差，用可信锚/长期偏差证据改一处；若问题是错误隔离，则改证据可用性与迟滞规则。两者选有证据的一种。
3. `r03`：仅在 r02 仍有明确、可解释的剩余问题时，做一个有界修订或简化。

每轮最多 12 组主要参数设置，整个候选搜索建议不超过 36 组。NIS/Huber/固定恢复等对照也给合理、可记录的相当调参机会；不做候选独享的大规模搜索。

一个参数组不能同时改传感器、初始姿态、时间偏移和方法。所有配置、失败与淘汰原因保留。

## 10.2 每轮必交的决策卡

```text
问题：开发数据的哪种行为需要修正？
证据：run_id、事件、曲线/逐历元记录。
假设：只改哪个机制，预期影响哪个指标？
最近邻：已有论文/强对照是否已有相同机制？
实现：变更文件与公式，新增参数。
结果：相对同传感器最强合理对照的作用和代价。
决定：保留 / 简化 / 否定 / 请求一个不可替代输入。
```

**对齐、外参、噪声单位等错误必须先修成共同实现，再重新跑所有受影响对照；它们不是算法增益。**

## 10.3 进入独立测试的条件

同时满足：

- 管线、对齐、真值、同一输入与评价通过检查。
- 最终候选在预先选定的目标事件上相对 B4/B5/B6 中合理强者有可重复收益。
- 正常条件无未解释的严重退化；若明确存在精度—平滑折中，完整展示曲线，不能称全面提升。
- 去掉新增机制后优势减弱，基本归因成立。
- 文献对照能说明与最接近机制的区别，或明确定位为小型应用系统贡献。
- 参数、Q/R、初始化、数据角色、事件、指标、代码 SHA 已冻结。

不要求所有指标都第一，也不允许仅挑一个指标赢。条件达不到时先交阶段报告和可运行 baseline；**不打开 parking00 性能，不自动生成“负结果研究”投稿稿，不自动开始无限新项目。**

## 10.4 打开留出数据后

一次冻结 run 可以包含全部事先登记的方法和全部场景，不是只允许跑一条命令。

运行错误可在保留失败并解释影响后修复，再重跑**全部受影响方法**；但若改变科学机制/参数，旧留出数据就成为开发数据，结论降级并需要新的留出支持。审计重放不等于再次盲测。

如果新数据不支持增量，保留真实结论，不从预先批量比较的几十行里事后挑一个新冠军改名为 proposed。

---

# 11. 分阶段任务、产物与时间预算

以当前日期 2026-10-11、官网列出的 10-15 全文截止为保守日程。截止具体时区、模板及 2026 作者规范需单独核实。[S11]

| 阶段 | 任务 | 最小产物 | 自动推进条件 |
|---|---|---|---|
| P0 工作空间 | 环境、Git、权限、资料、保护旧项目 | ENVIRONMENT.md、STATE、source lock | 无不可接受环境破坏 |
| P1 源码+数据并行 | KF-GINS demo、容器、数据下载/元数据、相关工作 | demo轨迹、DATA_MANIFEST、文献区别表、用户输入清单 | 数据与编译至少一条继续通路 |
| P2 两基线 | building00 FAST-LIO 与 KF-GINS，时间/坐标/初态验证 | 两真实轨迹、质量报告、失败及初始化说明 | 输出有物理意义，非仅 exit0 |
| P3 基础融合 | B0–B6，同输入同口径，协议固定 | BASELINE_REPORT、事件与指标协议 | 有目标问题与改进空间 |
| P4 候选开发 | r01–r03 有界迭代、必要消融 | METHOD_SPEC、决策卡、开发表 | 第 10.3 节全部满足 |
| P5 留出与代价 | freeze 后 parking00、扰动、实际计时 | 独立结果、全表、失败、审计 | 完整结果而非一定正结果 |
| P6 论文 | 机制叙事、图表、文献、6页稿与审查 | r01/r02…、claim map、PDF | 每个主张均有证据 |
| P7 交付 | 代码/配置/数据来源/恢复测试/版本归档 | DELIVERY、作者简报、resume命令 | 工程和研究状态分开结案 |

建议时限：

- 10-11：P0/P1，KF-GINS demo 与数据下载并行；能开始 building00 文本解算。
- 10-12 18:00 前：P2/P3 最小闭环。未达到时切换已记录的 GNSS/INS 备用或请求人工解决一个具体阻塞，不再同时堆三套环境。
- 10-13：P4，主机制与文献区别固定。不要拖到 14 日才发现 baseline 错。
- 10-14：P5 + P6，先完整结果，再全文。
- 10-15：人工审核和提交窗口；不在最后几个小时新增算法家族。

编译/下载等待时可写解析器、合成测试、相关工作、论文数据设置骨架。没有结果前可写方法草稿，但 Abstract/Conclusion 的数值与“有效”结论保持未填写。

---

# 12. 项目目录与代码修改边界

```text
workspace/
├── AGENTS.md
├── README.md
├── configs/
│   ├── project_intent.yaml
│   ├── sources.lock.json
│   ├── sensors/
│   ├── initialization/
│   ├── baselines/
│   ├── methods/
│   └── experiments/
├── third_party/                 上游固定版本/子模块；不复制进主方法目录冒充原创
├── patches/                     依赖适配、日志输出、核心修改分别存放
├── containers/                  Dockerfile、构建/运行脚本和镜像锁
├── build/                       编译产物，忽略
├── src/
│   ├── adapters/                格式、坐标、时间、杆臂
│   ├── alignment/               初始对准及合法公共变换
│   ├── fusion/                  基础三维KF
│   ├── observation_manager/    运动一致性、锚和恢复策略
│   └── evaluation/              唯一允许读取参考真值的主评价模块
├── scripts/                     可重复命令入口，无隐式猜目录
├── tests/                       单元、合成、接口、回放测试
├── data/
│   ├── raw/                    只读，原数据和许可证
│   ├── derived/                裁剪bag/格式转换；绑定原SHA
│   ├── manifests/
│   └── reference/              参考轨迹，与算法输入分离
├── cache/                      不可变LIO/输入缓存
├── outputs/<run_id>/           原始日志/轨迹/逐历元记录/配置/审计
├── freezes/<freeze_id>/
├── artifacts/                  轻量公开或私有证据；不含大bag/秘密
├── docs/
│   ├── GOAL_LIO_GINS_R1.md
│   ├── GOAL_STATE.json
│   ├── STATE_HISTORY.jsonl
│   ├── RUN_REGISTER.csv
│   ├── DECISION_LOG.md
│   ├── USER_ACTION_REQUIRED.md
│   ├── CURRENT_STATUS.md
│   ├── reports/
│   └── reference/              本科论文/受版权文献，本地保存不默认推送
└── paper/
    ├── working/
    ├── versions/r01/
    ├── versions/r02/
    ├── figures/
    └── submission_candidate/   仅通过最终审阅后复制，绝不自动提交
```

主融合第一版优先 Python/NumPy/SciPy 实现与独立测试，C++ 基线保持源码固定。确认机制有价值后，只有时延或部署确有需要才移植 C++，并逐历元对照两者。

KF-GINS 备用修改只在新 worktree/patch 中完成：`src/kf-gins/gi_engine.cpp` 的 `gnssUpdate()` 计算创新/R，`EKFUpdate()` 及 `stateFeedback()` 保留符号约定。当前 dz 为“预测−观测”、反馈采用减号，不照搬外层“观测−预测”写法造成双重反号。[S7]

无需改 UI、全项目格式化、升级所有依赖、换 Git 历史、重建用户其他研究仓库。

---

# 13. 必需测试清单

测试数量不是目标，下列行为必须实际检查：

## 13.1 数据与几何

- GPS week/SOW/UNIX 往返、周跳、重复时间与非正 Δt。
- 增量 IMU 不被二次积分；bag 原始速率与文本增量单位一致。
- FRD/FLU、ENU/NED、旋转与逆变换、xyzw 顺序；单轴位移例子。
- 非零杆臂的纯旋转：补偿后固定天线/IMU关系符合几何，不出现虚假平移。
- KF-GINS LLH `.nav` 与 local NED `.nav` 解析器互相误用时明确报错。
- 文件行排序变化、ID 重排后结果身份不变，缓存 hash 改变时拒绝复用。

## 13.2 滤波与因果

- 零噪声合成轨迹得到预期位置；静止不自行随机游走均值。
- Joseph 更新后矩阵对称、半正定；R 非正/NaN 拒绝进入求解。
- `policy=disabled` 精确复现共同基础KF；GNSS每条只更新一次。
- 所有 GNSS 删除时各策略同初态的传播一致。
- 给算法一个未来故障标签文件不能改变输出；算法模块不得 import 评价真值加载器。
- 打乱/删除未来观测不改变已输出过去结果；有固定延迟则按可用时间检验。
- LIO reset、GPS长断、恢复不足窗口、常偏恢复、漂移恢复、转弯、静止都不崩溃。
- recovery 不会无限等待却仍显示 NORMAL；错误锚不会被每个可疑GNSS刷成可信。

## 13.3 结果与回放

- 水平RMSE用 `sqrt(mean(eN²+eE²))`，不能平均两个方向RMSE冒充。
- 独立脚本从原始轨迹与参考重算，不只对汇总JSON“再加一遍”。
- 主图点、主表单元格和摘要数字可追到同一 run 与同一评价口径。
- 原始/鲁棒KF、同输入前端、初始化的比较公平性自动检查。
- 修改 proposed 文件不能影响 B0–B6 的配置或缓存。
- 运行失败/覆盖不足在汇总表可见，不被统一 dropna 静默清除。

---

# 14. 工作记录、归档与恢复

## 14.1 每次运行最小记录

`run_id = UTC时间 + 阶段 + 短配置hash`，新建目录，若存在立即报错而不是覆盖。

```text
manifest.json             run_id、用途、parent/source commit、输入/配置hash、数据角色
config_resolved.yaml      真正传入程序的完整配置
commands.jsonl            argv、cwd、起止时间、真实退出码
stdout.log / stderr.log   原始日志；不混入代理密码和授权令牌
trajectory.*              原始输出及坐标/参考点定义
per_epoch.csv             误差、GNSSID、残差、NIS、运动分数、状态、R倍率、修正量
metrics.json              相同口径汇总、失败与覆盖
figures/                  实际数据图及生成脚本/点数据
tests.json                真实测试执行与结果
interpretation.md         不超过1页的事实、判断、下一步
SHA256SUMS                完成后封存，后续补充另建receipt目录
```

失败 run 同样保存，`FAILED` 与 `BLOCKED` 不改成 `PASSED`。合成验证与真实数据实验分开命名，防止写作混淆。

## 14.2 大文件不复制，证据不丢

- 原 bag、模型、真值仅保存固定原件；所有实验引用 SHA/manifest。
- 参数搜索复用已验证 LIO 轨迹，不重复跑点云；后端时延不能因此冒称含前端。
- 默认不生成每轮完整点云地图；如需要展示，只生成选定基线的一个地图，生成后保留。
- CSV 可用压缩或 Parquet，保存 schema 和确定性导出方式。不要反复在 Git 中堆同一大JSON。
- **SHA清单不是备份**。必须区分 `local_preserved`、`remote_numeric_backed_up`、`raw_data_backed_up`；原始数据只有一份时明确写一份。
- 原始数据/版权论文/带学生个人信息的本科论文不默认推到公共仓库。数值、代码、配置、图表许可分别审查。
- 已有数据不能自动删除；磁盘不足先停止生成大文件、列出占用和可重建缓存，请用户决定。

## 14.3 Git

在新空间初始化独立 Git（若已存在先读状态）。使用 `research/lio-gins-r1` 工作分支，阶段 checkpoint；不要触碰旧 VPR 仓库。

上游使用锁定 clone/子模块和补丁；先记录 dirty diff，不能 reset 掉用户编辑。

只有用户已提供这个新项目的远程并授权推送时，才能 push；没有 remote 不擅自创建公开仓库。push 后记录本地 HEAD 与 remote SHA。避免在一个收据里让 SHA 自引用本次提交；“科学冻结SHA”和“随后归档提交SHA”分开。

## 14.4 状态与断点

可变索引：`GOAL_STATE.json`、`CURRENT_STATUS.md`、`RUN_REGISTER.csv`。每次更新附加 `STATE_HISTORY.jsonl`，历史实验目录不改。

状态字段至少包括：

```json
{
  "goal_id": "LIO-GINS-R1",
  "phase": "P0",
  "execution_status": "not_started",
  "pipeline_ready": false,
  "development_effect_supported": false,
  "test_performance_opened": false,
  "independent_effect_supported": false,
  "novelty_status": "unverified",
  "paper_ready_for_human_review": false,
  "formal_submission_ready": false,
  "selected_architecture": "A_lio_raw_gnss_outer_kf",
  "latest_run_id": null,
  "freeze_id": null,
  "blocked_on": [],
  "next_action": "audit_workspace"
}
```

中断后先读取状态、当前Git/进程与最后日志；正在运行的任务不重复启动。长实验用可恢复的进程/会话，记录PID与日志；不要只发一句“后台继续”而没有真实进程。

## 14.5 文档要为研究服务

每阶段一份短报告，主要详细数据由脚本产生。不要为了凑“完整历程”生成大量重复PDF、几十份同义总结。

最少维护四个入口：`CURRENT_STATUS.md`（进展）、`DECISION_LOG.md`（决定）、`RUN_REGISTER.csv`（证据）、`USER_ACTION_REQUIRED.md`（确实需要用户做的事）。旧失败报告标明历史时间与后继报告链接，避免“数据已取得但首页仍说阻塞”。

---

# 15. 权限、预算与人工协同

## 15.1 可自主做

项目目录内写代码/测试/脚本；独立虚拟环境；已有容器运行；公开数据下载；固定版本开源代码读取；不花钱的常规编译与CPU实验；本地论文草稿；已获授权的目标分支推送。

## 15.2 需人工确认

安装/启动需sudo的新系统服务、加入 docker 组等权限提升、宿主驱动或ROS/网络变更、删除旧数据、超过空间预算的大下载、账号注册/登录、付费云GPU、创建公共remote、对外发邮件、投稿/版权/作者列表。

不将密码写进脚本或标准输出；不读取用户无关邮件/文件；不把整个home挂给构建容器。

## 15.3 默认资源预算

先实测磁盘；不假设400GB仍全部空闲。建议至少保留80GB安全余量，若容量小于预期则重新计算下载上限。首轮只申请 building00/parking00，总量以上游实际文件列表为准，不声称已经知道每个bag体积。

构建并发默认不超过4，避免内存耗尽；正式计时不并行下载/解压/跑其他重实验。只读缓存重放允许批量，但不要同时开多个雷达里程计竞争CPU。

无外部数据时可以推进KF-GINS demo、接口、文献、测试，不能以无数据直接写出“完整验证通过”。

## 15.4 请求用户/伙伴团队的一次性清单

1. building00、parking00 的 bag 与上述文本。
2. local NED 真值原点/坐标转换说明。
3. KF-GINS 对该机器人数据的已知初始化配置/建议IMU参数（如果有）。
4. AT128/ADIS 基线输出的参考点与时间语义是否有补充说明。
5. WinTA-GIL/最近邻工作的可访问论文或代码线索，明确本项目区别。

这些不是全部必须由人手动提供：已有公开文档能解决的先解决；只有确实缺失的条目出现在行动清单。

---

# 16. 六页论文的组织与写作规范

## 16.1 论文只讲一个成立的问题

研究过程可以经历多轮失败，但最后六页不是 Codex 执行日志。用如下逻辑组织：

**具体运行问题 → 已有策略局限 → 增量机制 → 同传感器对照 → 目标场景改善 → 正常代价与边界。**

不要把版本号、运行了多少参数、SHA数量和“全自动生成”当科学贡献。复现信息放短节/附件/仓库。

## 16.2 预算（含参考文献的保守6页）

| 内容 | 页数预算 | 内容重点 |
|---|---:|---|
| 标题、摘要、关键词 | 0.45 | 研究问题、机制、实际核心数值 |
| Introduction | 0.65 | 异常修正/恢复的具体矛盾和2–3条有证据贡献 |
| Related Work | 0.50 | LIO全球融合、鲁棒更新、恢复/窗口一致性最近邻 |
| Method | 1.35 | 局部传播、观测管理、因果性、约束与复杂度 |
| Experimental Setup | 0.65 | 数据、真值依赖、初始化、事件、基线、指标 |
| Results | 1.25 | 全路线、事件、消融、正常代价、耗时 |
| Discussion/Conclusion | 0.35 | 适用范围和不能解决的情况 |
| References/必要披露 | 0.80 | 核实引用与合规声明 |
| **总计** | **6.00** | 按正式模板微调，不缩字体作弊 |

官网目前列出最多6页、全文10月15日；2026正式模板、匿名、参考文献是否计页、时区与出版要求仍需从投稿页面/组委会确认。IEEEtran 仅可作工作模板，不宣称已经确认就是2026官方模板。[S11]

## 16.3 正文最值得保留的图表

- Fig.1：机制级框图。已有局部前端、局部传播、观测监测、恢复更新、输出；虚线单独画离线评价，不把真值箭头画进算法。
- Table I：序列、输入、参考生成、时长/有效覆盖；初始化明确。
- Table II：全路线同传感器比较及GNSS/INS对照。
- Fig.2：事先固定选择规则的一个完整“退化—失锁—恢复”事件，显示真实误差、GNSS创新/运动一致性、状态、修正量。展示完整事件，不截一段最漂亮的小图。
- Table III：消融与恢复指标，包含正常代价。
- 时延可并入表；空间不足把次要参数网格放仓库。

图表来自脚本和真实数值，禁止用生成式图片画出“真实轨迹结果”。概念框图可以原创绘制，但不替代数据。

## 16.4 英文摘要骨架（占位符不可进入投稿）

> Intermittent and degraded GNSS observations can disturb the global consistency of otherwise continuous LiDAR–inertial motion estimates. This work investigates a hierarchical localization framework with motion-verified global updates. The framework uses local displacement evidence and a persistent observation-management state to regulate the admission and gradual reintegration of GNSS positions, while retaining the underlying local odometry and Kalman prediction models. We evaluate the method on [datasets/routes] using [reference and initialization protocol], and compare it with fixed-covariance fusion, innovation gating, robust weighting, and a matched fixed-recovery baseline. In [predefined target conditions], the proposed mechanism changes [primary metric] from [a] to [b], with [normal-condition cost] and [runtime]. Ablation results attribute [supported effect] to [specific component]. The results support [bounded conclusion]; [remaining failure mode] is not resolved.

如果无新增机制收益，不能自动把这段改成一个“新框架显著提高性能”的稿子。若改进成立，摘要可以写 `we propose`，但贡献幅度与范围保持一致。

## 16.5 写清楚来源，但不把文章写成仓库使用教程

Implementation 中应有明确一句：

> FAST-LIO2 supplies local LiDAR–inertial estimates, and KF-GINS serves as the GNSS/INS baseline. Our contribution is confined to the [precisely defined observation-management mechanism], rather than to either underlying estimator.

根据真实最终架构修改。若以后改为KF-GINS内观测管理，则准确写 KF-GINS 是实现基础，而不是仍称独立对照。

“框架”可以是组织方式；**新增价值必须落实到公式、规则及对照结果**。不能用模糊的新术语隐藏本质上没有改变的方法。

## 16.6 版本与披露

`paper/working/` 可编辑；每次主要评阅或结果变更保存 `paper/versions/rXX/`：tex/bib、PDF、config/run绑定、图表数据、CHANGELOG、claim-evidence map。

旧稿和旧结论不删；新稿不同数值要指出改变来自修bug、改变协议还是新增数据。

投稿稿剔除“作者待批准”“AI仍需验证”等工作提醒，把它们留在内部审核清单；但保留真实局限与实际AI使用披露。作者、单位、基金不得生成。IEEE出版适用时，AI生成文本/图/代码的使用按官方政策在致谢中说明工具、使用范围和程度；最终按本届出版方规范核对。[S12]

---

# 17. 最终验收：给用户什么

## 17.1 工程交付

- 从干净clone与已下载原始数据开始可复现的README。
- 固定upstream commit、容器/编译环境、转换器、基线、候选及测试。
- 一键按序列运行与一键只重放后端的入口，说明二者差别。
- 全部实验、负结果、冻结快照、文件身份、归档恢复验证。

## 17.2 科研交付

- 主问题和最近邻工作区别，一页即可。
- 同输入强基线与消融表，原始/扰动清楚分开。
- 独立测试的第一次开启记录、完整结果与局限。
- `CLAIMS_SUPPORTED.md`：逐条列支持/不支持/尚不确定。
- 不通过时具体写清哪个实验不支持哪个机制，而不是一句“创新不足”。

## 17.3 作者交付

- `AUTHOR_BRIEF_ZH.md`：2–3页以内中文解释，说明输入输出、核心公式、真正改了哪里、改善在哪个场景、失败在哪。
- 10个答辩问题与简要答案，必须对应本项目事实。
- 有证据时交完整英文6页内稿；没证据时交方法与实验草稿，不把自动完成PDF视为成功。
- `RESUME.md`：当前状态、最近run/commit、未完成项、单条下一步命令。

## 17.4 完成状态

使用以下之一而非全部称成功：

- `PIPELINE_READY`：基线与评价可靠，尚无方法结论。
- `DEVELOPMENT_GAIN`：开发证据支持，未打开留出。
- `INDEPENDENT_GAIN_WITH_LIMITS`：有独立支持且范围明确，待学术/格式审核。
- `NO_ADDITIONAL_GAIN`：新增机制未超过匹配强基线。
- `BLOCKED_USER_INPUT`：具体缺文件/原点/权限/账户。

独立增益也不是“已录用”。本项目应把可投稿的证据做到尽可能扎实，而不是承诺审稿结果。

---

# 18. 来源与核查记录

以下为本计划使用的原始来源；执行时保存访问日期、版本和必要摘记，不把来源全文复制进公共仓库。

- **[S1] i2Nav-Robot 官方README**：传感器、话题、时间/格式、F9P SPP、参考生成、下载、使用限制。<https://github.com/i2Nav-WHU/i2Nav-Robot/blob/2ffdca6d56e6432d4daf27c070e570171548f32d/README.md>
- **[S2] 官方适配 FAST-LIO2 配置**：AT128+ADIS16465。<https://github.com/i2Nav-WHU/i2Nav-Robot-Baseline/blob/6c602f8d974fbe5be1183771541c90057e9e3bb6/FAST_LIO/config/i2nav.yaml>
- **[S3] KF-GINS 官方文档及论文**：<https://github.com/i2Nav-WHU/KF-GINS/blob/8291a93e49de513fe9d21f819500d39082ded611/README_CN.md>；Niu et al., `KF-GINS: an open-sourced software for GNSS/INS integrated navigation`, GPS Solutions 29, 202 (2025), <https://doi.org/10.1007/s10291-025-01967-w>。
- **[S4] 官方序列定义**：<https://github.com/i2Nav-WHU/i2Nav-Robot/blob/2ffdca6d56e6432d4daf27c070e570171548f32d/sequence_detail/i2nav_robot.json>
- **[S5] 官方bag校验值**：<https://github.com/i2Nav-WHU/i2Nav-Robot/blob/2ffdca6d56e6432d4daf27c070e570171548f32d/sha256sum/sha256sum.json>
- **[S6] 官方标定**：<https://github.com/i2Nav-WHU/i2Nav-Robot/blob/2ffdca6d56e6432d4daf27c070e570171548f32d/calibration/calibration.yaml>
- **[S7] KF-GINS gnssUpdate/EKFUpdate 源码**：<https://github.com/i2Nav-WHU/KF-GINS/blob/8291a93e49de513fe9d21f819500d39082ded611/src/kf-gins/gi_engine.cpp>
- **[S8] WinTA-GIL**：Feng et al., `WinTA-GIL: Windowed Trajectory Alignment for GNSS-IMU-LiDAR Heading Refinement in Intermittent Signal Environments`, arXiv:2607.04879，摘要页注明 accepted to IROS 2026；已访问摘要和HTML方法部分，不在本计划中宣称复现实验。<https://arxiv.org/abs/2607.04879>；<https://arxiv.org/html/2607.04879v1>
- **[S9] 相关分阶段自适应GNSS/INS工作**：Shan et al., `Robust Urban INS/GNSS Positioning Under Degraded GNSS Conditions Using a Dual-Adaptive Cubature Kalman Filter`, Electronics 15(10), 2064 (2026)，已核对其恢复阶段调节描述，执行时补全公式级对照。<https://doi.org/10.3390/electronics15102064>
- **[S10] ROS Noetic EOL 官方说明**：<https://discourse.ros.org/t/ros-noetic-end-of-life-may-31-2025/43160>
- **[S11] UPINLBS 2026 官网**：<https://upinlbs2026.com/>。本次可核实6页上限和10月15日全文截止；`/submission` 未成功取得完整作者说明。最终稿日期与会议日期顺序异常待核实，不能据此自动延期。
- **[S12] IEEE AI及投稿政策**：<https://conferences.ieeeauthorcenter.ieee.org/author-ethics/guidelines-and-policies/submission-policies/>
- **[S13] FAST-LIO2 原方法**：Xu et al., `FAST-LIO2: Fast Direct LiDAR-Inertial Odometry`, IEEE T-RO 38(4), 2053–2073 (2022)，<https://arxiv.org/abs/2107.06829>；代码 <https://github.com/hku-mars/FAST_LIO>。
- **[S14] 无雷达备用数据**：<https://github.com/i2Nav-WHU/awesome-gins-datasets>。只支持GNSS/INS，不据此声称三传感器实验。
- **[S15] 用户本科论文**：`基于多传感器融合的机器狗自主定位与导航系统研究`，第3章与图3.1/3.4作结构参考。实验数值不作为本目标的新证据；PDF本地保留，不默认公开。

# 19. 现在开始

第一轮执行只要求完成 P0/P1 的可启动部分：**保护现有空间 → 登记目标 → 跑 KF-GINS demo → 构建 FAST-LIO2 隔离环境 → 列出并取得最小数据 → 保存真实报告**。

数据已齐全且检查通过，可继续 P2/P3；不需要等用户再发同样命令。缺数据时继续无依赖任务并给出一次性清单，不编造结果。直到开发证据充分，再冻结和开启 parking00 的性能评价。
