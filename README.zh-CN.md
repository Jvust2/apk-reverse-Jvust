<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
    <img src="assets/banner-light.svg" alt="apk-reverse" width="100%">
  </picture>
</p>

<p align="center">
  <a href="README.md">English</a> · <b>简体中文</b>
</p>

<p align="center">
  <a href="https://github.com/newliver666/apk-reverse/stargazers"><img src="https://img.shields.io/github/stars/newliver666/apk-reverse?style=flat-square&label=stars&color=49454F" alt="stars"></a>
  <a href="https://github.com/newliver666/apk-reverse/network/members"><img src="https://img.shields.io/github/forks/newliver666/apk-reverse?style=flat-square&label=forks&color=49454F" alt="forks"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/newliver666/apk-reverse?style=flat-square&color=49454F" alt="license"></a>
  <img src="https://img.shields.io/badge/python-3.9%2B-49454F?style=flat-square&logo=python&logoColor=white" alt="python">
  <img src="https://img.shields.io/badge/platform-android-49454F?style=flat-square&logo=android&logoColor=white" alt="android">
  <a href="https://github.com/newliver666/apk-reverse/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/newliver666/apk-reverse/ci.yml?style=flat-square&label=ci&color=49454F" alt="ci"></a>
</p>

<p align="center">
  <a href="#它擅长什么">能力</a> · <a href="#结构">结构</a> · <a href="#安装">安装</a> · <a href="#环境要求">环境要求</a> · <a href="#先读这个">失败目录</a> · <a href="#范围">范围</a> · <a href="#仓库维护">维护</a> · <a href="#免责声明">免责声明</a>
</p>

# apk-reverse

面向 Android APK 逆向工程、去臃肿、去广告、外科式 dex 补丁、重打包，以及运行时/服务端分析的 Agent Skill。

它是一个 **skill**，不是教程：它是写给 agent（Claude Code、Codex，或任何支持 Agent Skills 格式的 harness）在工作过程中加载的，因此按 progressive disclosure（渐进披露）来组织——一份简短、面向决策的 `SKILL.md`，只在某一步真正需要时才加载的详细 references，以及可直接运行的参数化脚本。

## Agent 应当如何使用它

`SKILL.md` 刻意写成一份**带 gate 的流程**，而不是建议，因为观察到的失败模式并不是无知——而是模型把整份文档读完、表示认同，然后照样从第一性原理重新推理一遍。

所以正文里有四样东西是用来**执行**的，不是用来读的：

- **四条覆盖规则（R1–R4）。** 当它们与当前计划冲突时，在证据推翻它们之前，以它们为准。
- **一份症状索引。** 每一行都是已经付过代价的失败。**命中一行就是停止信号**：在你跑下一条命令之前加载那个文件，而不是在又试了几次之后。绕过已经记录在案的已知症状继续推理，就是同一批小时被花掉两次的方式。
- **四个 gate（G1–G4）**，每个都是一个动作加一条通过标准。「我理解这个思路」并不能通过 gate。它们存在的意义是让分类、环境真相和对照构建发生在第一次打补丁**之前**，而不是在第三次失败之后。
- **一条两击规则和若干停止条件。** 同一形态的失败出现两次，说明错的是模型，不是参数。一个已经失败过两次的假设再出第三个变体，就是回合葬身之处。

另外还有一样在结尾、应当被**扣住**的东西：**「done」**有定义（六项）。一份干净的日志不在其中。少于六项全部达成，就只是一个检查点，应当作为检查点汇报，并说明还剩什么。

如果你是正在读这段的 agent：成本最低的第一条命令是 `python skills/apk-reverse/scripts/doctor.py`。它会告诉你这里存在哪些工具、哪些脚本真的能跑，以及环境里是否已经有什么东西在污染你的测量结果。

## 它擅长什么

- **快速**判断一个需求在客户端是否本来就做不到，而不是把几小时烧在一个由服务端强制执行的付费墙（paywall）上。
- 在任何工作开始之前先确定**交付物必须是什么形态**——一个免 root、自包含的产物与「让它在你这台机器上能跑」是两个不同的问题，混淆这两者是这个领域里最昂贵的漂移。
- 为给定改动选择**最安全的补丁层**，并避开那些会把 app 弄坏的层。
- 抓住那种「看起来成功」的重打包失败：app 安装、启动、渲染都完美，但**每一个签名请求都被拒绝**，因为客户端是从自己的签名证书推导请求签名密钥的。
- 把**你自己的错误与 app 或服务端的问题区分开**——限定在某个功能上的失败（登录、注册、支付）常常是某一条代码路径上的 TLS/证书问题，而不是你刚做出来的补丁的后果。设备状态、失联的 device server 和时钟漂移会以同样的方式伪装成同类问题。
- 确认**实际执行的是哪个架构、哪个库**，而不是相信 manifest 里带了什么或设备自称什么。
- 处理**加壳/加固目标**：识别壳、脱壳，并把内存 dump 还原成一个打过补丁、可安装的 APK。
- 处理一个**故意终止进程的加固库**——包括那种刻意崩溃的形态（`fault addr 0x4`），它看起来和普通的空指针解引用 bug 一模一样；以及「把它失效化，但绝不要让它*不返回*」这条规则，它决定修法是生效，还是以完全看不出与原因有关的方式冻住整个 app。
- 知道**该伸手去拿哪些工具，以及每个工具在哪里说谎**——包括那些只以 GUI 形式存在的工具，此时应当请求人类介入，而不是悄悄换用一个更弱的方法。
- 让打过补丁的构建**保持**打过补丁：失效化版本检查、强制升级弹窗和自更新安装器，使这份成果无法被远端一键关掉——同时认出那个能在版本号毫无变化的情况下悄悄把它撤销的热更新/远程配置通道。
- 把**客户端侧的登录闸门**（可打补丁）与**账号维度的资源**（为空，因为服务端没有东西可答）区分开；并且知道伪造一个 session 所产生的状态比保持未登录更糟。
- 让**长时间任务保持诚实**：一份实时记录、分级结论、校准过的超时和有界等待，使进展不会丢失、同一个错误不会被犯两次。
- 避开那些会产出「构建完美、运行即死」的 APK 的具体错误。
- 当 APK 不是可选项时，决定**交付物应该是什么**——被多个独立检查拒绝的重打包是*受阻*，不是*昂贵*；回落阶梯是系统级模块、本地 RPC 服务，或一份明确写出边界的诚实报告。
- 分辨真实内存 dump 与**抽取壳骨架**，并知道哪条恢复路线适用——包括当 `frida` 本身被拒绝时走 root 侧 dump。这次测量能看见什么、看不见什么，写在 `skills/apk-reverse/references/advanced-unpacking.md`。
- 当逆向的成本高于调用时，**调用例程而不是逆向它**：在宿主上做模拟执行，或把一个活函数通过 Frida RPC 服务化。
- 当一个 native 函数被 OLLVM 碾平成状态机时，去读**指令级执行证据**——包括在真实设备上实测到的 Stalker 反咬的两种方式。
- 认出**用户态 hooking 根本够不到那个检查**的情况（裸 `svc` 系统调用、`init_array` 早期检测）、上下相邻层实际能做什么，以及什么时候继续升级是错误答案。
- 处理**非 REST 的协议**——无 schema 的 protobuf、gRPC、QUIC/HTTP3——以及无视系统信任库的 native 侧证书固定（pinning）。
- **直接在手机上工作**：MT Manager 的编辑/重打包/签名流程及其 APK MCP 接口、LSPosed Manager、设备上的数据检查，与 PC 工具链并用，而不是用它来替代 PC 工具链。
- 在花几小时去追一个在进程生命周期内任何时刻都不存在的「解密 DEX」之前，先把 **Java2C 与抽取壳区分开**——代码已经被编译进 `.so`。
- 处理以 **split APK / App Bundle 集合**形式到来的构建：从设备上取出该集合、用一个 keystore 为每个成员签名以便 `pm install-multiple`，或在合法时把 code/native 成员合并成一个独立 APK。
- 用已知明文差分处理一个**真实的 Dex VMP**——哪些环节可以自动化、哪些不能，一个编译出来的 fixture 能触达什么、不能触达什么，以及如何*证明*一张推导出的私有 opcode 表，而不是断言它。
- **在发表所学的同时不发表目标**——一个带上下文报告目标身份形态的扫描器、一份明确列出*不得*脱敏内容（工具、库、协议字段、CVE、加固产品、公开 crackme）的清单，因为把这些脱敏会毁掉可复用的那部分；以及能 gate 住一次提交的退出码。
- 在重复本仓库已经收敛过的劳动之前先读**先例**：记录中正向的那一半，含路线及其死路、对每条断言的分级，以及该案例指明要回写的文件。

## 结构

`SKILL.md`、`references/` 与 `scripts/` 都在 skill 目录 `skills/apk-reverse/` 内。仓库根目录下的一切是跨 skill 共享的维护工具，不属于已安装的 skill。

```
SKILL.md                  带 gate 的流程，不是背景阅读材料：
                          how-to-use  -> 四条覆盖规则（R1-R4）
                          症状索引（命中一行即为停止信号）
                          四个 gate（G1-G4，带通过标准的动作）
                          十三个分类问题
                          工作流，带每一步的跳过条件和一条两击规则
                          「done」的含义  ->  停止条件  ->  约束  ->  索引
references/               按需加载，每个文件一个主题
  recon.md                    识别壳、SDK、代码位置、篡改检查；脱壳
  server-config-and-updates.md
                              「广告」最常见的那种形态，也是通常被误诊的那种：
                              服务端提供 UI，客户端负责渲染（启动屏、弹窗、
                              公告、tab 集合）。证明它的两层抓取、如何按
                              data class 保留的字段名找到配置 DTO、为什么
                              你要补的是决策而不是数据、「移除」的范围如何界定，
                              以及远端重新启用 / 配置缓存持久性
  byte-level-patching.md      等长字节编辑：为什么它优于方法重建（实测）、
                              如何在不刮 listing 的情况下定位一条指令的精确偏移、
                              会让解码失步的指令宽度陷阱、把分支失效化还是重定向它、
                              dex 头完整性字段的顺序，以及校验器的 move-result 规则
  packers.md                  加固目标：拒绝信号、用单变量测试测量校验边界、
                              选择 native 宿主
  code-virtualization-and-custom-linkers.md
                              「已加壳」与「干净」之间的那一层：整个类被变成
                              `native` 声明、SONAME 与文件名不匹配的私有加载器、
                              内嵌的自解密 payload、一个 Java 层「签名杀手」在日志里
                              报告成功而 native 检查却在杀你。留还是删的死锁、
                              如何把*检查器*与*实现*分开，以及那条不做任何
                              失效化就终结它的字符串重定向技术
  framework-runtimes.md       Flutter / React Native / Unity：UI 归哪一层所有，
                              以及在没有符号时怎么找逻辑（字符串编码陷阱）
  dart-aot.md                 Dart AOT 深入：版本钉定与构建一个匹配的反编译器、
                              对象池与引用索引、寄存器/布尔约定、
                              识别业务逻辑的三种签名、定位、打补丁。
                              开篇先讲它所依赖的 snapshot 解码前端（aotopsy 或
                              blutter），因为 pool 列表是输入，不是本 skill 自己产出的东西
  native-and-so.md            .so 宿主、DT_NEEDED vs JNI_OnLoad、重定位限制、
                              免重定位的 bootstrap、用 native 替换 Java 方法，
                              以及*实际加载并执行*的是哪个 ABI/库
  native-tamper-and-suicide.md  加固库如何杀掉自己的进程：可见的机制、
                              如何判断实际触发的是哪一个、如何定位现场、
                              伪造的 section header、由 PT_GNU_EH_FRAME 推出的
                              函数边界、扫描器陷阱，以及安全地失效化
  detection-and-anti-analysis.md  当 app 反击，或工具在这里跑不起来时：把检测与
                              环境损坏区分开、按成本而不是按升级来决策、认出
                              动态分析根本无效的环境，并把「挡住我的分析」这个问题
                              与「挡住交付物」分开
  toolchain.md                该装什么、如何非交互地调用它、哪些工具只有 GUI、
                              版本对齐陷阱、离线工作、**「不在 PATH 上」不等于「没装」**，
                              以及该用哪个签名器
  long-task-discipline.md     实时记录、结论分级、漂移控制、超时与等待校准、
                              交付物形态漂移、你从未看过的截图、
                              长上下文衰减、交接
  ad-removal.md               广告分类学、包装层映射、回调陷阱、全局闸门、验证
  updates-and-forced-upgrade.md  让打过补丁的构建活下去：定位版本检查、
                              两层补丁（把例程 no-op、把比较失效化）、不能碰的东西
                              （manifest 版本、安装器权限、host 阻断）、
                              自更新与热更新/远程配置通道、验证根本没有发出任何版本请求
  account-gates.md            登录墙、强制手机绑定、游客模式：把客户端侧闸门
                              （可补）与账号维度资源（不可补）区分开、为什么
                              伪造 session 比保持未登录更糟，以及重装后
                              无法避免的登录态丢失
  signature-derived-keys.md   当 app 自己的签名证书被当作密钥材料时：
                              检测用 grep、为什么离线提取不可靠、
                              先硬编码再验证的流程
  membership-and-limits.md    服务端 vs 客户端权威；什么可补、什么不可补
  server-api.md               探测 app 的 API；证明闸门归谁所有
  tls-and-cert.md             功能维度的网络失败：过期证书、双信任链
  third-party-builds.md       在信任一个「破解版」/「魔改版」APK 之前审计它
  dex-patching.md             补丁层对照表 + dexlib2 技术深入
  patch-audit.md              证明一个补丁*落地*了并且*合法*：长度 vs 字节
                              比较、等长替换的盲区、校验器层面的合法性
                              （move-result 相邻性）静态检查、文本匹配式
                              补丁陷阱，以及如何报告一个缺失的补丁
  repack-and-sign.md          重打包规则、解包与重打包、签名、安装后隐患
  runtime-data.md             DataStore / SharedPreferences / SQLite / protobuf；app 何时
                              会改写你的编辑，以及解码一个看起来像加密的值
  dynamic-frida.md            Frida 配置、版本钉定、四层探测、hook 策略
  environment.md              设备/模拟器配置、root、ADB、离线设备、日志信号、
                              模拟器 console 控制与恢复、preflight、看一眼屏幕
  verification.md             主张阶梯；「done」的含义
  desensitization-and-leak-scans.md
                              发表纪律：什么必须脱敏、什么必须保留、
                              不得匿名化的清单、泄漏扫描器及其退出状态，以及
                              入口文件本身就是一处提示词暴露面
  precedents/                 正向案例库：含死路的路线、每条断言的分级、
                              实测到的坑，以及回写清单
  routing.md                  按需清单：每个 reference 及其加载时机、每个
                              script 及其用途，以及症状索引的镜像
  rasc-and-droidsaw.md        ASC 索引器的 Rust 重实现：实测加速比与
                              完全一致的类集合、它会静默丢掉方法体的 enum 形态，
                              以及如何构建与验证它
  evidence-summary.md         随 skill 一起发布的浓缩版：能力、一行结论、
                              强度，以及你在已安装副本里实际能打开的证据

  ../evals/                   也不是 spec 目录，而是 Agent Skills 指南推荐的
                              位置：`evals.json` 存放本 skill **尚未**运行过的
                              带 skill / 不带 skill 用例，运行方法写在文件里
  ../evidence/                不是 spec 目录：上面 evidence summary reference 的
                              机器可读配套文件 —— `capability-matrix.json`（同样的行、
                              更多字段）、`tested-tool-versions.json`（版本及每个版本背后的
                              探测）、`known-limitations.md`（面向安装者的限制清单）。随 skill
                              一起发布，使已安装的副本不需要仓库就能回答「这一条验证过吗、
                              强度如何」
  pitfalls.md                 失败目录 —— 构建之前先读
  advanced-unpacking.md       dump 拿到了但方法体是空的：按平凡方法体比例做
                              抽取壳诊断、FART 式主动调用以及为什么它的经典 hook
                              在 Android 12-16 上失效、code_item 拼接、当 frida
                              本身被拒绝时的 root 侧 dump，以及诚实的 VMP 边界
  lsposed-and-modules.md      重打包被拒绝，那就交付一个系统级 hook 模块：模块解剖、
                              无 gradle 的构建链、作用域配置与如何验证注入，
                              以及 Java 模块够不到的那一层
  emulation-and-rpc.md        调用例程而不是读它：Unidbg/Unicorn 模拟及其
                              环境填充成本，对比把活函数通过 Frida RPC 服务化
  native-dbi-and-deobfuscation.md
                              OLLVM 形态、Frida-Stalker trace、trace 到 CFG 的路线、
                              Stalker/QBDI/模拟的取舍，以及两条实测边界（一次
                              不产生任何事件的 follow，和一次因 follow 热 libc 导出而崩溃）
  protocol-reverse.md         无 schema 的 protobuf、从反编译代码恢复 schema、gRPC 帧
                              抓取、QUIC/HTTP3 的限制，以及 native 侧证书固定
  kernel-and-environment-hardening.md
                              用户态 hooking 可证明够不到检查：裸 `svc`、init_array 早期
                              检测、每种 root 方案隐藏了什么、带版本闸门的
                              内核路线图，以及什么时候停止升级
  on-device-tooling.md        直接在手机上工作：MT Manager 的编辑/重打包/签名及其 APK MCP、
                              LSPosed Manager、Termux+frida、设备上数据检查
  java2c-and-jni-sinking.md   Java2C 与 JNI sinking，最容易与抽取壳混淆的两种加固
                              形态：区分落地壳 / 抽取壳 / VMP / Java2C / JNI sinking
                              的那张表、为什么代码在 `.so` 里而*永远*不在 dump 出的 dex 里，
                              以及为什么 `Java_*` 符号搜索会一无所获（动态注册、
                              `-fvisibility=hidden`）
  split-apk.md                App Bundle / split APK 集合：集合是什么、如何从设备拉取、
                              合并成一个 APK 还是把整个集合作为一个单元签名、安装拒绝
                              及其各自含义，以及如何从拉取的集合做出一个可安装的 fixture
  vmp-differential-analysis.md
                              针对真实 Dex VMP 的已知明文差分：哪些环节可以
                              自动化、哪些不能（上传是瓶颈）、一个编译出的
                              fixture 能覆盖到什么程度、如何*证明*一张推导出的私有
                              opcode 表、smali 生成，以及这条路线何时关闭
  coverage-and-limits.md      把主张阶梯用在 skill 自己身上：每个已覆盖条目背后的
                              证据、本 skill 不随附的依赖，以及从未实际演练过的东西
  handoff-boundaries.md       本 skill 在哪里结束、另一门学科在哪里开始：JNI 形态
                              对照表、壳与加载器的分界，以及「已核实」对四种
                              交付物形态各自意味着什么
scripts/                  参数化、与路径无关
  doctor.py                   先跑这个：能力报告 + 每个脚本的可运行性，发现
                              安装在 PATH 之外或作为可运行 jar 存在的工具，并暴露
                              会污染实验的环境事实（时钟偏移、残留的
                              adb forward / proxy、设备侧已在运行的 frida 进程）
  dexutil.py                  无依赖的 dex 读取器：结构遍历 + 精确指令
                              解码、dex 头重算/校验（正确的 checksum/signature
                              顺序）、分支目标与操作数辅助函数。被
                              dex 脚本共享的库，也可独立运行以带偏移 dump 单个方法
  dex_find_insn.py            按解码语义定位一条指令，并打印其精确字节
                              偏移，附上下文与任一分支的两侧 —— 你靠这个找到
                              补丁点，而不是猜偏移
  dex_patch_bytes.py          按 JSON 规格做等长字节补丁：语义匹配、通过
                              expect_next 钉定极性、等长强制、校验器检查、dex
                              头重算、重新解码以证明它已落地（先 --dry-run）
  dex_check_verifier.py       三级检查：是否有任何条件分支以 move-result 为目标
                              （绕过它的生产者）？比较两个构建，并把
                              既存发现与你补丁引入的回归分开
  coldstart.py                冷启动捕获：定时截图连拍 + logcat 信号 +
                              已安装构建事实 + 启动计时，并在前台
                              activity 不是你的 app 时发出警告
  so_constpatch.py            对一个孤立的字符串常量做等长原地改写，用于
                              重定向一次库加载，而不是击败一个检查
  smtool.py                   带可配置 classpath 的 baksmali/smali 包装器
  dexpatch/                   dexlib2 方法级重写器（用于需要新指令的改动）
  patch_smali.py              smali 树中的方法体替换
  dex_strpatch.py             带 string_ids 顺序守卫的字节级字符串补丁
  dex_classdiff.py            证明一次 dex 编辑是外科式的
  dex_strings.py              不需要反编译器的 strings/URL/SDK 标记提取
  dart_pool_strings.py        从 Dart AOT snapshot 恢复字面量（带帧条目、
                              单字节 vs UTF-16 的分岔、文件偏移、游程噪声过滤）
  dart_pprefs.py              为 Dart snapshot 构建/查询 对象池 -> 代码位置 索引
  dart_disasm.py              Dart AOT 代码的带注释窗口式反汇编 + B/BL 调用者索引
  find_refs.py                在给一个方法打补丁之前统计它的调用者
  repack.py                   重建 APK、只剥离签名、保留 META-INF/services/、写出
                              4 字节对齐的归档（resources.arsc STORED+对齐）、签名、校验；
                              也处理 split APK / App Bundle 集合：清点、用一个
                              keystore 为每个成员签名，或把 code/native 成员合并成独立 APK
  devsh.py                    引号安全的 ADB shell 辅助工具
  usb_net_proxy.py            通过 USB 给离线设备提供网络
  datastore_inject.py         安全地编码/注入 AndroidX DataStore preferences
  probe_api.py                带正确请求头探测一个 HTTP API
  grab_crash.py               恢复被崩溃上报 SDK 藏起来的栈
  install_test.py             安装 + 启动健康检查，带 logcat 信号扫描
  frida_probe.js              四层运行时探测（app 网络层 + OkHttp + java.net + 异常）
  run_probe.py                注入探测、把它流式写入日志文件、保持常驻
  tls_check.py                对一个或多个 host 做严格证书检查
  preflight.py                每个实验块之前的环境检查（设备、root、
                              ABI/翻译层、时钟偏移、残留 proxy/forward、失联的 server）
  lib_map.py                  一个活进程里*实际映射*了什么：每库路径、
                              基址、架构，以及它来自 APK 还是
                              运行时物化出来的
  elf_plt.py                  从重定位表把 PLT stub 解析到它导入的符号（x86_64 + aarch64）；
                              列出某个符号的调用者；对两个
                              库做字节级 diff，并指出每个变更 stub 属于哪个符号
  apk_diff.py                 两个构建的条目级 diff：变更 / 新增 / 移除，按
                              内容哈希，使等长替换也能被抓住
  native_crash.py             从日志或 tombstone 定位一次 native 死亡：signal、故障
                              地址、寄存器、把帧拆成 app 与 system、故障
                              指令本身，以及当故障看起来是*被安排好的*时给出标记
  blob_decode.py              搜索、而不是猜测一个存储值的分帧
                              （base64/hex x 旋转 x deflate）；把编辑后的 payload 重新编码
  snap.py                     有界连拍截图 + 带停滞检测的控件树捕获，
                              并对这棵控件树是否可用给出结论
  sig_probe.py                找到确切的 signatures[0].toCharsString() 值 —— 从 APK 得到的
                              离线候选，或从设备读取的权威值
  spawn_patch_detach.py       在 Frida 探测下 spawn、detach，然后启动并捕获：在
                              spawn 模式下 Activity 栈常常起不来，而内存
                              写入能在 detach 后存活，hook 不能
  hook_patch_only.js          spawn_patch_detach.py 的最小探测 —— 按偏移把一个 native
                              死亡点失效化并报告 PATCHED
  dex_dump_validate.py        对一目录的 dump dex 镜像去重、校验并排序：sha256
                              分组、头完整性、区分真实 dump 与抽取壳骨架的
                              平凡方法体比例，以及一个最可能原件的排序
                              （对页对齐的 /proc/<pid>/mem 捕获用 --trim）
  dex_mem_scan.py             在内存捕获中搜索内嵌的 dex 镜像，并按每个镜像自己头部
                              声明的尺寸抽取出来 —— 用于躺在匿名映射里、
                              没有任何 maps 条目为它命名的解密 dex
  lsposed_scaffold.py         生成一个最小 LSPosed/Xposed 模块工程（带
                              xposed meta-data 的 manifest、assets/xposed_init、hook 类、无 gradle 的构建说明）
  frida_rpc_serve.py          把 Frida 脚本的 rpc.exports 桥接到本地调用方，带断线重连
                              处理，从而可以调用一个活的 native 函数，而不是逆向它
  rpc_template.js             frida_rpc_serve.py 的可编辑配套脚本
  stalker_trace.js            用 Frida Stalker 做指令级追踪：可配置目标、
                              触发选择、事件流，以及输出体积规则
  stalker_report.py           把 stalker_trace.js 的日志归约为基本块直方图与调用序列，
                              并对实测到的零事件情形给出明确诊断
  mt_mcp_probe.py             探测 MT Manager 的设备端 APK MCP（Streamable HTTP，端口 8787）：
                              JSON-RPC 握手加上分组后的工具清单
  java2c_probe.py             收集能区分 Java2C 与抽取壳、VMP 及普通 JNI sinking 的
                              证据：从 dex 得到 native 密度与 stub 比例、
                              从 `.so` 得到 JNI_OnLoad / 动态注册 / 工具链字符串，
                              每一项都标注为 强/中/弱
  protobuf_decode_raw.py      无 schema 的 protobuf 解码：hex / 文件 / stdin 到 JSON 树，每个
                              长度定界字段都保留为一个候选集合、并列项予以标注而
                              不是猜测，另含字节级精确重编码以检查一次往返
  vmp_diff_harness.py         构建带标注的 opcode 覆盖 fixture、从原始/加固 dex 对
                              推导候选私有 opcode 映射、在闭环中验证该比较，
                              并把还原出的指令流渲染成 smali 骨架
  kernelsu_syscall_mask.py    生成 KernelSU/APatch 系统调用遮蔽脚手架：一个可安装的
                              用户态模块骨架加上 KPM/LKM/eBPF 内核侧模板，每个
                              都带自己的版本闸门和明确的未核实标注
  rasc_build.py               构建并验证 rasc，即 ASC 索引器的 Rust 重实现：
                              --check 检查已有什么、--build 克隆并 cargo、--verify 用
                              droidasc 校验一个 APK，并在任何类集合差异上失败
  scan_leaks.py               在发布一个仓库之前扫描其中的目标身份：manifest / `pm` / `ps`
                              上下文里的 bundle id、序列号形态的 token、PAT、内联
                              appkey 赋值、字面 endpoint、宿主用户路径。对
                              必须保留的一切给予豁免（工具、库、CVE、加固产品、
                              公开 crackme、占位符），发现项带上下文，
                              `--show-exempt` 打印某个命中项为什么被抑制，退出码 0/1/2
  svc_scan.py                 指出某条内联 `svc` 背后的系统调用以及它所在的段，
                              这决定 libc 层面的 hook 究竟能否观察到该调用；
                              `--context` 展示邻近字节，因为字节扫描也会匹配到数据
  anti_detect_probe.js        仅观察的 Frida 探测（不打任何补丁）：path/loader/thread/kill
                              hook 附调用者模块 + 偏移、一份环境自述
                              （`TracerPid`、以 frida 命名的映射），以及实时流式输出，使一个
                              亚秒级自毁目标仍能产出证据
```

仓库另外带有一个**可执行**的测试层，它与证据记录是两回事：`tests/` 断言脚本的行为（单元、CLI 契约、无设备集成），`tests/benchmark.md` 记录某条路线在真实目标上的表现。`tests/README.md` 说明了这个划分，`.github/workflows/ci.yml` 运行各闸门加测试套件。

## 安装

这个仓库是一个 **skills 仓库**：skill 位于 `skills/apk-reverse/`，这正是 `skills` CLI 解析的布局；安装是按名字进行的，而不是复制一个目录：

```
npx skills add newliver666/apk-reverse              # install every skill in the repo
npx skills add newliver666/apk-reverse --list       # list what is here, install nothing
npx skills add newliver666/apk-reverse --skill apk-reverse -y
npx skills use  newliver666/apk-reverse@apk-reverse # use it once, without installing
```

CLI 默认把 skill 软链进你的 agent 的 skills 目录（`--copy` 则生成独立副本），`-g` 为所有项目安装而不是仅当前项目。仓库里只有一个 skill 时，`--skill apk-reverse` 今天是多余的；这里把它写出来，是因为等第二个 skill 存在时，正是它用来选中单个 skill。

安装后，agent 在任务匹配其描述时加载 `SKILL.md`，并且只在需要时拉入 `references/*`。没有全局状态，没有与机器绑定的路径，也没有构建步骤。

## 环境要求

没有什么是强制的；每个脚本都自己检查所需。`skills/apk-reverse/scripts/doctor.py` 报告这里哪些工具存在、因此哪些脚本能跑，以及——这很有用——哪些工具存在于 PATH 之外。

如果你的工具链不在 PATH 上（项目本地的 `tools/` 目录、带版本号的 SDK 目录、可运行的 `.jar` 而不是一条命令），把 `APKREV_TOOLS` 设为一个或多个目录，`doctor.py` 就会找到它们：

```
set APKREV_TOOLS=<dir>;<dir>                     # Windows, e.g. an SDK or project-local tools dir
export APKREV_TOOLS=<dir>:<dir>                  # POSIX
```

脚本本身是纯 `python3`，并且意图在 Windows、macOS 和 Linux 上行为一致；凡有片段仅限 POSIX，都会标注出来。这里没有任何东西假定你用的是 Unix shell。

| 工具 | 用途 |
|---|---|
| Python 3.9+ | 所有脚本 |
| **`droidasc`**（ASC）（**可选，但强烈建议——先装这个**） | 整 APK 交叉引用索引：`findrefs` / `listclass` / `getclass` / `getmanifest`。一句 `pip install droidasc`，无 JVM、无 SDK、无需建索引。把「这几千个类里哪一个提到过这个字符串」变成亚秒级查询，也是找到名字被 R8 混淆过的类的唯一路线。**这是 agent 在做任何完整反编译之前应当伸手去拿的工具** —— 见 `skills/apk-reverse/references/toolchain.md` §droidasc (ASC) —— 一次查询就能问一个 APK「谁引用了这个？」 |
| `ddc`（可选，但强烈建议） | 单文件 dex→Java 反编译器，带查询子命令（`info`、`findrefs`、`strings --with-locations`、按类反编译）。无 JVM。**读** ASC 所**定位**的东西；也能可靠地报告包身份 —— 见 `skills/apk-reverse/references/toolchain.md` §ddc —— 带查询子命令的 dex 转 Java（值得采用） |
| `baksmali` / `smali` + `dexlib2` jars | 反汇编、汇编、外科式打补丁 |
| JDK（`javac`、`java`） | 构建/运行 dexlib2 补丁器；同时提供 `keytool`/`jarsigner` |
| Android SDK build-tools（`aapt`、`zipalign`、`apksigner`） | manifest 信息、对齐、签名。**`apksigner` 才是该用的签名器** —— `jarsigner` 会重写归档并破坏 Android R+ 所要求的对齐 |
| `uber-apk-signer`（可选） | 一步完成对齐 + 签名 |
| ADB | 设备工作 |
| Frida（宿主包 + 与之匹配的设备端 server） | 动态分析 |
| 一台已 root 的设备或模拟器 | 静态分析之外的任何事 |

这些都不需要在 `PATH` 上：每个脚本都为它外壳调用的工具接受显式路径，`skills/apk-reverse/references/toolchain.md` 覆盖了如何找到一个 `PATH` 不认识的安装（对 `apksigner` 和 `keytool` 来说这是常见情况）。

## 先读这个

**本项目仅为学习、研究和经授权的安全测试而发布。** 它不附带任何 exploit payload、任何目标数据、任何第三方二进制 —— 它是一套方法、一组脚本和一份证据记录。你有责任确保自己对所分析的对象拥有相应权利；见文末**免责声明**。

`skills/apk-reverse/references/pitfalls.md`。这是这里最有价值的文件 —— 每一条都是在看起来完全健康的情况下产出了损坏产物的失败。

最痛的四个：

1. 重打包时把整个 `META-INF/` 剥离，会删掉 ServiceLoader 注册，app 在启动时死掉，而报错信息指向一个毫不相干的库。
2. 对一个字节级字符串打补丁却不保持 `string_ids` 顺序，整个 dex 会被拒绝，而 checksum 和签名却完美通过校验。
3. 用整棵 smali 树往返来重建 dex，会不可见地损坏 R8 的输出 —— 类表对比是干净的，它只在运行时炸开。
4. 通过让它**不返回**来失效化一条 native 终止路径。一个自旋 stub 并不能抑制检查；它冻住调用者和它身后的每一个线程。app 挂死，且*完全没有崩溃记录*，最终的死亡会被归咎于那个杀掉这个冻结进程的任意东西。

## 范围

为处理你自己的应用、你被授权分析的样本，以及 CTF/竞赛沙箱而构建。它不含任何内置的第三方二进制，也不含任何目标特定数据。

它覆盖什么、刻意不覆盖什么，写在 `SKILL.md` 顶部 **Coverage** 一节。简版：仅 Android（不含 iOS），并且在经过真实打磨的层上深入 —— dex 补丁、重打包、壳与自定义加载器、native 篡改响应，以及 Flutter/Dart AOT。一次扩展迭代加入了第二梯队的已记录路线：重打包受阻时的**模块侧交付**、**抽取壳恢复**及其 VMP 边界、用于「调用而不是阅读」的**模拟执行与实时 RPC**、针对 OLLVM 的**指令级追踪**、REST 之外的**协议逆向**、当用户态 hooking 可证明够不到时用的**内核路线**图，以及**设备上工具**。随后一次**基准迭代**把公开目标放到这些路线之下（`tests/benchmark.md`）：它加入了 **Java2C 判别**（那种会让 agent 去追一个从不存在的解密 DEX 的误诊）、**split APK / App Bundle 处理**、**无 schema 的 protobuf 解码**、一个 **Dex-VMP 差分**测试台，以及**带版本闸门的内核模块模板** —— 并纠正了先前两条与自身测量结果不一致的说法。Unity/IL2CPP 逻辑恢复、React Native/Hermes 字节码内部，以及击败服务端权威**不**在覆盖范围内，skill 的写法就是明说这一点并停下，而不是把最近的一条已记录流程套用到一个它并非为之编写的目标上。

Coverage 一节完整陈述、同时也应当放在这里的四条限定：

- **Flutter/Dart AOT 分析有一个依赖。** 工作流始于一份 pool 列表（`pp.txt` 一类输出）。产出它需要一个 snapshot 解码反编译器 —— aotopsy（静态二进制，不需要工具链）或 blutter（从源码构建，约 80 秒）—— 而本仓库不含其中之一。它被点名为前置条件，而不是留在那里让人自己推。
- **本仓库里并非每条主张背后都有一次运行。** `docs/tool-verification/` 记录了实际测量了什么、在哪个目标上、用哪个独立交叉检查确认；那里未覆盖的内容都是凭经验记录的，按本 skill 自己的主张阶梯，应当读作*推断*。
- **扩展迭代被单独记录，并且大部分是*推断*。** 其证据在 `docs/tool-verification/EXTENSION-*.md`，一个主题一个文件，各自带强度说明。那里常见的形态是*工具被测量过，路线没有* —— 所以在把任何较新的文档当作已验证路径之前，先读那些文件。
- **基准迭代按行记录，并带有该行自己的强度。** `tests/benchmark.md` 列出每个公开目标、该行演练的脚本、实际发生了什么（包括失败的行和没人跑的行），以及证据有多强。标为 `unverified` 的行是在陈述本仓库证据的状况，不是在陈述机制本身。

## 仓库维护

根目录下住着四个工具，它们不属于已安装的 skill：

```
check_repo.py      发现的每个 skill、frontmatter 有效、脚本可运行、
                   文档中的路径可解析、README 路径显式且存在，
                   并且 —— 仅在受跟踪的表面上 —— 没有目标身份
                   （把规则委派给 skills/apk-reverse/scripts/scan_leaks.py，
                   这样要争论豁免清单时就只有一个地方）
check_refs.py      每一处指向另一文档某节的交叉引用，
                   都能到达该文档里真实存在的标题
check_routing.py   按需清单仍与入口点一致：症状镜像与 SKILL.md 一致、
                   每个 reference 文件都在 skills/apk-reverse/references/routing.md 中
                   被点名，每个脚本也是
check_commands.py  文档让你运行的每条命令都会与脚本自己的 argparse 表
                   核对 —— 一个不存在却被写进文档的 flag，是锚点检查
                   看不见的漂移
check_budget.py    阻止常驻加载的部分悄悄膨胀：按行和 token 测量 SKILL.md
                   的整个主体（含索引行，因为它们也会被加载）、索引行长度、
                   没有可导航头部的长文件，并把含糊其辞的规则作为趋势报告
build_scripts.py   审计机器特定残留物（绝对路径、凭据）
```

一致性有一种天然的反向压力 —— 一条断掉的路径会大声失败，然后有人修它。膨胀没有，这正是第三个工具存在的原因：每次迭代都会加一个 reference、一行索引和一条覆盖主张，而没有测量的话，仓库里没有任何东西会注意到。

`tests/benchmark.md` 保存**回归矩阵**：维度 -> 公开目标 -> 该行演练的脚本 -> 实测结果 -> 强度标注。它是你在信任 `docs/tool-verification/` 下任何主张之前要重跑的检查表。样本会下载进 `tools/_work/` 且从不提交，因此每一行都点名它的公开来源并记录它所针对的哈希。

`docs/tool-verification/` 也不属于已安装的 skill。它是针对一个真实目标、一次测量迭代的证据记录：每个脚本实际做了什么、哪个独立方法确认了它、发现了哪些缺陷，以及该目标未能演练哪些场景。它存在的意义，是让 `SKILL.md` 里的 **Coverage** 主张可以被对照运行来检查，而不是被信任；也让缺口被写在下一个人能找到它们的地方。

---

Proudly supported by the [LINUX DO](https://linux.do) community.

## 免责声明

**仅为学习、研究和经授权的安全测试。** 本仓库中的每个脚本、reference 和已记录结果，都是为了解释 Android 应用分析**如何**工作，使从业者能对自己已经拥有的工具进行推理。这里没有任何东西是一项服务、一个产品，也不构成对任何特定用途的背书。

- **仅限经授权的目标。** 请把它用在你自己拥有的应用、你被明确许可分析的应用、公开的 CTF/挑战材料，或你掌控的沙箱中。分析你无权分析的软件，在你所在的地区可能违法，而这个判断要由你作出，不是由本仓库作出。
- **不提供担保，不保证适用于任何目的。** 材料按*现状*提供，不附带任何形式的担保。结果是某台机器在某个时刻的测量记录；这里没有任何东西承诺某条路线会在你的目标、你的设备、你的工具链或今天的 app 版本上生效。
- **先验证再信任；先备份再行动。** 多个脚本会修改产物（dex、APK、`.so`、已存储的 app 数据），有些会在已 root 的设备上操作。保留你自己的副本、在副本上作业，并在对你在意的东西跑任何东西之前先读 `SKILL.md` 的 gate。
- **你的使用由你自己负责。** 作者与贡献者不对因使用或误用本仓库而产生的任何损失、损害、法律后果或服务中断承担任何责任，也不与任何可能被用于检查的应用、厂商或平台存在隶属、背书或代理关系。
- **测试数据不在此分发。** 样本、dump 和设备产物被刻意排除在这棵树之外（`.gitignore` 排除了它们），只存在于本地被忽略的工作区中。你为了跟做而取得的任何东西，都由你自己负责保管，并在用完后删除 —— 遵守你本地的规则以及样本自带的条款。本仓库*确实*发表的是方法与证据，且已移除全部目标身份。
- **无隶属关系。** 工具、库、加固产品和公开挑战目标的名字出现，只是为了让材料可复用；它们属于各自的拥有者，本项目与它们没有关联。
