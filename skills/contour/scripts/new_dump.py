#!/usr/bin/env python3
"""生成一个倾倒包骨架（contour-dump-v2）：唯一 dump_id、带时区的时间戳、受管收件区内的路径。

这是 references/protocol.md 规则的一种本地实现。不能运行 Python 时，
按 protocol.md 用其他工具生成同样的字段即可。

用法：
    python new_dump.py <档案根目录> <store-id> <baseline|incremental|verification>
                       --collected-via <执行读取的使用端 endpoint-id 或工具名>
                       --source-method native-view|model-self-report|export|file-memory|mixed
                       [--memory-scope S] [--model MODEL] [--provider P]
                       [--trigger user|probe] [--last-revision REV]
                       [--previous-dump-id ID] [--contour-loaded true|false|unknown]

store-id 是记忆存储标识（AI 实际保存记忆的位置），不是读取它的端。
--collected-via 和 --source-method 没有默认值：它们是来源事实，必须按实际读取者和
采集方式给出，不能由脚本替调用者假定。

为什么要脚本：dump_id 唯一性、ISO 8601 带时区、路径正确——
这些是确定性的活，让模型每次现编只会引入不一致。
语义部分（真正写内容）仍然归模型。
"""

import argparse
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

# store-id 会被直接拼进路径，必须限定字符集——否则 "../escaped" 能把包
# 写到 dumps/inbox 之外，而校验器只扫 inbox，看不见它。collected_via 沿用同一字符集。
IDENTIFIER = re.compile(r"\A[a-z0-9]+(?:-[a-z0-9]+)*\Z")

SKELETON = """---
schema_version: contour-dump-v2
dump_id: {dump_id}
store_id: {store_id}
collected_via: {collected_via}
provider: {provider}
model: {model}
captured_at: {captured_at}
dump_type: {dump_type}
trigger: {trigger}
memory_scope: {memory_scope}
source_method: {source_method}
contour_context_loaded: {loaded}
last_contour_revision_read: {last_revision}
previous_dump_id: {previous_dump_id}
---

## 导出边界与已知限制

<!-- 这一端能导出到什么程度，什么拿不到。别写"全部导出"，那不成立。 -->

## 可访问的持久记忆

<!-- 每条尽量带：原话、事实发生时间或用户陈述时间、supersedes/retracts 关系。
     这些是整合时唯一能用来裁决的信息——captured_at 不参与裁决。 -->

### 身份与事实

### 正在进行的事

### 判断方式与价值排序

### 明确否决、负向约束与原因

### 沟通偏好与用户纠正

### 零散但可能跨场景复用的信息

## 记忆中的过期项、矛盾与不确定项

## 非原生记忆来源

<!-- 来源不确定时放这里或"无法确认"，不许冒充原生记忆。
     混在一起，冲突消解那步就没法工作。 -->

### 当前会话内容与推断

### 已加载的知界文件

### 已创建或更新的外部知识资产

<!-- 只放可确认的创建、更新、重命名、迁移或删除动作。
     [操作] = 当前会话或工具记录可确认；[记] = 只来自本端跨会话记忆。
     不收 [推]，也不收普通项目实现或当前工作区里本来就能定位的交付物。 -->

### 项目文件、自定义指令或其他外部资料

## 本端无法确认的内容
"""


def main():
    # Windows 控制台默认不是 UTF-8，中文提示会变乱码。显式指定。
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass

    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("instance_repo", help="档案根目录（当前文件布局方案）")
    p.add_argument("store_id", help="记忆存储标识，全小写，不含模型名")
    p.add_argument("dump_type", choices=["baseline", "incremental", "verification"])
    p.add_argument("--model", default="unknown")
    p.add_argument("--provider", default="unknown")
    p.add_argument("--collected-via", required=True,
                   help="执行读取的使用端 endpoint-id 或工具名；没有默认值，未知写 unknown")
    p.add_argument("--source-method", required=True,
                   choices=["native-view", "model-self-report", "export",
                            "file-memory", "mixed"],
                   help="本次实际的采集方式；没有默认值")
    p.add_argument("--memory-scope", default="unknown",
                   choices=["global", "project", "workspace", "mixed", "unknown"])
    p.add_argument("--trigger", default="user", choices=["user", "probe"],
                   help="本次倾倒由什么发起：user = 用户本轮请求，probe = 探测检查；"
                        "不表示授权依据")
    p.add_argument("--last-revision", default="null",
                   help="该存储所在使用端最后读到的统一版本")
    p.add_argument("--previous-dump-id", default="null",
                   help="incremental 必填")
    p.add_argument("--contour-loaded", default="unknown",
                   choices=["true", "false", "unknown"])
    args = p.parse_args()

    for name in ("store_id", "collected_via"):
        value = getattr(args, name)
        if not IDENTIFIER.match(value):
            p.error(
                f"{name} 不合规：{value!r}。"
                "只允许小写字母、数字和单个连字符分隔（claude-code-local / codex-cli）"
            )
    # 空白不等于“未知”：未知写 unknown，没有时写 null。
    for flag, value, hint in (
        ("--provider", args.provider, "未知写 unknown"),
        ("--model", args.model, "未知写 unknown"),
        ("--last-revision", args.last_revision, "没有时写 null"),
        ("--previous-dump-id", args.previous_dump_id, "没有时写 null"),
    ):
        if not value.strip():
            p.error(f"{flag} 不能为空：{hint}")
    if args.dump_type == "incremental" and args.previous_dump_id == "null":
        p.error("incremental 包必须给 --previous-dump-id")

    now = datetime.now(timezone.utc).astimezone()
    stamp = now.strftime("%Y%m%dT%H%M%S%z")
    dump_id = str(uuid.uuid4())

    inbox = (Path(args.instance_repo) / "dumps" / "inbox").resolve()
    target_dir = (inbox / args.store_id).resolve()
    # 双保险：字符集挡住已知形态，解析后的路径检查挡住符号链接一类的意外。
    if target_dir != inbox / args.store_id or inbox not in target_dir.parents:
        print(f"拒绝写到收件区之外：{target_dir}", file=sys.stderr)
        return 1

    target_dir.mkdir(parents=True, exist_ok=True)
    # 文件名带 dump_id：它是包的唯一身份，时间戳只是让目录可读。
    target = target_dir / f"{stamp}__{args.dump_type}__{dump_id}.md"

    if target.exists():
        # 包不可变：绝不覆盖已存在的文件。
        print(f"已存在，拒绝覆盖：{target}", file=sys.stderr)
        return 1

    target.write_text(SKELETON.format(
        dump_id=dump_id,
        store_id=args.store_id,
        collected_via=args.collected_via,
        provider=args.provider,
        memory_scope=args.memory_scope,
        source_method=args.source_method,
        model=args.model,
        captured_at=now.isoformat(timespec="seconds"),
        dump_type=args.dump_type,
        trigger=args.trigger,
        loaded=args.contour_loaded,
        last_revision=args.last_revision,
        previous_dump_id=args.previous_dump_id,
    ), encoding="utf-8")

    print(target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
