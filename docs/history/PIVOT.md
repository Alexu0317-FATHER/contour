# 知界 (Contour) — Pivot 记录

> 本文件记录 Contour 从「认知状态追踪」转向「行为层路由」的过程。
> 老版本的完整快照在 tag `v0.3.0-cognitive`，本目录保留了当时的设计文档、README 与对外文章。

---

## 一、曾经的 Contour 是什么

**一句话**：一个 Claude Code 插件，追踪用户对每个知识点、每个领域的掌握程度（mastered / partial / unknown），跨会话同步，让 Claude 按用户的真实认知水平调整讲解深度。

**起点的三个问题**（2026-02-14，`design/Alex_AI_Infrastructure_Design.md`）：

1. **污染** —— 多层 AI 总结造成信息失真（Gemini 美化 → Sonnet 总结 → Claude 理解）
2. **颗粒度不足** —— 粗粒度标签导致沟通两极化（"程序员"或"非程序员"的二分法）
3. **上下文污染** —— 不相关信息被引入当前 session

**最终架构**（v0.3.0）：

| 组件 | 职责 |
|---|---|
| SessionStart hook | 确定性加载 Core Profile + Domain State |
| Stop hook + Haiku | 每轮回复后触发，语义分类认知信号，直接写 Domain State |
| `/contour:extract` | 历史补录：扫描过往会话遗漏的信号，写入 buffer |
| `/contour:sync` | 读 buffer，更新 Domain State，清空 buffer |
| `/contour:setup` / `/contour:uninstall` | 初始化与卸载，含 CLAUDE.md 注入 |

数据全部是本地纯 markdown，存在 `~/.claude/contour/`，可手改。

**它真的跑起来过**：本机 `~/.claude/contour/` 下的 Domain State 文件持续更新到 2026-03-25，比最后一次 commit 晚三周。闭环（Stop hook 写 → SessionStart 读）是实际工作的，不是设计稿。

---

## 二、演进时间线：转折点在哪

这条线不是"做了一个东西然后失败了"，是**命题在七周里被自己改了三次**。

| 日期 | 文档 | 转折点 |
|---|---|---|
| 02-14 | `Alex_AI_Infrastructure_Design.md` | 起点：防污染的个人信息系统，三个问题 |
| 02-16 | `_v2` | 架构定型，转向 custom commands 实现 |
| 02-17 | `_v3` | custom commands 设计完成 |
| 02-18 | `Alex_Contour_Design_v4.md` | 命名为「知界 Contour」。**明确划界：不是 personality profiling**，差异化核心是"追踪认知边界颗粒度" |
| 02-22 | `Alex_Contour_Design_v5.md` | **第一次真正的命题转向**：目标从"追踪认知状态"改写为"**用不让人感到被居高临下的方式沟通**"。原话——"追踪是手段，沟通体验是目的" |
| 02-27 | `Retrospective.md` | **机制选型认错**：承认 LLM 的 post-response self-check 从未成功触发过一次，改用 hook + 独立 LLM 调用 |
| 03-03 | `Alex_Contour_Expansion_Roadmap.md` | 想扩展成多 domain 的"个人认知技能树" |
| 03-04 | `Contour_Roadmap_v2.md` | **卡住的地方**：闭环确实在工作，但**用户感受不到**。核心问题变成"什么形式的『可感知』是有价值的，而不是噪音" |
| 03-15 | `BACKLOG.md` | 最后一轮未竟清单：UX 感知、Setup 迭代、多 domain 路由、VS Code 兼容性 |

**v5 那次转向是关键。**在 2026-02-22，命题事实上已经从"记录用户懂什么"挪到了"AI 该怎么跟用户说话"——只是当时仍然把认知状态当作核心数据，没意识到那只是众多输入之一。

---

## 三、为什么停下：不是做砸了，是证伪了一个命题

停下的直接原因写在 `Contour_Roadmap_v2.md` 里：**机制成立，但价值不可感知。**

再往下追一层，问题出在命题本身：

**Contour 追踪的是「你懂不懂」——事实层。**而真正决定对话体验好坏的，是「对你该怎么说」——行为层。认知状态只是行为选择的输入之一，而且是成本很高、变化很快、维护负担很重的那一种。

把事实层做到极致，也只能推导出行为的一部分。v5 已经摸到了这扇门（"沟通体验是目的"），但数据模型还停在事实层，所以越做越重，感知越做越弱。

**这个结论是自己撞出来的，不是从竞品调研里读来的。**Contour 是它自己那条论断的第一手证据。

---

## 四、哪些结论继续有效

以下判断在 pivot 后依然成立，并且正在被新方向复用：

**1. LLM 是概率机器，不是执行引擎**（`Retrospective.md`）

> 凡是"必须每次执行"的操作，不能依赖 LLM 自觉。

post-response self-check 从未成功触发过一次，原因是结构性的：模型完成主任务后自然结束 turn，元任务被系统性跳过。正确做法是拆开——**hook 负责"什么时候执行"（确定性），LLM 调用负责"执行什么"（语义）**。

**2. 「写了但不读」的基础设施是负债**（`Retrospective.md`，源自对 PAI 用户反馈的调研）

> 比"功能不可见"更糟的是"假装有功能"。

Contour 把闭环做真了，却撞上了更细的一层：**写了也读了，用户仍然感受不到。**这一条是 Contour 自己贡献的新教训。

**3. 工程层面的既有资产**

- `hooks/cognitive-monitor.ts` —— 唯一一个真跑通过的 Stop hook 实现
- VS Code hook 兼容性的根因分析（输出字段名、同步阻塞超时、触发时机差异）—— 见 `BACKLOG.md`
- `skills/setup` 与 `skills/uninstall` 的完整安装/卸载流程，含 CLAUDE.md 注入
- `.claude-plugin/` 的 marketplace 打包配置

**4. `BACKLOG.md` 里那条「Setup 迭代」的提问依然没有答案**

> 桌面端和网页端用户根本不需要建文档，Claude 本身有记忆系统……Setup 阶段能否直接读取 Claude.ai 的记忆系统？对于 Claude Code 用户，能否直接接入 CLAUDE.md？

这个问题在新方向里原样重现，仍是待实测项。

---

## 五、现在的 Contour 是什么

**方向已定，形态待定。**

新方向：从事实层（你懂什么）转向**行为层（对你该怎么说话）**——维护一份本地的、人类可读的、版本化的个人档案，并在每次对话开始时按场景把对的部分喂给模型；模型在对话中产生的新信息，由确定性脚本收回、去重、按准入规则决定是否入档。平台只是运行时，档案归用户。

截至本文件写作时，**产品定义与 MVP 边界尚未冻结**，spec 未出。已经确定的只有方向和上面那批可复用的结论。

> **待补**：新方向的 spec 定稿后，回来补完本节，并在此处链接 spec。

---

## 六、材料索引

| 位置 | 是什么 | 在仓里 |
|---|---|---|
| tag `v0.3.0-cognitive` | 认知追踪版的完整可运行快照 | ✅ |
| `docs/history/README-cognitive.zh.md` / `.md` | 老版本对外的产品说明 | ✅ |
| `docs/history/assets/` | 老 README 的配图 | ✅ |
| `BACKLOG.md`（仓根） | pivot 前最后一轮未竟清单 | ✅ |
| `docs/history/design/` | 九份设计文档 + Retrospective，思维演进的原始记录 | 仅本地 |
| `docs/history/article-*.md` | 对外文章《我一个不会代码的人，被逼得自己写了个AI插件》原稿 | 仅本地 |
| `docs/references/` | 老版本的中文参考文档与安装截图 | 仅本地 |

标「仅本地」的材料保存在开发机上，未进公开仓。本文第二节的时间线与第四节的结论，均已从这些材料中摘出，可独立阅读。

> **待补**：文章已发布版本的链接。

---

*最后更新：2026-08-07*
