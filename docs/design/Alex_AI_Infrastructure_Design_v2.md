# Alex 个人AI基础设施设计文档

**最后更新**: 2026-02-16
**状态**: 架构设计完成，待实现custom commands

---

## 核心目标

为Claude Code建立一个**自动、低成本、细颗粒度、防污染**的个人信息系统。

解决三个问题：

1. **污染**：多层AI总结造成信息失真
2. **颗粒度不足**：粗粒度标签导致沟通两极化（"程序员"或"非程序员"的二分法）
3. **上下文污染**：不相关信息被引入当前session

---

## 运行环境

- **仅在Claude Code中运行**
- 工作区 = Windows本地项目文件夹（如 `D:\Content_Creator`、`D:\Life_with_AI`）
- 每个工作区有独立的 `.claude/claude.md`（极简，仅去歧义指令）
- Custom commands为全局配置，位于 `C:\Users\pc\.claude\commands\`

---

## 文件系统结构

所有AI基础设施文件集中存放：

```markdown
D:\Life_with_AI\profile\ai-infra\
├── extract-buffer.md         (A) 临时提取缓冲，/sync后清空
├── Alex-core.md              (D) 人格级：思维方式、核心偏好、价值观
├── Alex-coder.md             (B) 代码领域：认知缺陷 + 认知转化状态
├── Alex-coder-log.md         (C) 代码领域：完整演变记录（认知+思维）
└── Alex-writer.md                 写作领域：静态偏好文件，无需追踪
```

全局custom commands通过绝对路径访问这些文件，不受CC启动目录限制。

---

## 文件职责定义

### extract-buffer.md (A)

**目的**：单次session提取的临时缓冲层。

**为什么需要A**：避免多个command重复扫描同一个session的完整context。一次提取，所有信号写入A；后续分发时读A而非重扫session，降低token成本。

**特征**：

- 由 `/extract` 写入
- 由 `/sync` 读取并清空
- 用标签区分信号类型（如 `[cognition]` `[thinking]` `[preference]`）
- 不加载任何其他md文件，成本最低

### Alex-core.md (D)

**目的**：Alex这个人的根本特征，所有工作区都可读。

**内容维度**：

- 思维方式（如何论证、如何取舍、优先级）
- 核心偏好（沟通风格、工作方式、禁忌）
- 价值观（什么重要、什么反感）

**特征**：

- 变化频率极低（半年到一年审视一次）
- 目标20-50行，稳定精简
- 是所有domain文件的"宪法"
- 由 `/sync` 在识别到显著思维变化时更新

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

### Alex-coder.md (B)

**目的**：代码领域的当前认知状态。

**内容**：

- 认知缺陷：当前不懂的
- 认知转化：从不懂变为已掌握的（标注日期）
- 通信规则：在代码语境下AI应如何沟通

**特征**：

- 由 `/sync` 动态更新
- 只记录结果，不记录过程（过程归C）
- 保持轻量（目标<50行）

**示例内容**：

```markdown
## 认知缺陷
- 环境变量为什么要分离
- PR提交的完整流程

## 已掌握
- ✓ git和github的区别（2026-02）
- ✓ .env文件的用途和管理方式（2026-01）

## 通信规则
- 用术语，但第一次要解释上下文
- 假设我有系统设计思维，但不假设代码细节
- 直接说"不行"，别说"当然可以"
```

### Alex-coder-log.md (C)

**目的**：代码领域的完整演变记录。

**内容**：

- 认知演变的完整过程（从不懂→部分理解→掌握→可能遗忘）
- 思维模式是否产生变化
- 为D（Alex-core.md）的更新提供依据

**特征**：

- 由 `/sync` 追加写入，标注执行日期
- 可以任意增长，不常加载
- 主动记录演变，不是被动存档

**示例内容**：

```markdown
## 2026-02-10 /sync
[cognition] git和github的区别：从不懂→已掌握
  - 信号来源：session中主动解释了两者区别
[cognition] PR提交流程：仍不懂
[thinking] 无新变化

## 2026-01-15 /sync
[cognition] .env文件：从不懂→已掌握
[thinking] 发现Alex开始用"防污染"框架思考所有系统设计问题
  - 可能需要更新Alex-core.md
```

### Alex-writer.md

**目的**：写作领域的静态偏好文件。

**为什么不需要完整追踪**：写作是Alex的成熟领域，不存在大量"从不懂到懂"的认知转化。认知追踪的核心前提不成立。

**特征**：

- 只记录风格偏好和沟通规则
- 半年审视一次即可
- 无需配套的mastered/log文件

---

## Custom Commands

### `/extract`

**功能**：扫描当前session，提取所有值得记录的信号，写入 extract-buffer.md (A)。

**关键约束**：

- 只读当前session context
- 只写A，不加载B/C/D任何文件
- 用标签区分信号类型：`[cognition]` `[thinking]` `[preference]`
- 仅提取，不分类、不对比、不判断去重

**文件位置**：`C:\Users\pc\.claude\commands\extract.md`

**待设计**：具体prompt内容

### `/sync`

**功能**：读取A，分发到B/C/D，然后清空A。

**具体操作**：

1. 读 extract-buffer.md (A)
2. 读 Alex-coder.md (B) + Alex-coder-log.md (C) + Alex-core.md (D)
3. `[cognition]` 信号 → 对比B，更新认知缺陷/转化状态 → 追加到C并标注日期
4. `[thinking]` 信号 → 追加到C → 如果变化显著，更新D
5. `[preference]` 信号 → 更新B的通信规则部分或D
6. 去重：与B/C现有内容语义对比，避免重复写入
7. 清空A

**文件位置**：`C:\Users\pc\.claude\commands\sync.md`

**待设计**：具体prompt内容，去重逻辑，"显著变化"的判断标准

---

## 工作流程

### 日常流程

```markdown
1. 在任意工作区启动CC，正常工作
2. Session结束时运行 /extract
   └─ 扫描当前session → 写入 extract-buffer.md (A)
   └─ 无需加载其他文件，成本最低
3. 时机合适时运行 /sync（可以攒多次extract后再sync）
   └─ 读A → 分发到B/C/D → 清空A
```

### 定期审视

```markdown
当Alex-coder.md (B) 膨胀或长时间未整理时：
1. 启动新session，运行 /sync
2. /sync 把已掌握的认知标记转化
3. 把陈旧信息归入Alex-coder-log.md (C)
4. B恢复轻量状态
```

---

## 扩展规则

新增不熟悉的领域时：

- 添加 `Alex-{domain}.md` (B) + `Alex-{domain}-log.md` (C)
- `/extract` 和 `/sync` 的prompt中增加对应domain的标签
- 模式统一，无需新建command

成熟领域（如写作）：

- 只需一个 `Alex-writer.md` 静态偏好文件
- 不启用B/C追踪机制
- 半年审视一次

---

## 关键原则

1. **防污染**：不同domain的文件内容隔离，A不携带domain之外的信息
2. **极简**：B永远保持轻量，C可以增长但不常加载
3. **低成本**：/extract只扫一次session只写A；/sync只读A不重扫session
4. **可见性**：所有文件可读、可审视、可手动编辑
5. **按需部署**：成熟领域不上完整追踪机制

---

## 下一步：设计Custom Commands的具体prompt

### 高优先级

- [ ] `/extract` 的prompt：如何识别cognition/thinking/preference信号，输出格式
- [ ] `/sync` 的prompt：分发逻辑、去重规则、"显著变化"判断标准

### 中优先级

- [ ] 各工作区 `.claude/claude.md` 的配置方式
- [ ] Alex-core.md 和 Alex-writer.md 的初始内容填充

### 低优先级

- [ ] 多domain的 /sync 扩展策略
- [ ] Alex-coder-log.md 的长期管理（是否需要按时间分割）
