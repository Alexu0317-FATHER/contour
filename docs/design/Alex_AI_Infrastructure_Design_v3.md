# Alex 个人AI基础设施设计文档

**最后更新**: 2026-02-17
**状态**: Custom commands设计完成，待实际部署测试

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
- 每个工作区有独立的 `.claude/claude.md`（极简去歧义指令 + **必须加载对应领域的B文件**，这是系统闭环运转的前提条件）
- Custom commands为全局配置，位于 `C:\Users\pc\.claude\commands\`

---

## 文件系统结构

所有AI基础设施文件集中存放：

```
D:\Life_with_AI\profile\ai-infra\
├── extract-buffer.md         (A) 临时提取缓冲，/sync后清空
├── Alex-core.md              (D) 人格级：思维方式、核心偏好、价值观
├── Alex-coder.md             (B) 代码领域：认知状态表格 + 通信规则
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
- 读取对应领域的B文件用于认知状态对比，不加载C和D

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
- `/sync` 不直接修改D；发现可能需要更新D的信号时，在C中记录 `[core-candidate]`，由用户手动审视后决定是否更新

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
- 认知状态表格：每个知识点的当前状态（认知缺陷/部分理解/已掌握）及更新时间
- 通信规则：在代码语境下AI应如何沟通

**特征**：
- 两个更新来源：工作区claude.md指令在工作session中实时更新（主力） + `/extract`+`/sync` 补网
- 只记录结果，不记录过程（过程归C）
- 保持轻量（目标<50行）

**示例内容**：
```markdown
## 认知状态

| 知识点 | 认知缺陷 | 部分理解 | 已掌握 | 更新时间 |
|--------|---------|---------|--------|----------|
| PR提交的完整流程 | | | ✓ | 2026-02 |
| git和github的区别 | | | ✓ | 2026-02 |
| .env文件的用途和管理方式 | | | ✓ | 2026-01 |
| 环境变量为什么要分离 | ✓ | | | 2026-01 |

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
- `/sync` 不读取C（仅追加），避免token成本和上下文噪音
- 可以任意增长，不常加载
- 供用户手动审视，包含 `[core-candidate]` 条目作为D更新的决策依据

**示例内容**：
```markdown
## 2026-02-10 /sync
[cognition] git和github的区别：认知缺陷 → 已掌握
  evidence: session中主动解释了两者区别
  source: Life_with_AI | 讨论git工作流和AI基础设施设计
[cognition] PR提交流程：新增 → 认知缺陷
  evidence: 用户提出基础概念性问题
  source: Life_with_AI | 讨论git工作流和AI基础设施设计

## 2026-01-15 /sync
[cognition] .env文件：认知缺陷 → 已掌握
  evidence: 用户在实际操作中正确配置了.env文件
  source: Content_Creator | 配置视频自动发布脚本
[thinking] 用"防污染"框架思考所有系统设计问题
  evidence: 在讨论多个不同话题时反复使用隔离和防污染作为核心论证
  source: Life_with_AI | 讨论AI基础设施架构设计
[core-candidate] 用"防污染"框架思考所有系统设计问题 — 如果模式持续可能需要更新core.md
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
- 读取当前session context（当前session或通过 --resume 恢复的历史session均可）
- 读取对应领域的B文件，用于认知状态对比（判断行为性掌握和认知回退）
- 不加载C和D
- 只写A
- 用标签区分信号类型：`[cognition]` `[thinking]` `[preference]`
- 仅提取和识别信号类型，不做目标文件的路由决策、不判断去重

**文件位置**：`C:\Users\pc\.claude\commands\extract.md`

### `/sync`

**功能**：读取A，分发到B/C，然后清空A。必须在新的专用session中运行。

**具体操作**：
1. 读 extract-buffer.md (A) + Alex-coder.md (B) + Alex-core.md (D)
2. 不读 Alex-coder-log.md (C)——C仅追加，不读取
3. `[cognition]` 信号 → 对比B，更新认知状态（含认知回退处理） → 追加到C并标注日期
4. `[thinking]` 信号 → 追加到C → 对照D判断是否为新模式或矛盾，如是则在C中记录 `[core-candidate]`
5. `[preference]` 信号 → 领域特定的更新B的通信规则；跨领域的记录为 `[core-candidate]`
6. 去重：与B/D现有内容语义对比，避免重复写入
7. 清空A

**文件位置**：`C:\Users\pc\.claude\commands\sync.md`

---

## 工作流程

### 日常流程

```
1. 在任意工作区启动CC，正常工作
   └─ 工作区claude.md加载B → CC知道用户认知状态 → 工作中实时识别并更新B（机制1）
2. Session结束时或之后任意时间通过 --resume 恢复，运行 /extract
   └─ 读取B + 扫描session对话 → 写入 extract-buffer.md (A)
   └─ 作为机制1的补网，捕获遗漏的信号
3. 时机合适时在新session中运行 /sync（可以攒多次extract后再sync）
   └─ 读A+B+D → 分发到B/C → 清空A
```

### 定期审视

```
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

1. **防污染**：不同domain的文件内容隔离；/sync在新session中运行避免上下文污染；C只追加不读取避免历史噪音干扰；D手动更新避免AI擅自修改"宪法"
2. **极简**：B永远保持轻量，C可以增长但不常加载
3. **低成本**：/extract读B+扫一次session写A；/sync读A+B+D不重扫session不读C
4. **可见性**：所有文件可读、可审视、可手动编辑
5. **按需部署**：成熟领域不上完整追踪机制

---

## 下一步

### 高优先级
- [x] `/extract` 的prompt设计完成
- [x] `/sync` 的prompt设计完成
- [ ] 在真实工作session中部署测试（5-10轮extract+sync）
- [ ] 各工作区 `.claude/claude.md` 配置B文件加载 + 实时更新指令（机制1）

### 中优先级
- [ ] Alex-writer.md 的初始内容填充
- [ ] 使用指南：B加载为必要前提、/extract可通过resume补提取、建议用户给出认知反馈
- [ ] 验证认知追踪的准确性（B文件是否真实反映认知状态）
- [ ] 验证去重和防污染效果

### 低优先级
- [ ] 示例和模板拆到独立目录（为skill打包做准备）
- [ ] 多domain的 /sync 扩展策略
- [ ] Alex-coder-log.md 的长期管理（是否需要按时间分割）
