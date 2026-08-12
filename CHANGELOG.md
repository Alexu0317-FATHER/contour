# Changelog

## [Unreleased] — 2026-08-12 · 目录布局与分发通道

### 一度扁平化到根，又改回 `skills/contour/`

先把技能上提到仓库根（`adf2ad9`），理由是贴合 Anthropic Agent Skills 的单技能仓库惯例（`<skill>/SKILL.md`）。**惯例本身是真的，但它成立的前提是"这个仓就是这个技能"**——而本仓还装着 `docs/新知界需求.md`、`docs/roadmap/`、`docs/history/`、`evals/`、CHANGELOG，它是**项目开发仓，不是技能分发包**。前提不成立，所以改回来（`7a955c3`）。

查证之后，四条安装通道**没有一条**要求"仓库根即技能根"：

| 通道 | 实际从仓库取什么 |
|---|---|
| plugin marketplace（claude.ai + Claude Code 一次覆盖） | 读根上的 `.claude-plugin/marketplace.json` |
| Codex `skill-installer` | `--repo <owner>/<repo> --path <技能子目录>`，只取子目录 |
| claude.ai 手动上传 | 打包 zip，只含技能部分 |
| 本地手动装 | 复制或软链技能目录 |

三条只取子目录，一条读根上的清单。扁平化没给任何一条带来好处，**只挡死了 marketplace**——而 claude.ai 的 Plugins 页能直接把 GitHub 仓添加为 marketplace，那是唯一能一次覆盖 claude.ai 与 Claude Code 的通道。

- **新增 `.claude-plugin/marketplace.json` 与 `plugin.json`**（`source: "./"`）
- **`evals/` 留在仓库根，不进技能包**：它评的是技能自身，且内容是编造的测试场景，混进运行时可能被模型误当成用户的真实状态——跟 `tests.md` 绝不进被测端上下文同属一类风险
- 活文档路径引用同步更新，已脚本校验无死链

### 查证到的分发事实（此前全是推测）

- **Codex 有原生技能目录** `$CODEX_HOME/skills/<name>`（默认 `~/.codex/skills`），格式与 Claude 完全一致；`.system/skill-installer` 可从任意 GitHub 仓安装，**含私有仓**
- **claude.ai 账号级技能覆盖 chat、Cowork 与 Excel / Word / PPT / Outlook 加载项**；Claude in Chrome 未见文档说明，待测
- **本地 `~/.claude/skills/` 与 claude.ai 账号技能互不同步**，两个层级各自独立；plugin marketplace 是唯一能同时覆盖两边的通道
- **技能默认就有 `/skill-name` 显式唤醒**，自定义命令已并入技能；`disable-model-invocation: true` 可让某个技能**只有用户能唤起**，由 harness 拦截模型调用

## [Unreleased] — 2026-08-11 · 交叉评审合并，知界技能首版草稿

CC 与 Codex 两条并行线的交叉评审结束，结论合并为单一实现。**评审阶段到此为止，两份评审已归档。**

### 文件去哪了

| 原位置 | 新位置 | 说明 |
|---|---|---|
| `新知界需求.md`（仓库根） | `docs/新知界需求.md` | **当前版本的唯一需求规格**；只有准备进入当前实现的能力才写这里 |
| — | `docs/roadmap/` | 已确认但暂不进入当前版本的后续能力；按主题单独成文，成熟后再进入需求或技能 |
| `NOTES.local.md`（仓库根） | `docs/NOTES.local.md` | 决策记录，仍被 gitignore |
| `docs/倾倒与同步协议-v0.md` | `docs/history/` | 已吸收进技能，头部标注了每节去向，**不再修改** |
| `docs/原生记忆可见性测试.md` | `docs/history/` | 同上 |
| `docs/cc_review.md`、`docs/codex_review.md` | `docs/history/` | 评审存档 |

**规则只活在仓库根的技能一份。** 技能随包分发到各端，`docs/` 不会——规则留在 `docs/` 等于每个端拿到的技能都缺协议。要改规则改技能，不要改归档。

### 新增

- **`references/protocol.md`** —— 数据面。实例仓结构、`endpoint-id` 规范、倾倒包 schema、消费 manifest、基础版本检查、GitHub 通道验证（GH-01～05）。吸收自协议 v0
- **`references/drive.md`** —— 控制面。确认门槛、隔离执行、hook 与自动化的边界
- **`assets/templates/`** 新增 `config.md`、`sources.md`、`endpoint-state.md`
- **`assets/prompts/self-report-incremental.md`** —— 日常增量用，基线 prompt 只在端首次纳入时跑
- **`scripts/validate_dump.py`、`scripts/new_dump.py`** —— 包 schema 校验与唯一 ID 生成。确定性的活交给脚本，不让模型每次现编
- **`evals/evals.md`** —— 技能自身的评测规格（开发期工具，不是运行时）
- **`docs/roadmap/锚点适配路线图.md`** —— 固定后端共同契约与按需加载方式；记录 GitHub 当前基线、Google Drive 版本模型及准入验证，不改变 MVP 只支持 GitHub 的范围

### 冻结的范围

- **端**：ChatGPT、Codex、Claude.ai、Claude Desktop、Claude Code
- **锚点**：**新建的** GitHub 私有记忆实例仓。现有 `Alexu0317-FATHER/contour` 是技能代码与历史项目仓，有公开发布记录，**不能兼任个人记忆锚点**
- **退出范围**：Google Drive（后续方向）、Gemini 与国内模型、Notion / Dropbox 等其他后端、"写不进锚点时用户手工搬运"的降级档

### 改了什么

- **资产模型**：五份小写文件 → `config` / `profile` / `now` / `routing` / `sources` / `evidence` / `tests` + `state/endpoints/` + `dumps/` + `review/`。补回 `sources.md`（信息源路由，此前是实质缺口）；同步台账从 `now.md` 拆出去（`now.md` 只放用户状态，游标归各端自己的文件，避免并发热点）
- **不变量一** 从"五端接同一个实例"改为三条可执行纪律：**一个写入权威 + 读前追平 + 条件写入**。版本号只提供观察不提供互斥，所以锚点必须提供可验证的条件写入
- **确认门槛**（新增 `SKILL.md` 第零节）：description 匹配 ≠ 执行权限。未获用户明确同意时零外部操作
- **hook 与定时任务不进 MVP 默认**。原"每轮 Stop 攒 buffer、下次 SessionStart 推送"方案否决——它未经确认就 commit/push，且污染工作会话上下文
- **时间裁决收紧**：`captured_at` 与触发类型只用于审计，**增量包也不例外**。只有条目级依据（事实发生时间、用户陈述时间、平台记忆创建时间、明确的取代/撤回关系）能裁决
- **倾倒包不可变**，新包不淘汰旧包。自述是概率性召回不是数据库快照，去重在条目层做
- **协调者按能力临时接任**，不指定固定协调端；乐观并发靠后端的条件写入
- **删除语义**：`evidence.md` 不再"永不删"。支持更正（`superseded`）与撤回（不含原文的墓碑）；MVP 不自动重写 Git 历史
- **测试身份隔离**：主考身份可见题库，被测身份不可见。同一产品可用不同 session 分别承担
- **Codex 装法改为受管区块**——实测确认 Codex 加载 `AGENTS.md` 但**不展开其中的 `@路径`**，故不能照搬 Claude Code 的活导入
- 删掉一批无依据的阈值数字（`now.md` 一个月降权、固定 8–12 题），改为从字段变化速度和路由条数推

### 发布前审计的修复（第二个 commit）

三名审查者过了一遍协议、交互与质量保障。无 P0，九项发布阻断已修：

| # | 问题 | 修法 |
|---|---|---|
| 1 | **`endpoint-id` 目录穿越** —— `../escaped` 能把倾倒包写到收件区之外，校验器还扫不到 | 字符集封死 `[a-z0-9]+(-[a-z0-9]+)*`，写入前再验一次解析后的路径确实在收件区内 |
| 2 | **包身份三套定义**，且撞号能通过校验 | 唯一身份定为 frontmatter 的 `dump_id`(UUID4)，文件名带上它；校验器验 UUID4 格式并在批次层面查重 |
| 3 | **"撤回"没把原文拿掉** —— 它还在 `dumps/` 里明文可读 | 默认撤回如实改口为"停止使用，原文仍可读"；要连原文一起清的，新增单独确认的**脱敏**动作，代价（破坏可追溯、不动 Git 历史、拦不住重新引入）原样告知 |
| 4 | **发布缺原子边界** —— 逐文件提交会让别的端读到"新画像+旧 manifest"或反之，后者是静默丢数据 | 一次发布必须是一个不可拆分的提交；多文件原子提交纳入 GH-04，**做不到的端没有协调资格** |
| 5 | **确认门槛允许未经同意读私有仓** | 读实例仓改判为外部操作。语义软命中只能诊断加问一次，**连读都不许**；用户明确要状态或要同步时才读 |
| 6 | **隔离执行会丢来源端记忆** —— sub-agent 既看不到本轮对话也够不着该端原生记忆，会交上来一份格式完整但空的包 | 隔离边界划在倾倒之后：倾倒必须留在当前会话，合并/发布/加载才可外包 |
| 7 | **加载自测是"先看答案再考试"** | 验证装载改为主考/被测分离；开不出第二个会话时降级用通道题，并标明这次验证是降级的 |
| 8 | **常驻层缺快变信息查证入口** | 常驻包装补三行：快变问题走 `sources.md`、查不到要说明依据哪次同步、同步入口 |
| 9 | **README 仍是旧版说明**（slash commands、Stop hook、不存在的图片） | 重写中英文 README，如实写明"开发中、还装不了"，并指明旧功能属于已归档版本 |

随后修正一并处理：manifest 补 `拒绝` 终态（否则用户否掉的探测包每轮重来）；同端并发会话的状态文件也要条件写入；冷启动验收拆成"最小可用"与"冷启动完成"两档，后者要求**每个已登记端都完成基线倾倒**；校验器堵掉 inbox 根部后门；`evals.md` 写明它目前只是规格、没有执行器，E-3 必须查工具调用记录；`.gitignore` 补 `.claude/settings.local.json`；修掉归档文档的失效链接。

**一处审计判错**：`.claude/settings.local.json` 已被用户全局 gitignore 覆盖，本机无泄漏风险——但换台机器就没有，所以仍写进仓库 `.gitignore`。

**一处上一版结论作废**：上个 commit 说"docs 链接全部有效"，那句不成立——校验器验的是工作区，而 `docs/NOTES.local.md` 被 gitignore，clone 出来就是死链。校验器已改为只认已入库文件。

### 收口修复（第三个 commit）

定向复审发现脱敏方案还差最后一扣，四处已补：

- **新删除语义没同步到唯一活规格和模板**——需求文档和 `evidence.md` 模板仍写着"从当前资产移除"，`schema.md` 还说端状态"天然无冲突"。规则、模板、活规格必须一致，否则另一个 AI 会照旧模板执行
- **manifest 没定义脱敏怎么记账**——新增 `redaction_events`，跟消费状态**平行**而非第四种状态：一个已消费的包照样可能几个月后被脱敏，两件事在不同时间轴上。带 `content_revision` 字段（首次入库隐含为 1），让同一 `dump_id` 的内容修订可追踪。**它不证明合法性**——有写权限的人能连字段一起改；变更是否合法以 Git 历史、原子发布记录和用户确认记录为准
- **脱敏必须走原子发布**——它一次改原包、`evidence.md`、`review/`、manifest 和版本号，必须同一提交并接受基础版本检查。做到一半被读到比不脱敏更糟
- **"从此刻起读不到"承诺过头**，且与同页"Git 历史仍有明文"直接冲突。收紧为单句保证：**当前默认分支最新版里已定位到的明文会被替换**；Git 历史、旧克隆、漏检的转述、各端原生记忆一律不在保证范围内

另：**"一个写入权威"改为"一个权威锚点"**。原措辞容易被读成固定一个协调端，与"多端可临时接任协调、单次发布串行"冲突。README 中英文与 `SKILL.md` 不变量同步改。

### 首次统一发布增加两端基线门槛

- 冷启动先登记用户实际使用的端；第一版统一资产只有在**至少两个不同的已登记端**各提交一份格式合规的 baseline 后才允许整合和发布。同端多包只算一端，已有 profile / 记忆导出不替代第二端，空内容但格式合规的 baseline 可以计入
- 门槛未满足时只保存 `config.md`、端状态和未消费倾倒包，不生成统一文件、不写消费 manifest，避免把单端记忆包装成“暂定统一结果”再回灌放大
- 门槛只限制首次发布；已有多端统一版本后，单端 incremental 可以照常异步合并
- “至少一个网页端 + 一个本地端”改成“至少两个不同端”，保留 `ChatGPT + Claude.ai` 等纯网页组合
- `config.md` 增加 baseline `dump_id` 与初始化状态；`validate_dump.py --cold-start-ready` 提供确定性检查；E-4 增加单端阻断与第二个纯网页端到达后的放行案例

### `sources.md` 分两区，新增知识资产路由

起因是一个具体场景：在一个端让 AI 写了份 GitHub 指南存进笔记系统，换个端问同样的问题，那一端答得挺好，于是又存了一份。**两份互不知情、各自演化——这是单一信源不变量在知识层的同一个失效。** 而资产比记忆更难自愈：它的位置只有产出它的那一端知道，没有任何自然机制会让它传过去。

CC 与 Codex 两轮设计评审的合并结论，字段与结构以 Codex 的方案为基底：

- **`sources.md` 分为动态信源区（表格，去哪拿最新事实）和知识资产区（记录块，已经沉淀过什么）。** 两区共用"指针 + 保质期"机制和归属判据，但识别方式不同：动态区认问句形态（当前 / 最近 / 下一步），资产区认主题命中
- **资产用记录块不用宽表**，编号 `A-001` 起递增、永不复用。必填七键：调用线索、权威资产、覆盖范围、超出覆盖时、来源不可用时、来源记录、最后验证。理由是 `来源记录` 多值、`覆盖范围` 与 `超出覆盖时` 是散文，塞不进单元格；结构与 `evidence.md` 同构
- **不设必填「使用规则」**，共同行为只在模板区头定义一次，写成断言句：*命中且在覆盖范围内时，先读那份资产，不要凭自己的知识直接答*。逐条重复同一句默认值只会被敷衍填满
- **「超出覆盖时」与「来源不可用时」是两条独立故障轴**，不得合并：前者走下一跳，后者是故障，必须让用户看见并检查路由
- **「调用线索」不是关键词表**，要装同义说法、场景和模糊指称；而"我记得以前问过你"这类泛指称属于区头规则（命中时扫全区），不写进行内
- **准入门槛**：同时要求会话外稳定位置与可观察的跨会话复用信号；普通项目实现、代码修改和当前工作区里本来就能定位的交付物不登记
- **自述 prompt 新增一类**：基线第 7 类（产出过什么 / 改过什么），增量第 5 类（产出物变动）。后者是资产路由最隐蔽的腐烂方式的唯一上报通道——指针还对、页面还在，但内容早已超出记录的覆盖范围

**只做读侧。** 读完是否提议把新内容补回原文档，属于各端自身行为，知界不定义、不禁止、也不承担；跨系统写回不进当前版本。

**不买常驻预算。** 目标是"有机会被想起"而非"每轮确定性在场"，所以走喂：只喂主题、位置和覆盖范围的**正面部分**，不喂否定边界——禁令形态在黑盒记忆里会被磨平，剩下一个膨胀的覆盖声明，比不喂更危险。召回率按 `probe.md` 的 P-4 实测，不足时再评估是否需要常驻。

评审后补齐四处闭环：知识资产动作在倾倒包中归入“非原生记忆来源”，不再混用 `[记]` / `[推]`；修改报告先标 `待复核`，实际读取后才能刷新覆盖范围和最后验证；补独立的 P-4 资产卡片召回探测；修正基线七类与增量五类的计数。

### 已知未决

- **知识资产区一条真实记录都还没有**，准入门槛和调用线索的实际命中率未验证
- 资产卡片喂进黑盒端后的召回率未测（P-4 目前也没跑过）
- 新私仓尚未创建，GH-01～06 一条都没实际跑过
- GitHub 发布路径三选一未定（条件直写 / 端分支 PR / 自动化串行）
- **网页端能否多文件原子提交未知**——若不能，"任意端可接任协调"对它们不成立，协调实际只发生在本地端
- `state/endpoints/` 用 Markdown 还是 YAML
- Claude Desktop 的 `@路径` 支持与记忆归属待测
- `evals/` 没有执行器，门槛与 description 的表现**尚未验证**
- 脱敏拦截靠语义匹配，会漏；墓碑本身泄露粗粒度主题。两个缺陷已写进文档，无解法

---

## [Unreleased] — 2026-08-07 · Pivot archival

Documentation and archival only. **No change to plugin code, skills, or hooks** — `v0.3.0` remains the installable release and the version in both READMEs is unchanged.

### Added
- **`docs/history/PIVOT.md`** — full pivot record: what the cognitive-tracking version was, a dated timeline of the three times the premise changed over seven weeks, why it stopped, which conclusions remain valid, and links to the four published versions of the launch article.
- **Tag `v0.3.0-cognitive` + matching GitHub Release** — complete pre-pivot snapshot. Still installable and runnable.
- **`docs/history/README-cognitive.md` / `.zh.md` + `docs/history/assets/`** — archived copies of the old product description so it stays readable without checking out the tag.
- **`LICENSE` (MIT)** — the READMEs had declared MIT since early versions but no license file existed, so GitHub reported none.
- **`BACKLOG.md`** — committed into the snapshot; its contents (UX perceivability, Setup iteration, multi-domain hook routing, VS Code compatibility root cause) all belong to the cognitive-tracking era.

### Changed
- **Both READMEs now open with a pivot notice** pointing at the tag and `PIVOT.md`. The launch article links here, so readers arriving from it need to know the state of things.
- **`.gitignore` boundaries redrawn** — the nine design documents, the article source, and the old Chinese reference docs remain local-only; `PIVOT.md`, the archived READMEs, and their images are public.
- **Repository description set** on GitHub.

### Rationale
The project is moving from tracking *what the user knows* (a factual layer) to *how the user should be spoken to* (a behavioral layer). The old version worked — the Stop hook → SessionStart loop ran for over a month — but the premise was wrong: cognitive state is only one input into how to speak to someone, and an expensive, fast-decaying one.

Nothing is deleted. The old version is preserved as a running snapshot and as a record of how the thinking changed, which is the more durable artifact.

---

## [0.3.0] — 2026-03-03

### Changed
- **Domain Log removed**: `/contour:sync` no longer writes to a Domain Log file. `[thinking]` patterns are now surfaced directly in the sync report; `[core-candidate]` entries prompt the user to decide immediately rather than deferring to a file.
- **Clarity Signal removed**: All cognitive signal logic now uses Inquiry Signal as the sole `partial` trigger. User acknowledgment ("got it", "I see") is inconsistent and unreliable as a signal baseline.
- **Slash command guard**: `cognitive-monitor.ts` now exits immediately for any userMessage starting with `/`, before calling Haiku — hard filter at script level.
- **extract/sync positioning corrected**: Reframed from "optional fallback" to "historical session backfill" — the Stop hook covers the active session; extract/sync cover past sessions that predate hook installation.
- **README install guide corrected**: Claude Code UI steps updated to match actual flow (Marketplaces → Add Marketplace → Discover tab → install scope selection).

### Removed
- `skills/sync/references/domain-log-structure.md` (moved to `docs/references/` for reference)
- Domain Log file creation from `/contour:setup` (Step 6 removed, steps renumbered)
- Domain Log deletion from `/contour:uninstall`

---

## [0.2.5] — 2026-02-27

### Added
- **Stop hook — cognitive-monitor.ts**: Active cognitive monitoring now runs as a system-level Stop hook after every assistant response. A bun TypeScript script reads the conversation transcript, calls `claude -p --model haiku` for semantic signal classification, and writes directly to Domain State when a signal is detected. No LLM self-check involved — execution is deterministic.
- **Anti-recursion mechanism**: Hook sets `CONTOUR_MONITOR_ACTIVE=1` in the environment before calling the inner claude process. Inner Stop hook detects this variable and exits immediately, preventing infinite recursion.
- **Windows support**: Git Bash path passed as third CLI argument; `CLAUDECODE` env var unset to allow nested claude invocation.
- **setup Step 8d**: `/contour:setup` now installs `cognitive-monitor.ts` to `{AI_INFRA_DIR}/hooks/` and registers the Stop hook in `~/.claude/settings.json` (idempotent).
- **uninstall updated**: `/contour:uninstall` now removes the Stop hook from `settings.json` and deletes the hook script.

### Changed
- **Daily workflow simplified**: `/contour:extract` and `/contour:sync` now serve **historical session backfill** — the Stop hook monitors the active session in real time, while extract/sync cover past sessions that predate hook installation or weren't covered by it.
- **Runtime dependency**: `bun` is now required for the cognitive monitor hook. Users without bun installed will see a warning during setup.

### Rationale
Pre-response prompt instruction (0.2.4) improved signal detection timing but remained unreliable — the model still controlled execution. Moving to a Stop hook eliminates LLM compliance as a variable entirely: the hook fires unconditionally after every response, and classification is handled by a separate Haiku call rather than the responding model's self-assessment.

---

## [0.2.4] — 2026-02-26

### Changed
- **Monitoring mechanism restructured from post-response to pre-response**: Replaced Self-Check Protocol (review output after responding) with Pre-Response Signal Check (classify input before responding). Signal detection now happens as the **first step** of each turn — if a cognitive signal is detected, the Edit tool call to update Domain State fires **before** any response text is generated. This eliminates the structural failure mode where LLMs consistently skip post-response meta-tasks.
- **CLAUDE.md injection block updated**: "CRITICAL INSTRUCTION" section rewritten to match pre-response framing — model is instructed to classify input and act first, not self-check after.

### Rationale
Post-response Self-Check Protocol (introduced in 0.2.2) never triggered successfully in practice. Root cause: LLMs naturally end their turn after completing the primary task (answering the user). A post-response epilogue requiring tool calls is structurally unreliable — the model's "attention" has already moved to turn completion. Pre-response classification exploits the moment when tool-calling intent is strongest (turn planning phase), making signal detection a precondition rather than an afterthought.

---

## [0.2.3] — 2026-02-24

### Changed
- **Monitoring trigger upgraded**: Inquiry Signal is now the sole cognition trigger. Conceptual questions ("What is X?", "How does X work?") fire immediately — Clarity Signal removed entirely (user acknowledgment is inconsistent and unreliable as a signal).
- **setup Step 8c added**: `/contour:setup` now writes a `SessionStart` hook to `~/.claude/settings.json`, ensuring Core Profile and Domain State are loaded deterministically at every session start via system-level hook rather than passive CLAUDE.md instruction.
- **uninstall updated**: `/contour:uninstall` now removes the Contour `SessionStart` hook from `settings.json` as part of cleanup.

### Improved
- README (EN/ZH): Added beginner-friendly guide for customizing storage location via `$AI_INFRA_DIR`, with step-by-step instructions for macOS/Linux and Windows.

---

## [0.2.2] — 2026-02-23

### Changed
- **Main monitoring mechanism overhaul**: Transformed passive "monitor during session" framing into explicit **Self-Check Protocol** executed before every response completion. Model now treats cognitive signal detection as a mandatory per-turn step, not optional background task.
- **Trigger pattern definitions expanded** with concrete examples in `contour-monitoring-rules.md`:
  * Clarity Signal: Explicit understanding markers ("I see", "got it", "makes sense now", etc.)
  * Mastery Signal: Hands-on competence demonstration (correct application, nuanced follow-ups, debugging with concept)
  * Regression Signal: Basic question on previously mastered concept ("How do I X again?", "Wait, what was X?")
  * New Concept Signal: First mention of unfamiliar technical term (user asks "What is X?", "How does X work?")
- **CLAUDE.md injection strengthened**: Added "CRITICAL INSTRUCTION" section with explicit per-response directive. Changed framing from "refer to rules file" to "you MUST execute this before finishing" — hardened with CRITICAL/mandatory language.

### Rationale
Previous monitoring rules relied on passive framing unsuited to LLM execution model. LLMs operate request-response, not event-loop. Per-turn self-check protocol bridges this gap by making signal detection an explicit, non-optional step in response generation workflow.

---

## [0.2.1] — 2026-02-20

### Fixed
- `/extract` now refuses to run in a Contour-operational session (e.g., after `/sync` or `/setup`) to prevent echo signal contamination.
- `/extract` report output constrained: factual buffer status observations are allowed, but AI must not describe Contour's internal mechanisms or imply that extract/sync can modify Core Profile.
- `/sync` report now includes a post-completion reminder not to run `/extract` in the same session.

---

## [0.2.0] — 2026-02-20

### Added
- `/contour:uninstall` skill — removes CLAUDE.md injection, deletes rules file, and optionally deletes data files. Safe by design: never touches non-Contour files.
- Bilingual support for Domain State and Domain Log — setup now generates files in the user's selected language (Chinese or English) based on Step 1 selection.
- `contour-monitoring-rules.md` — dedicated rules file written to `~/.claude/rules/` during setup, separating monitoring logic from CLAUDE.md entry block.

### Changed
- **CLAUDE.md three-layer restructure**: injection block is now a short entry point (~8 lines); full monitoring rules moved to `~/.claude/rules/contour-monitoring.md`. Rules can be updated without re-running setup.
- **Terminology unified** across all skill files: A/B/C/D internal shorthands replaced with Extract Buffer / Domain State / Domain Log / Core Profile.
- **Idempotent injection**: setup now checks for existing `<!-- Contour --> ... <!-- End Contour -->` block before writing — re-running setup replaces the block instead of appending a duplicate.
- Step 5 (domain name prompt) now renders in the user's selected language, fixing a language-switch bug when Chinese was selected in Step 1.
- Setup Step 9 report now renders in the user's selected language.
- README Commands table updated to include `/contour:uninstall`.

### Renamed
- `skills/sync/references/b-structure.md` → `domain-state-structure.md`
- `skills/sync/references/c-structure.md` → `domain-log-structure.md`
- `skills/setup/references/d-structure.md` → `core-profile-structure.md`

---

## [0.1.0] — 2026-02-19

Initial pre-release. Core skills operational: `/contour:setup`, `/contour:extract`, `/contour:sync`.
