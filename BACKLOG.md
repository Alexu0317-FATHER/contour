# Contour — Backlog

> 零碎想法、小迭代需求、已知问题的唯一落脚点。
> 大方向看 Roadmap，已完成的看 CHANGELOG。

---

## 🔥 Next Up（下个 session 要干）

- [ ] **UX 体验迭代：方向 B 子问题讨论**（优先级最高）
  方向已初步明确（2026-03-04），但方案未最终拍板，先讨论再写代码：
  1. AI「自然带出」mastery 感知——prompt 层 vs hook 层注入，哪个更不脆弱？
  2. 频率控制——每次变化都注入 vs 设累积阈值？
  3. `mastery-events.jsonl` 读后清空 vs 保留归档？
  4. 另外一种提醒：当用户本身身份不包含在领域内。比如Alex是文案，但是在Windows系统管理/代码领域里里体现出一定的知识量，可以适时的夸一波，这也是一种用户体验。
  5. 还有一种交互上的问题：与AI磨合，AI倾向于使用数据库的内容，但是数据库往往是过时的。如果不存入记忆，AI就会一直使用过时的信息。沟通频率较高的一些新内容，会让用户觉得很烦。比如全局Memory.md中记载了Claude自家产品线的知识。对于用户来说，默认CC应该懂自家产品线的知识，但反常识的是，不仅Claude，所有AI， Gemini, Chatgpt都不具备自家产品线的最新知识，更不可理解的是，即便记在了Memory，但是也不调用，比如Cowork，CC会理解成腾讯的在线会议软件，其实明明在memory里记载了这是Anthropic近期推出的新功能。再比如最近火爆的新项目OpenClaw，这种东西AI没有记忆，但是会自己理解为用户输入错了产品名称。
  > ⚠️ 当前最优探索路径，但尚未最终确定——下个 session 先把子问题讨论清楚。

- [ ] **Setup迭代**（优先级次于 UX）**
  目前的初始化只问用户有没有建立个人文档。然而，很多人并不会单纯搞个文件（比如Alexprofile.md）来记录。
  相反，使用Claude Code的用户可能会记在Claude.md,或者memory.md,这中间存在信息重叠；
  桌面端（Claude Desktop）和网页端Claude.ai用户根本不需要记，Claude本身有个记忆系统，会根据聊天记录自动构建用户画像。
  那么Setup阶段，对于桌面或网页端用户，能否读取Claude.ai的记忆系统？能否直接接入Claude.ai，而不要求用户建立个人文档？
  对于Claude Code用户，能否直接接入Claude.md，而不要求用户建立个人文档？（{user}-core.md）？

- [ ] **Stop hook 多 domain 路由**（优先级次于 UX）
  当用户有多个 domain 文件（alex-coder.md、alex-writing.md）时，Stop hook 如何路由到正确的 Domain State 文件？

---

## 🌐 跨 IDE 兼容性（多端支持方向）

- [ ] **Stop hook VS Code 兼容性修复**（2026-03-03 发现）

  **根因（已确认）：**
  1. **输出字段名不同**：Claude Code 不读 hook stdout；VS Code 要求 `{ "continue": true }`，而不是 `shouldContinue`。
  2. **同步阻塞超时**：`cognitive-monitor.ts` 用 `execSync` 同步调用 `claude -p --model haiku`，耗时 10-30 秒。VS Code hook 有 timeout（默认 15s），超时直接杀进程 → `unknown` finish reason → "Sorry, no response was returned"。
  3. **触发时机不同**：Claude Code 的 Stop hook 在整轮对话结束后触发（副作用）；VS Code 把它当工具调用循环之间的"继续？"检查点，阻塞 Notion 等 MCP 工具调用。

  **方案（已设计，待实现）：**
  将 `cognitive-monitor.ts` 拆成两层：
  - **主进程**（< 100ms）：立刻输出 `{ "continue": true }` → spawn detached 子进程 → `process.exit(0)`
  - **Worker 子进程**：承接原有全部逻辑（读 transcript → 调 Haiku → 写 Domain State）

  Claude Code 不受影响（不读 hook 输出、无 timeout）。

  **Haiku 认证说明：** VS Code 环境下 `claude CLI` 调用走 `~/.claude/` token，Claude Pro 用户无需额外配置。无 Claude Code 的纯 Copilot 用户需要 fallback 到 `ANTHROPIC_API_KEY`（Icebox，暂不做）。

---

## 🐛 已知问题 / 未通过测试

- [ ] **TC-05 缺失文件告警** 未通过
- [ ] **TC-09 Extract Buffer 保护** 未通过
- [ ] **验证去重和防污染效果**（Roadmap 里程碑 9）

---

## 💭 Ideas（有想法但还没想清楚）

---

## 🧊 Icebox（想到了但暂不做）

- Chrome 插件跨平台方案（Roadmap 阶段三长期）
- Claude.ai / Coworks 文件系统缺失的替代方案（外部存储 / Notion）
- Domain State 按子领域分块 + 渐进式加载（Roadmap 阶段二）

---

## ✅ 近期已完成（归档参考）

> 详见 CHANGELOG.md 和 docs/references/session-summary-2026-03-03.md

- Stop hook 写入目标确认（直接写 Domain State，不经 extract-buffer）
- extract/sync 从 Clarity Signal 改为 Inquiry Signal，全项目同步
- slash command 硬过滤（`/` 开头直接 exit，不进 Haiku）
- extract/sync 定位措辞修正（历史补录 vs 实时监控，不是主次关系）
- Domain Log 移除
- README 中英文工作原理段落重写
