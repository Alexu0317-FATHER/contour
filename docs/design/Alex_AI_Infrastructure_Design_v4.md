# Alex 个人AI基础设施设计文档 v4

**最后更新**: 2026-02-17
**状态**: Skill架构设计完成，待实际部署测试

---

## 核心目标

为Claude Code建立一个**自动、低成本、细颗粒度、防污染**的个人信息系统。

解决三个问题：

1. **污染**：多层AI总结造成信息失真
2. **颗粒度不足**：粗粒度标签导致沟通两极化（"程序员"或"非程序员"的二分法）
3. **上下文污染**：不相关信息被引入当前session

**核心差异化价值**：不是personality profiling，不是"让AI更了解你"。核心是**追踪用户在不熟悉领域的认知边界颗粒度**——哪些懂、哪些半懂、哪些不懂。D文件（人格/思维方式）是辅助校准沟通方式，B文件（认知状态表）才是系统的差异化核心。

---

## 运行环境

- **仅在Claude Code中运行**
- 以 **Plugin** 形式发布到GitHub，通过 `/plugin` 安装
- 安装后通过 `/ai-infra:setup` 完成初始化
- 数据文件默认存储位置：`~/.claude/ai-infra/`，可通过环境变量 `$AI_INFRA_DIR` 覆盖
- Skill以命名空间形式调用：`/ai-infra:setup`、`/ai-infra:extract`、`/ai-infra:sync`

---

## 文件系统

### 数据文件（用户本地）

存放在 `$AI_INFRA_DIR`（默认 `~/.claude/ai-infra/`）：

```markdown
~/.claude/ai-infra/
├── extract-buffer.md         (A) 临时提取缓冲，跨session数据桥梁
├── {user}-core.md            (D) 人格级：思维方式、核心偏好、价值观
├── {user}-coder.md           (B) 代码领域：认知状态表格 + 通信规则
└── {user}-coder-log.md       (C) 代码领域：完整演变记录
```

> `{user}` 为用户名，由 `/ai-infra:setup` 初始化时设定。

### Plugin文件（GitHub仓库）

```markdown
ai-infra/                               # GitHub repo root = plugin root
├── .claude-plugin/
│   └── plugin.json                      # Plugin元数据
├── skills/
│   ├── setup/
│   │   └── SKILL.md                     # 冷启动引导：生成D/B + 注入CLAUDE.md引用
│   ├── extract/
│   │   ├── SKILL.md                     # 英文版，实际部署文件
│   │   └── references/
│   │       ├── signal-formats.md        # 三类信号的记录格式
│   │       └── extract-output.md        # A的写入格式和报告模板
│   └── sync/
│       ├── SKILL.md                     # 英文版，实际部署文件
│       └── references/
│           ├── b-structure.md           # B文件格式（同时作为B初始化模板）
│           └── c-structure.md           # C文件格式（同时作为C初始化模板）
├── docs/
│   └── references/
│       ├── extract_chinese.md           # /extract 中文参考版（不部署）
│       └── sync_chinese.md             # /sync 中文参考版（不部署）
├── .gitignore
└── README.md
```

**语言策略**：`/ai-infra:setup` 第一步让用户选择语言（中文/English）。选择后，所有用户交互输出（description、报告、引导文案）和生成的ABCD文件内容均使用该语言。Skill内部prompt始终使用英文。中文版extract/sync仅作为设计参考文档，不参与运行。

---

## ABCD文件职责

### A — extract-buffer.md

**目的**：跨session的数据传递桥梁。

/extract在目标session中扫描对话并写入A → /sync在新session中运行（为防污染，不在工作session中执行），无法访问原session的对话 → A是两个skill之间唯一的数据通道。

**特征**：

- 由 `/ai-infra:extract` 追加写入
- 由 `/ai-infra:sync` 读取并清空
- 用标签区分信号类型：`[cognition]` `[thinking]` `[preference]`

### D — {user}-core.md

**目的**：用户的根本特征。所有session的"宪法"。

**内容维度**：思维方式、核心偏好、价值观。

**特征**：

- **全局加载**：`/ai-infra:setup` 在 `~/.claude/CLAUDE.md` 中注入引用指令，每个session自动生效
- 变化频率极低（半年到一年审视一次），目标20-50行
- `/ai-infra:sync` 不直接修改D；发现可能需要更新D的信号时，在C中记录 `[core-candidate]`，由用户手动决策

**D的初始化要点**：

- 只保留影响AI沟通方式的核心特征
- 必须剔除与认知追踪无关的内容（如工作作风、职业技能描述）
- 用户有现成文档时需过滤提取，而非直接照搬

### B — {user}-coder.md

**目的**：代码领域的当前认知状态快照。

**内容**：认知状态表格（知识点 × 认知缺陷/部分理解/已掌握 × 更新时间）+ 领域内通信规则。

**特征**：

- 追求轻量，只记录结果不记录过程（过程归C）
- 初始化时以 `b-structure.md` 为模板生成
- 两个更新来源：
  1. **主力机制**：CLAUDE.md中的监测指令，在工作session中实时识别认知变化并更新B
  2. **补网机制**：`/ai-infra:extract` + `/ai-infra:sync`，捕获主力机制遗漏的信号

### C — {user}-coder-log.md

**目的**：代码领域的完整演变记录，供用户手动审视。

**内容**：认知演变全过程 + 思维模式变化 + `[core-candidate]` 条目。

**特征**：

- 由 `/ai-infra:sync` 追加写入，标注执行日期
- **只追加，不读取**——避免token成本和上下文噪音
- 初始化时以 `c-structure.md` 为模板生成

---

## CLAUDE.md加载指令

`/ai-infra:setup` 在 `~/.claude/CLAUDE.md`（全局）中注入以下指令：

**D的加载**：引用 `{user}-core.md`，每个session自动生效。

**B的加载 + 监测规则**：

- 引用对应domain的B文件
- 包含认知监测规则（何时识别为认知变化）和发现变化时的更新动作
- 单domain用户：注入全局CLAUDE.md；多domain用户：注入各工作区CLAUDE.md

> 具体的CLAUDE.md prompt文案（监测规则 + 更新动作）待设计。见"下一步"。

**关于 `--resume` 的行为**：CC在resume时会重新读取当前CLAUDE.md，所以监测指令对resumed session中的新交互生效。但AI不会主动回扫旧对话历史——旧session的全面信号提取只能靠 `/ai-infra:extract`。

---

## Skills

三个skill均设置 `disable-model-invocation: true`，仅由用户手动调用。

### `/ai-infra:setup`

冷启动引导。执行流程：

1. **选择语言**（中文/English）——决定后续所有交互和生成文件的语言
2. 检测数据目录是否已存在（已存在 → 提示覆盖或跳过；不存在 → 创建）
3. 询问用户名
4. **生成D**：
   - 场景A（用户有现成文档）→ 读取并过滤提取，剔除无关内容
   - 场景B（用户无文档）→ 通过3-5个关键问题引导生成最小可用版本
   - 生成后展示给用户确认
5. **生成B**：询问追踪领域 → 以 `b-structure.md` 为模板生成空表格 + 基础通信规则
6. **生成C**：以 `c-structure.md` 为模板创建空日志
7. **创建A**：创建空的 `extract-buffer.md`
8. **注入CLAUDE.md**：将D引用、B引用及监测指令写入全局或工作区CLAUDE.md
9. 报告初始化结果

### `/ai-infra:extract`

扫描当前session对话，提取信号写入A。在目标session中运行（当前session或通过 `--resume` 恢复的历史session）。

- 读取B（认知状态对比基线），不加载C和D
- 提取三类信号：`[cognition]` `[thinking]` `[preference]`
- 只写A，不做去重和路由决策
- Reference文件：`references/signal-formats.md`、`references/extract-output.md`

### `/ai-infra:sync`

读取A，分发信号到B/C，清空A。**必须在新的专用session中运行**。

- 读取A + B + D，**不读取C**（C只追加）
- `[cognition]` → 对比B更新认知状态（含回退处理）→ 追加到C
- `[thinking]` → 追加到C → 对照D判断是否记录 `[core-candidate]`
- `[preference]` → 领域特定的更新B通信规则；跨领域的记录为 `[core-candidate]`
- 语义去重 → 清空A → 报告结果
- Reference文件：`references/b-structure.md`、`references/c-structure.md`

---

## 工作流程

### 首次安装

```markdown
1. 通过 /plugin 安装 ai-infra plugin
2. 运行 /ai-infra:setup
   └─ 创建数据目录和初始文件（A/B/C/D）
   └─ 往 ~/.claude/CLAUDE.md 注入D和B的加载指令 + 监测规则
3. 重启Claude Code，验证D和B是否正常加载
```

### 日常流程

```markdown
1. 在任意工作区启动CC，正常工作
   └─ CLAUDE.md自动加载D+B → CC知道用户认知状态
   └─ 工作中实时识别并更新B（主力机制）
2. Session结束时或之后通过 --resume 恢复，运行 /ai-infra:extract
   └─ 读取B + 扫描session对话 → 写入A
   └─ 作为主力机制的补网
3. 时机合适时在新session中运行 /ai-infra:sync（可攒多次extract后再sync）
   └─ 读A+B+D → 分发到B/C → 清空A
```

---

## 扩展规则

新增不熟悉的领域：添加 `{user}-{domain}.md` (B) + `{user}-{domain}-log.md` (C)。extract和sync按信号内容领域路由，不按来源工作区，无需新建skill。

---

## 关键原则

1. **防污染**：domain文件隔离；/sync在新session运行；C只追加不读取；D手动更新
2. **极简**：B保持轻量快照，C可增长但不常加载
3. **低成本**：D+B通过CLAUDE.md加载；/extract扫一次session写A；/sync读A+B+D不重扫session不读C
4. **可见性**：所有文件可读、可审视、可手动编辑
5. **系统提建议，人做决策**：core候选、认知回退等关键变更提示用户确认

---

## 下一步

### 高优先级

- [x] 架构设计v4完成
- [x] `/extract` prompt设计完成（英文部署版）
- [x] `/sync` prompt设计完成（英文部署版）
- [x] Reference文件完成（signal-formats、extract-output、b-structure、c-structure）
- [ ] `/ai-infra:extract` 和 `/ai-infra:sync` 的SKILL.md封装（frontmatter + 相对路径引用 + 中文description）
- [ ] `plugin.json` 编写
- [ ] GitHub仓库创建 + plugin文件结构搭建
- [ ] 在真实工作session中部署测试（5-10轮extract+sync）
- [ ] CLAUDE.md监测指令prompt设计（监测规则 + 发现认知变化时的动作）
- [ ] D文件初始化引导文案设计（场景A：用户有现成文档；场景B：用户无文档）
- [ ] `/ai-infra:setup` 的SKILL.md设计

### 中优先级

- [ ] README撰写（中英文）
- [ ] 验证认知追踪的准确性
- [ ] 验证去重和防污染效果

### 低优先级

- [ ] 多domain的 /sync 扩展策略
- [ ] C文件的长期管理（是否需要按时间分割）
