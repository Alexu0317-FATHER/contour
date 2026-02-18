# 知界 (Contour) — 设计文档 v5

**最后更新**: 2026-02-18
**状态**: 所有设计文件完成，待真实 session 部署测试

---

## 核心目标

为 Claude Code 建立一个**自动、低成本、细颗粒度、防污染**的个人信息系统。

解决三个问题：

1. **污染**：多层 AI 总结造成信息失真
2. **颗粒度不足**：粗粒度标签导致沟通两极化（"程序员"或"非程序员"的二分法）
3. **上下文污染**：不相关信息被引入当前 session

**核心差异化价值**：不是 personality profiling，不是"让 AI 更了解你"。核心是**追踪用户在不熟悉领域的认知边界颗粒度**——哪些懂、哪些半懂、哪些不懂。D 文件（人格/思维方式）是辅助校准沟通方式，B 文件（认知状态表）才是系统的差异化核心。

---

## 运行环境

- **仅在 Claude Code 中运行**
- 以 **Plugin** 形式发布到 GitHub，通过 `/plugin` 安装
- 仓库地址：`https://github.com/Alexu0317-FATHER/contour`
- 安装后通过 `/contour:setup` 完成初始化
- 数据文件默认存储位置：`~/.claude/contour/`，可通过环境变量 `$AI_INFRA_DIR` 覆盖
- Skill 以命名空间形式调用：`/contour:setup`、`/contour:extract`、`/contour:sync`

---

## 文件系统

### 数据文件（用户本地）

存放在 `$AI_INFRA_DIR`（默认 `~/.claude/contour/`）：

```
~/.claude/contour/
├── extract-buffer.md         (A) 临时提取缓冲，跨 session 数据桥梁
├── {user}-core.md            (D) 人格级：思维方式、核心偏好、价值观
├── {user}-coder.md           (B) 代码领域：认知状态表格 + 通信规则
└── {user}-coder-log.md       (C) 代码领域：完整演变记录
```

### Plugin 文件（GitHub 仓库）

```
contour/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── setup/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── claude-md-injection.md   CLAUDE.md 注入模板
│   │       └── d-structure.md           D 文件格式 + 初始化引导
│   ├── extract/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── signal-formats.md
│   │       └── extract-output.md
│   └── sync/
│       ├── SKILL.md
│       └── references/
│           ├── b-structure.md
│           └── c-structure.md
├── docs/
│   └── references/
│       ├── extract_chinese.md
│       └── sync_chinese.md
├── .gitignore
└── README.md
```

**语言策略**：`/contour:setup` 第一步让用户选择语言（中文 / English）。选择后，所有用户交互输出和生成的 ABCD 文件内容均使用该语言。Skill 内部 prompt 始终使用英文。中文版extract/sync仅作为设计参考文档，不参与运行。

---

## ABCD 文件职责

### A — extract-buffer.md

**目的**：跨 session 的数据传递桥梁。

`/extract` 在目标 session 中扫描对话并写入 A → `/sync` 在新 session 中读取 A（无法访问原 session 的对话）→ A 是两个 skill 之间唯一的数据通道。

- 由 `/contour:extract` 追加写入
- 由 `/contour:sync` 读取并清空
- 用标签区分信号类型：`[cognition]` `[thinking]` `[preference]`

### D — {user}-core.md

**目的**：用户的根本特征。所有 session 的"宪法"。

**内容维度**：思维方式、核心偏好、价值观。

- **全局加载**：`/contour:setup` 在 `~/.claude/CLAUDE.md` 中注入引用指令，每个 session 自动生效
- 变化频率极低（半年到一年审视一次），目标 20-50 行
- `/contour:sync` 不直接修改 D；发现可能需要更新 D 的信号时，在 C 中记录 `[core-candidate]`，由用户手动决策

**D 的初始化要点**：

- 只保留影响 AI 沟通方式的核心特征
- 必须剔除与认知追踪无关的内容（如工作作风、职业技能描述）
- 用户有现成文档时需过滤提取，而非直接照搬

### B — {user}-coder.md

**目的**：代码领域的当前认知状态快照。

**内容**：认知状态表格（知识点 × 认知缺陷/部分理解/已掌握 × 更新时间）+ 领域内通信规则。

- 追求轻量，只记录结果不记录过程（过程归 C）
- 初始化时以 `b-structure.md` 为模板生成
- 两个更新来源：
  1. **主力机制**：CLAUDE.md 中的监测指令，在工作 session 中实时识别认知变化并更新 B
  2. **补网机制**：`/contour:extract` + `/contour:sync`，捕获主力机制遗漏的信号

### C — {user}-coder-log.md

**目的**：代码领域的完整演变记录，供用户手动审视。

**内容**：认知演变全过程 + 思维模式变化 + `[core-candidate]` 条目。

**特征**：

- 由 `/contour:sync` 追加写入，标注执行日期
- **只追加，不读取**——避免 token 成本和上下文噪音
- 初始化时以 `c-structure.md` 为模板生成

---

## CLAUDE.md 加载指令

`/contour:setup` 在 `~/.claude/CLAUDE.md`（全局）中注入以下内容（见 `skills/setup/references/claude-md-injection.md`）：

**D 的加载**：引用 `{user}-core.md`，每个 session 自动生效。

**B 的加载 + 监测规则**：

- 引用对应 domain 的 B 文件
- 监测规则（何时识别为认知变化）和发现变化时的更新动作
- MVP 阶段：单 domain，统一注入全局 CLAUDE.md
- 多 domain 注入策略（工作区级 CLAUDE.md）为阶段二扩展，见 Roadmap

**监测规则摘要**（完整版见 `claude-md-injection.md`）：

- `[cognition]`：用户暴露对某知识点的理解程度变化 → 直接更新 B，静默执行，不打断对话
- `[preference]`：用户明确表达通信偏好 → 域内偏好更新 B，跨域偏好留给 `/sync`
- `[thinking]`：仅观察，不写文件，留给 `/extract` + `/sync` 处理

**关于 `--resume` 的行为**：CC 在 resume 时会重新读取当前 CLAUDE.md，监测指令对 resumed session 中的新交互生效。但 AI 不会主动回扫旧对话历史——旧 session 的全面信号提取只能靠 `/contour:extract`。

---

## Setup 交互流程

### 流程图

```
/contour:setup
│
├── Pre-flight: 数据目录已存在且有文件？
│   ├── 是 ──► AskUserQuestion: "覆盖 D/B/C？(A 文件保留)"
│   │          ├── Yes ──► continue
│   │          └── No  ──► STOP
│   └── 否 ──► continue
│
├── Step 1 — 选择语言 (AskUserQuestion)
│   ├── 中文 ──► 后续所有输出使用中文
│   └── English ──► all subsequent output in English
│
├── Step 2 — 解析数据目录
│   └── $AI_INFRA_DIR 或 ~/.claude/contour/ ──► 创建并告知用户路径
│
├── Step 3 — 用户名 (free text)
│   └── 空值？──► 重新提问（示例：alex, jane）
│
├── Step 4 — 生成 D 文件
│   │
│   ├── AskUserQuestion: 有现成的个人简介文档？
│   │
│   ├── 有 ──► Scenario A ────────────────────────────────────────┐
│   │          读取文档 → 按筛选标准过滤 → 生成 D 草稿            │
│   │                                                             │
│   └── 无 ──► Scenario B ──────────────────────────────────┐    │
│              Q1 背景 (free text + examples)                │    │
│                 └── 空值？──► 重新提问                     │    │
│              Q2 沟通风格 (AskUserQuestion, multiSelect)    │    │
│              Q3 思维风格 (AskUserQuestion, multiSelect)    │    │
│              Q4 AI 行为偏好 (AskUserQuestion, multiSelect) │    │
│              合成 ──► 生成 D 草稿 ─────────────────────────┘    │
│                                                                 │
│              ◄────────────────────────────────────────────────-─┘
│   AskUserQuestion: 确认 D 草稿？
│   ├── 确认 ──► 写入 {user}-core.md
│   ├── 补充内容 ──► 收集 → 更新草稿 → 重新确认
│   └── 调整内容 ──► 收集 → 更新草稿 → 重新确认
│
├── Step 5 — Domain 名称 (free text)
│   └── 空值？──► 重新提问（示例：coder, writer）
│   └── 生成 B 文件 ({user}-{domain}.md)
│
├── Step 6 — 生成 C 文件 ({user}-{domain}-log.md)
│
├── Step 7 — 创建 A 文件 (extract-buffer.md)
│   └── A 已存在且有内容？──► 警告并跳过，提示先运行 /contour:sync
│
├── Step 8 — 注入 CLAUDE.md
│   └── 使用 claude-md-injection.md 模板，替换占位符后追加写入
│
└── Step 9 — 报告
    └── ⚠️  提醒用户重启 Claude Code
```

### 设计说明

**语言选择为第一步**：用户尚未表达语言偏好前不能假定英文，Step 1 的问题文案需中英双语呈现。一旦选定，后续所有输出统一使用该语言。

**空值验证范围**：用户名（Step 3）、Domain 名（Step 5）、Q1 背景（Scenario B）、AskUserQuestion 中"Other"的自定义输入。选项式 AskUserQuestion 本身不允许空提交。

**D 草稿确认循环**：Scenario A 和 B 最终都进入同一个确认环节，用 AskUserQuestion 收集反馈，支持多轮调整直至用户满意。不设调整次数上限。

**A 文件保护**：setup 不覆盖已有内容的 extract-buffer.md，防止未 sync 的信号丢失。

**CLAUDE.md 注入方式**：追加而非覆盖，不破坏用户已有的全局指令。

---

## Skills

三个 skill 均设置 `disable-model-invocation: true`，仅由用户手动调用。

### `/contour:setup`

冷启动引导。完整实现见 `skills/setup/SKILL.md`。引用文件：

- `references/d-structure.md` — D 文件格式和初始化引导
- `references/claude-md-injection.md` — CLAUDE.md 注入模板

### `/contour:extract`

扫描当前 session 对话，提取信号写入 A。在目标 session 中运行。

- 读取 B（认知状态对比基线），不加载 C 和 D
- 提取三类信号：`[cognition]` `[thinking]` `[preference]`
- 只写 A，不做去重和路由决策
- Reference 文件：`references/signal-formats.md`、`references/extract-output.md`

### `/contour:sync`

读取 A，分发信号到 B/C，清空 A。**必须在新的专用 session 中运行**。

- 读取 A + B + D，**不读取 C**（C 只追加）
- `[cognition]` → 对比 B 更新认知状态（含回退处理）→ 追加到 C
- `[thinking]` → 追加到 C → 对照 D 判断是否记录 `[core-candidate]`
- `[preference]` → 域内更新 B 通信规则；跨域记录为 `[core-candidate]`
- 语义去重 → 清空 A → 报告结果
- Reference 文件：`references/b-structure.md`、`references/c-structure.md`

---

## 工作流程

### 首次安装

```
1. 通过 /plugin 安装 contour plugin
2. 运行 /contour:setup
   └─ 创建数据目录和初始文件（A/B/C/D）
   └─ 往 ~/.claude/CLAUDE.md 注入 D 和 B 的加载指令 + 监测规则
3. 重启 Claude Code，验证 D 和 B 是否正常加载
```

### 日常流程

```
1. 在任意工作区启动 CC，正常工作
   └─ CLAUDE.md 自动加载 D+B → CC 知道用户认知状态
   └─ 工作中实时识别并更新 B（主力机制）
2. Session 结束时或之后通过 --resume 恢复，运行 /contour:extract
   └─ 读取 B + 扫描 session 对话 → 写入 A
   └─ 作为主力机制的补网
3. 时机合适时在新 session 中运行 /contour:sync（可攒多次 extract 后再 sync）
   └─ 读 A+B+D → 分发到 B/C → 清空 A
```

---

## 扩展规则

> **阶段二扩展**，MVP 不实现。

新增不熟悉的领域：添加 `{user}-{domain}.md` (B) + `{user}-{domain}-log.md` (C)。extract 和 sync 按信号内容领域路由，不按来源工作区，无需新建 skill。多 domain 的 CLAUDE.md 注入策略（工作区级注入）在阶段二一并设计。

---

## 关键原则

1. **防污染**：domain 文件隔离；/sync 在新 session 运行；C 只追加不读取；D 手动更新
2. **极简**：B 保持轻量快照，C 可增长但不常加载
3. **低成本**：D+B 通过 CLAUDE.md 加载；/extract 扫一次 session 写 A；/sync 读 A+B+D 不重扫 session 不读 C
4. **可见性**：所有文件可读、可审视、可手动编辑
5. **系统提建议，人做决策**：core 候选、认知回退等关键变更提示用户确认

---

## 下一步

### 高优先级

- [x] 架构设计 v5 完成
- [x] `/extract` prompt 设计完成（英文部署版）
- [x] `/sync` prompt 设计完成（英文部署版）
- [x] Reference 文件完成（signal-formats、extract-output、b-structure、c-structure）
- [x] CLAUDE.md 监测指令设计完成 → `skills/setup/references/claude-md-injection.md`
- [x] D 文件初始化引导设计完成 → `skills/setup/references/d-structure.md`
- [x] `/contour:setup` SKILL.md 完整实现（9 步流程）
- [x] `plugin.json` 编写 + GitHub 仓库创建
- [ ] **在真实工作 session 中部署测试（5-10 轮 extract + sync）← 当前最高优先级**

### 中优先级

- [ ] README 撰写（中英文）
- [ ] 验证认知追踪的准确性
- [ ] 验证去重和防污染效果

### 低优先级

- [ ] 多 domain 的 /sync 扩展策略
- [ ] C 文件的长期管理（是否需要按时间分割）
