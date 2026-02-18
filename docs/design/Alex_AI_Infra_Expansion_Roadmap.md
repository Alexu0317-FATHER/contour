# 知界 (Contour) — 扩展路线图

**创建日期**: 2026-02-16
**最后更新**: 2026-02-18
**状态**: 阶段一进行中（plugin文件结构完成，待真实session测试）

---

## 阶段一：Plugin发布到GitHub

### 可行性判断：完全可行

Claude Code的skill本质上就是markdown文件 + YAML frontmatter。这套系统的核心产物是三个skill的prompt文件（setup、extract、sync）加上一组reference模板，天然适合plugin形式发布。

### 里程碑

1. ✅ 架构设计完成（v3 custom commands → v4 skill/plugin）
2. ✅ `/extract` prompt设计完成（英文部署版）
3. ✅ `/sync` prompt设计完成（英文部署版）
4. ✅ Reference文件完成（signal-formats、extract-output、b-structure、c-structure）
5. ✅ `/contour:setup` 的SKILL.md设计
6. ✅ `plugin.json` 编写 + GitHub仓库创建
7. ⬜ 在真实工作session中跑通5-10轮extract+sync
8. ⬜ 验证认知追踪的准确性（B文件是否真实反映认知状态）
9. ⬜ 验证去重和防污染效果
10. ⬜ README撰写（中英文）
11. ⬜ 发布到GitHub

### 发布前需要解决的问题

**1. 冷启动流程**

通过 `/contour:setup` skill解决。引导用户完成D和B的初始化，注入CLAUDE.md加载指令。

核心设计约束：
- 如果用户有现成文档，需要过滤提取，剔除与认知追踪无关的内容
- 如果没有，通过3-5个问题引导生成最小可用版本
- 平衡"足够好的初始状态"和"防止AI美化/过度推理"

**2. 路径配置**

已确定方案：默认 `~/.claude/contour/`，支持 `$AI_INFRA_DIR` 环境变量覆盖。跨平台路径兼容由 `~` 语法自然处理。

**3. README**

需要讲清楚：

- 解决什么问题（颗粒度不足 + 记忆污染 + 上下文污染）
- 为什么不是又一个"AI profile generator"——核心差异是**认知边界追踪**，不是人格标签
- 与同类项目（soul.md、PAI）的定位区别：不追求人格克隆或全生命周期管家，聚焦认知颗粒度
- 使用流程和效果展示（附真实使用前后对比）
- 用户使用指南：碰到AI解释过的信息时要告诉AI，这样extract才能识别
- 环境变量配置说明

**4. 语言策略**

- Skill内部prompt：英文（部署版）
- Skill description和用户交互输出：中文
- 中文版extract/sync仅作为设计参考文档，不参与运行
- 中英文README
- 未来有需求时可做纯英文版skill

### 发布时机

**先自己跑通，再发布。** 带着真实使用数据和效果展示发布，比发一个纯架构设计有说服力得多。

---

## 阶段二：多Domain自动扩展（个人认知技能树）

### 核心构想

从单一domain（如coding）扩展为自动识别和追踪多个领域的认知状态。最终形态是一棵个人的**认知技能树**——AI在跟用户沟通不同领域内容时，动态加载对应domain的B文件，精确校准沟通颗粒度。

```
User's Cognitive Map
├── 💻 Coding      [掌握 · 部分理解 · 盲区]  active
├── 🎬 Video Edit  [掌握 · 部分理解 · 盲区]  active
├── 📊 Finance     [掌握 · 部分理解 · 盲区]  active
└── 📚 History     (未追踪)                  candidate
```

### 需要新增的机制

**1. Domain索引文件**

```markdown
# ~/.claude/contour/domains.md
| Domain | File | Status |
|--------|------|--------|
| coder | {user}-coder.md | active |
| video-editing | {user}-video-editing.md | active |
```

CLAUDE.md指令从"读取某个B文件"变成"读取domains.md索引，根据对话内容动态加载对应B文件"。索引极轻（几行），动态加载只读相关domain的B（~30行），总成本几乎不变。

**2. 自动建域流程**

```
工作session中，AI检测到用户在讨论一个未追踪的领域
  → 不自动创建（防止误判）
  → extract时标记为 [new-domain-candidate]
  → sync时提示用户确认
  → 用户确认 → 生成B+C + 更新索引
```

系统提建议，人做决策——跟D的 `[core-candidate]` 逻辑一致。

**3. Domain类型决策指南**

- 不熟悉的领域 → 完整追踪（B + C）
- 成熟领域 → 静态偏好文件（仅B，无C）
- 判断依据：该领域是否存在大量"从不懂到懂"的认知转化

**4. B文件的渐进式加载**

随着知识点增多，单个B文件可能膨胀。需要探索：

- B文件按子领域分块（如 coding 下分 git、docker、CI/CD 等子域）
- 按对话内容只加载相关子块，而非整个B
- C的结构是否需要配套优化以支持分块追踪
- 核心思路：认知追踪的颗粒度细化，但加载成本不随之线性增长

### 前提条件

- 阶段一的核心验证通过（单domain的extract+sync准确可靠）
- 真实使用中确实出现了多domain需求或单domain膨胀问题

---

## 阶段三：跨平台通用化

### 近期：其他 CLI / IDE 适配（低成本）

部分 AI 编程工具正在主动兼容 Claude Code 的 skill/plugin 格式，适配成本极低。

| 平台 | 兼容性 | 备注 |
|------|--------|------|
| VS Code (Copilot) | 待验证 | 逐步跟进 Claude Code 格式 |
| Cursor | 待验证 | 社区已有适配案例 |
| Copilot CLI | 待验证 | 命令行环境，理论可行 |
| 其他 IDE | 部分可行 | 如 Alma：全局安装 plugin 后自动识别 skill |

**策略**：以 Claude Code 为标杆，跟踪各平台兼容进展，有成熟适配方案时再跟进，不主动开发适配层。

### 长期：其他 AI 平台通用化（高工程量）

### 可行性判断：逻辑可行，但工程量级完全不同

核心逻辑是"扫描对话 → 提取信号 → 分类存储 → 按需加载"。不依赖Claude Code独有能力，依赖两个通用条件：能读写文件，能访问对话内容。

### 各平台现状

| 平台 | 自定义指令 | 文件读写 | Skill/Command | 直接平移可行性 |
|------|-----------|---------|---------------|--------------|
| Claude Code | ✅ CLAUDE.md | ✅ 完整文件系统 | ✅ skill | ✅ 当前方案 |
| Claude.ai | ✅ Project指令 | ❌ 无文件操作 | ❌ 无 | ❌ |
| ChatGPT | ✅ Custom Instructions | ❌ 无本地文件 | ❌ 无 | ❌ |
| Gemini | ✅ Gems | ❌ 无本地文件 | ❌ 无 | ❌ |

### 可能的方案

最轻量的跨平台方案：Chrome插件 + 本地存储。用户把对话记录粘贴进来或通过API拉取，前端调用AI API做提取和分类。

但这本质上变成了一个产品——需要前端、后端、API对接。工程量级远超几个markdown文件。

### 决策条件

基于阶段一二的验证结果决定是否值得投入：

- 核心逻辑是否真的有效？
- 社区反馈是否有强烈的跨平台需求？
- 投入产出比是否合理？

---

## 版本管理策略

### 版本号规则

`v{major}.{minor}.{patch}`

| 级别 | 触发条件 | 示例 |
|------|---------|------|
| major | 架构级变更（新增 domain 机制、文件结构重组） | v1→v2 |
| minor | skill 功能更新（sync 新增逻辑、新 reference 文件） | v1.0→v1.1 |
| patch | prompt 微调、bug fix、文案修改 | v1.0.0→v1.0.1 |

### 发布节奏

**先自用跑通，再发布。** 不按时间表，带真实使用数据和效果展示发布。

### 数据文件兼容性

用户本地的 ABCD 文件（`~/.claude/contour/`）是核心资产，**不能被 skill 升级破坏**。

- patch 更新：透明升级，无需用户操作
- minor 更新：说明是否需要重新运行 `/contour:setup`
- major 更新：提供迁移说明或迁移 skill

### 回滚

- Plugin 回滚：`git checkout v{old-version}` 后重新安装
- 数据文件回滚：用户自行备份（README 中说明备份建议）

---

## 关键原则

- **先验证再扩展**：核心逻辑没跑通之前，不投入任何扩展工作
- **最小可行产品**：每个阶段只做那个阶段必须做的事
- **真实数据驱动**：用自己的使用数据证明效果，而不是用架构设计说服别人
- **系统提建议，人做决策**：自动建域、core候选等关键变更都需要用户确认
