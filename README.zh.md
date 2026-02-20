# 知界 (Contour)

[English](README.md) | 中文

为 Claude Code 提供细粒度的认知状态追踪。

大多数 AI 工具要么把你当成专家，要么把你当成新手。知界 (Contour) 能够精确追踪你对每个知识点、每个领域的掌握程度——什么是你已经精通的，什么是你一知半解的，什么是你完全不懂的——并在不同的会话之间保持这些状态的同步。

## 前置要求

- 已安装 Node.js 环境
- 能够运行 `npx` 命令
- 已安装并配置好 [Claude Code](https://claude.ai/code)

## 安装指南

### 快速安装 (推荐)

```bash
npx skills add Alexu0317-FATHER/contour
```

### 注册为插件市场

在 Claude Code 中运行以下命令：

```bash
/plugin marketplace add Alexu0317-FATHER/contour
```

### 安装技能

**方式 1：通过浏览界面安装**

1. 在 Claude Code 中运行 `/plugin`
2. 选择 `Browse and install plugins`
3. 选择 `contour`
4. 选择你想要安装的插件
5. 选择 `Install now`

**方式 2：直接安装**

```bash
/plugin install contour@Alexu0317-FATHER/contour
```

## 更新指南

要将知界更新到最新版本：

1. 在 Claude Code 中运行 `/plugin`
2. 切换到 `Marketplaces` 标签页 (使用方向键或 Tab 键)
3. 选择 `contour`
4. 选择 `Update marketplace`

你也可以启用自动更新 (Enable auto-update) 来自动获取最新版本。

## 工作原理

知界为每个领域使用四个本地文件：

- **核心画像 (Core Profile)** (`{user}-core.md`) — 你的沟通偏好画像。全局加载，极少变动。
- **领域状态 (Domain State)** (`{user}-{domain}.md`) — 你在特定领域的认知状态快照。持续更新。
- **领域日志 (Domain Log)** (`{user}-{domain}-log.md`) — 仅追加的审计日志。供你回顾使用。
- **提取缓冲区 (Extract Buffer)** (`extract-buffer.md`) — 跨会话的信号缓冲区。

两种更新机制并行运行：

1. **实时监控** — 注入到 `CLAUDE.md` 中的指令会在你工作时检测认知变化，并静默更新领域状态。
2. **提取与同步** — `/contour:extract` 扫描会话中的认知信号；`/contour:sync` 将它们分发到领域状态和领域日志中。

## 可用命令

| 命令 | 何时运行 | 作用 |
|---------|-------------|--------------|
| `/contour:setup` | 安装后运行一次 | 初始化你的核心画像、领域状态、领域日志和提取缓冲区文件，并将监控指令注入到 `CLAUDE.md` 中 |
| `/contour:extract` | 在一个重要的会话结束时 | 扫描会话中的认知信号，写入缓冲区 |
| `/contour:sync` | 在一个新的专用会话中 | 读取缓冲区，更新领域状态和领域日志，清空缓冲区 |
| `/contour:uninstall` | 当你想移除知界时 | 从 `CLAUDE.md` 中移除监控指令，可选择删除数据文件 |

### /contour:setup

为你的工作区初始化知界环境。

```bash
/contour:setup
```

**作用：**
- 在你的本地目录中创建必要的数据文件（核心画像、领域状态等）。
- 将实时监控指令注入到你工作区的 `CLAUDE.md` 文件中。
- **注意：** 设置完成后，请重启 Claude Code 以激活实时监控指令。

### /contour:extract

从当前会话中提取认知信号。

```bash
/contour:extract
```

**何时使用：**
在一个重要的工作会话结束时运行此命令，特别是当你学习了新概念或展示了对现有概念的掌握时。它会扫描对话历史，并将检测到的信号写入提取缓冲区。

### /contour:sync

将提取的信号同步到你永久的认知状态中。

```bash
/contour:sync
```

**何时使用：**
在一个新的、专用的会话中运行此命令（以避免上下文污染）。它会读取提取缓冲区，更新你的领域状态和领域日志，然后清空缓冲区。

### /contour:uninstall

从你的工作区中移除知界。

```bash
/contour:uninstall
```

**作用：**
- 从你的 `CLAUDE.md` 中移除知界的监控指令。
- 可选择提示你删除本地数据文件。

## 环境配置与数据文件

默认存储在 `~/.claude/contour/` 目录下。

你可以通过在系统或 `.env` 文件中设置 `$AI_INFRA_DIR` 环境变量来覆盖默认的存储位置：

```bash
export AI_INFRA_DIR="/path/to/your/custom/dir"
```

所有文件都是纯 Markdown 格式 —— 可读、可编辑，且完全属于你。

## 自定义

因为知界将你的认知状态存储在纯 Markdown 文件中，你可以随时手动编辑它们。

- 想要强制 Claude 在特定领域把你当成专家？打开你的 `{user}-{domain}.md` 文件，手动将概念的状态更新为 `mastered`。
- 想要调整你的沟通偏好？编辑你的 `{user}-core.md` 文件。

知界会在下一次会话中尊重你的手动修改。

## 免责声明

- **文件修改：** `/contour:setup` 命令会修改你当前工作区下的 `CLAUDE.md` 文件，以注入监控指令。
- **数据隐私：** 所有的认知状态追踪都在你的本地机器上进行。知界本身不会将任何数据发送到外部服务器（尽管 Claude Code 会像往常一样将提示词发送给 Anthropic 的 API）。

## 版本

`v0.2.1` — 预发布版本。正在积极测试中。

## 开源协议

MIT