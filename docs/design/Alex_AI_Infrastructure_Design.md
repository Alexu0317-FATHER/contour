# Alex 个人AI基础设施设计文档

**最后更新**: 2026-02-14
**讨论session**: Desktop（Claude）
**状态**: 架构设计完成，待实现

---

## 核心问题陈述

AI对Alex的理解存在三个关键问题：

1. **污染**：多层AI总结造成信息失真（Gemini美化→Sonnet总结→Claude理解）
2. **颗粒度不足**：粗粒度标签导致沟通两极化（"程序员"或"非程序员"）
3. **上下文污染**：不相关信息被引入当前session（讨论代码时突然提及家庭问题）

目标：为Claude Code建立一个**自动、低成本、细颗粒度、防污染**的个人信息系统。

---

## 解决方案架构

### 三层工作区隔离

```markdown
Desktop（claude.ai）
  └─ 思维镜子 + 监督整理
     - 不读取任何工作区档案
     - 有独立的memory系统
     - 用于关键决策和模式识别

Content_Creator工作区（写作/内容创作）
  ├─ .claude/claude.md（极简，仅去歧义指令）
  ├─ custom commands（@coder/@writer工作区分别配置）
  └─ 自动提取观察到Alex-writer.md

Life_with_AI工作区（个人/工作/育儿）
  ├─ 维护完整的个人档案
  └─ 定期审视和整理观察库

其他工作区...（按需扩展）
```

### 文件系统结构

```markdown
.claude/USER/
├── Alex-core.md
│   └── 思维方式、核心偏好、价值观（极少变化）
│
├── domains/
│   ├── coder/
│   │   ├── core.md         （现在不懂的）
│   │   ├── mastered.md     （已掌握的）
│   │   └── archive.md      （完整历史）
│   │
│   └── writer/
│       ├── core.md
│       ├── mastered.md
│       └── archive.md
│
└── observations/
    └── （待定：是否需要临时存储？）
```

---

## 核心概念定义

### Alex-core.md

**目的**：捕捉Alex这个人的根本特征，所有工作区都可读。

**内容维度**：

- 思维方式（如何论证、如何取舍、优先级）
- 核心偏好（沟通风格、工作方式、禁忌）
- 价值观（什么重要、什么反感）

**特征**：

- 变化频率极低（半年到一年审视一次）
- 大约20-50行，稳定精简
- 是所有domain-specific档案的"宪法"

**示例内容**：

```markdown
## 思维方式
- 具体→抽象的逻辑推导
- 直接指出漏洞，不怕破坏流畅性
- 工程化思维：成本效率、去重、防污染

## 核心偏好
- 极简原则：宁缺毋滥
- 讨厌被美化或夸大
- 听见优于温和
- 信息源的真实性优先于完整性

## 反感清单
- AI自动美化（"架构师思维"）
- 过度推理和比喻
- 臃肿的配置和指令
```

---

### Alex-{domain}/core.md

**目的**：当前工作区中，Alex还没掌握的认知边界。

**特征**：

- 由`/extract-cognition`定期更新
- 保持轻量级（目标<50行）
- 包含具体的知识缺口和学习阶段

**示例内容（Alex-coder/core.md）**：

```markdown
## 认知边界：不知道
- git和github的区别
- 环境变量为什么要分离
- PR提交的完整流程

## 认知边界：有基础但不理解深度
- .env文件是什么（知道它存在，不知道为什么这样设计）
- docker基础（看过dockerfile，不知道思想）

## 通信规则（在代码语境下）
- 用术语，但第一次要解释上下文
- 假设我有系统设计思维，但无论代码细节
- 直接说"不行"，别说"当然可以"
```

---

### Alex-{domain}/mastered.md

**目的**：已掌握知识的清单，用于防止"遗忘学过的东西"。

**特征**：

- 简洁列表，每条一句话
- 标注学习时间/版本（可选）
- 由`/archive-cleanup`定期从archive补充

**示例内容**：

```markdown
## 已掌握
- ✓ git基础概念和常用命令
- ✓ PR = Pull Request，及其在Github中的作用
- ✓ .env文件的用途和管理方式

## 部分掌握
- ◐ Docker概念（知道容器概念，不会写Dockerfile）
```

---

### Alex-{domain}/archive.md

**目的**：完整历史记录，不经常加载。

**特征**：

- 可以任意长（400+行无问题）
- 包含完整的学习过程记录
- 由`/extract-cognition`逐次追加
- 由`/archive-cleanup`定期整理

**结构**：

```markdown
## 学习阶段 v1（初期，时间段）
- Alex不知道：git和github的区别
- 学习信号：问过"git和github哪里不一样"
- 后续进展：已掌握

## 学习阶段 v2（中期）
- ...
```

---

## Custom Commands（设计中）

### `/extract-cognition`

**工作区**：domain工作区内运行
**输入**：当前session的对话
**输出**：更新 `Alex-{domain}/core.md` 和 `archive.md`

**待设计的细节**：

- Prompt的具体写法
- 如何判断"这是新的不懂"vs"这是复习"
- 如何对比mastered.md避免重复

---

### `/extract-thinking`

**工作区**：Content_Creator工作区运行
**输入**：当前session的对话
**输出**：提炼思维模式，更新Alex-core.md（如需要）

**待设计的细节**：

- 思维模式如何分类
- 与认知边界的区别在哪
- 多少个session要求一次review

---

### `/extract-preference`

**工作区**：domain工作区运行
**输入**：当前session的对话
**输出**：更新 `Alex-{domain}/core.md` 的通信规则部分

**待设计的细节**：

- 如何识别"隐含的偏好"
- 与思维方式的边界
- 冲突处理（多个preference相互矛盾）

---

### `/archive-cleanup`

**工作区**：任意工作区运行
**输入**：`core.md` + `archive.md` + `mastered.md` + 当前session
**输出**：

- 新的core.md（精简化）
- 新的archive.md（整理后）
- 新的mastered.md（更新进度）

**待设计的细节**：

- 去重的语义匹配算法
- "掌握"的判断标准
- 是否需要分割archive成多个版本

---

## 工作流程

### 日常流程

```markdown
1. 在Content_Creator工作区开启session
   └─ 加载.claude/claude.md（极简，3行）
   └─ 加载Alex-core.md（可选，取决于claude.md配置）
   └─ 不加载domain档案

2. 工作过程中，自然流露思维和知识边界

3. Session结束时（或定期）
   └─ 运行 `/extract-cognition`
   │   └─ 对比 core.md + mastered.md + 当前session
   │   └─ 更新 core.md 和 archive.md
   │
   └─ 运行 `/extract-thinking`（可选，不必每次）
   │   └─ 检查是否有新的思维模式要添加到Alex-core
   │
   └─ 运行 `/extract-preference`（可选）
       └─ 检查是否有新的通信偏好

4. Core.md逐步变长（预期3-6个月达到上限）
```

### 整理流程

```markdown
1. 判断condition：core.md > 50行，或者已经3个月没整理
2. 开启新session，运行 `/archive-cleanup`
   └─ 读 core.md + mastered.md + archive.md
   └─ 对比，去重
   └─ 将已掌握的从core移到mastered
   └─ 将旧信息从core移到archive
3. Core.md恢复轻量状态（<30行）
4. Archive持续增长（无所谓）
```

### Desktop审视流程

```markdown
定期（比如季度）在Desktop运行分析
- 读所有domain的Alex-core.md
- 读Alex-core.md（思维方式部分）
- 进行meta-analysis：
  └─ 是否出现新的thinking pattern
  └─ 是否有contradiction
  └─ 是否需要更新Alex-core.md
```

---

## 待讨论的实现细节

### 高优先级

- [ ] `/extract-cognition`的具体prompt
  - 如何识别新的不懂
  - 如何判断重复
  - 与mastered.md的对比逻辑
  
- [ ] `/archive-cleanup`的具体prompt
  - 去重的语义匹配
  - 迁移的标准
  
- [ ] 工作区级别的claude.md配置
  - Content_Creator中如何指向Alex-writer
  - Coder工作区如何指向Alex-coder
  - YAML格式还是注释形式

### 中优先级

- [ ] `/extract-thinking`的设计
  - 思维模式的分类方法
  - 与认知边界的清晰区分
  
- [ ] `/extract-preference`的设计
  - 隐含偏好如何识别
  - 通信规则的具体格式
  
- [ ] Desktop的meta-analysis prompt

### 低优先级

- [ ] 是否需要observations.md这个中间层
- [ ] Archive的版本管理策略
- [ ] 多个domain之间的跨越性学习

---

## 下一步行动

1. **新session中讨论**：
   - 确定每个command的具体prompt
   - 设计工作区级别的配置方式
   - 原型测试第一个command

2. **原型实现**：
   - 在Content_Creator工作区创建.claude/USER结构
   - 实现第一个custom command `/extract-cognition`
   - 运行3-5个session进行测试和迭代

3. **收集反馈**：
   - 观察效果是否符合预期
   - 调整prompt和文件结构
   - 逐步加入其他commands

---

## 关键原则（重申）

1. **防污染**：不同domain的档案相互隔离
2. **极简**：core档案永远保持轻量级
3. **自动性**：custom commands自动运行，不需要手工维护
4. **可见性**：所有档案都可读、可审视、可编辑
5. **成本意识**：避免频繁加载大文件，防止context爆炸

---

**本文档是架构设计，具体实现细节将在下一个session中讨论。**
