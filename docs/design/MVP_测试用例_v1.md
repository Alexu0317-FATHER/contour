# 知界 (Contour) MVP 测试用例（单用户版）

**适用范围**：当前仅面向单用户、自用场景的 MVP 验证。

---

## 测试目标

验证三条核心链路：
1. `/contour:setup` 初始化可用
2. 工作中监测 + `/contour:extract` + `/contour:sync` 可形成闭环
3. 文件写入安全（不误覆盖、不丢数据）

---

## 用例清单

### TC-01 首次初始化（Smoke）
**前置条件**：空环境（无现有 contour 数据目录）

**步骤**：
1. 运行 `/contour:setup`
2. 按流程完成设置（可走 Scenario B）

**预期结果**：
- 成功创建 A/B/C/D 文件
- 输出中包含重启 Claude Code 提示
- 文件路径与命名符合 setup 输入

---

### TC-02 语言优先级正确
**步骤**：
1. 在 Step 1 选择中文
2. 继续完成 setup 对话

**预期结果**：
- 后续 setup 交互保持中文
- Scenario B 中不再重复询问语言

---

### TC-03 Scenario B 的 Q1 空值重问
**步骤**：
1. 进入 Scenario B
2. 在 Q1 提交空值（空格/回车）
3. 第二次输入有效回答

**预期结果**：
- 系统会重问一次 Q1
- 输入有效回答后流程继续

---

### TC-04 重跑 setup 的覆盖确认
**前置条件**：已存在 contour 数据文件

**步骤**：
1. 再次运行 `/contour:setup`
2. 在覆盖提示中先选取消
3. 再运行一次并选择覆盖

**预期结果**：
- 取消时不修改现有 D/B/C
- 覆盖时按规则重建 D/B/C
- A 文件遵循保护策略（见 TC-09）

---

### TC-05 缺失 D/B 文件时的告警
**步骤**：
1. 手动让 D 或 B 文件缺失（改名或移动）
2. 启动新 session

**预期结果**：
- 出现缺失告警，并提示运行 `/contour:setup`
- 会话可继续，但不执行认知追踪

---

### TC-06 监测更新不打断心流
**步骤**：
1. 正常工作对话中触发一个认知变化信号

**预期结果**：
- 不主动在对话里播报“已更新文件”
- 文件读写动作在终端可见

---

### TC-07 extract + sync 单轮闭环
**步骤**：
1. 在工作 session 中产生至少 1 条 cognition 信号 + 1 条 preference 信号
2. 运行 `/contour:extract`
3. 在新 session 运行 `/contour:sync`

**预期结果**：
- A 被消费并清空
- B 发生对应更新
- C 追加本轮记录

---

### TC-08 认知回退逻辑
**步骤**：
1. 先让某知识点在 B 中达到 partial 或 mastered
2. 再提出该知识点的基础问题
3. 执行 extract + sync

**预期结果**：
- B 中该知识点状态回退为 unknown
- C 中保留该次回退记录

---

### TC-09 A 文件保护（防数据丢失）
**前置条件**：`extract-buffer.md` 已有未同步内容

**步骤**：
1. 再次运行 `/contour:setup`

**预期结果**：
- setup 不覆盖 A 文件已有内容
- 给出提示：先运行 `/contour:sync` 再清理

---

### TC-10 Scenario A 路径（有现成文档）
**前置条件**：用户有现成的个人简介文档（如 `Alex-core.md`）

**步骤**：
1. 运行 `/contour:setup`，选择"有现成文档"
2. 提供文档路径或粘贴内容
3. 查看 D 草稿，分别测试三条确认分支：确认 / 补充内容 / 调整内容

**预期结果**：
- 草稿只保留影响 AI 沟通方式的特征，职业描述等已被过滤
- 补充/调整分支能正确更新草稿并重新确认
- 最终写入的 D 文件内容与确认稿一致

---

### TC-11 extract 无可提取信号
**步骤**：
1. 在一个纯操作性对话 session 中运行 `/contour:extract`（无认知变化、无偏好表达）

**预期结果**：
- 输出提示"No extractable signals in this session"
- `extract-buffer.md` 无新增内容

---

### TC-12 sync 时 A 文件为空
**前置条件**：`extract-buffer.md` 存在但内容为空

**步骤**：
1. 在新 session 运行 `/contour:sync`

**预期结果**：
- 输出提示"Buffer is empty, nothing to sync"并停止
- B/C 文件无任何变动

---

### TC-13 CLAUDE.md 注入不破坏原有内容
**前置条件**：`~/.claude/CLAUDE.md` 已有其他指令内容

**步骤**：
1. 运行 `/contour:setup` 完成初始化

**预期结果**：
- CLAUDE.md 原有内容完整保留
- Contour 注入块追加在文件末尾
- 注入块被 `<!-- Contour -->` 标签正确包裹

---

### TC-14 多次 extract 累积后再 sync
**步骤**：
1. 在 session 1 中产生信号，运行 `/contour:extract`
2. 在 session 2 中产生信号，运行 `/contour:extract`（不中途 sync）
3. 在新 session 中运行 `/contour:sync`

**预期结果**：
- A 文件中包含两轮 extract 的内容
- sync 正确处理全部信号（含语义去重）
- B/C 按预期更新，A 最终清空

---

## 验收标准（MVP）

满足以下条件即视为 MVP 可用：
- TC-01、TC-05、TC-07、TC-09 全部通过
- 其余用例无阻断级问题（即不影响主流程使用）
