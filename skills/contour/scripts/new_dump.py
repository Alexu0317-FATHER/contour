#!/usr/bin/env python3
"""生成一个合规的倾倒包骨架：唯一 dump_id、带时区的时间戳、正确的路径。

用法：
    python new_dump.py <实例仓路径> <endpoint-id> <baseline|incremental|verification>
                       [--model MODEL] [--provider P] [--surface S]
                       [--trigger user|probe] [--last-revision REV]
                       [--previous-dump-id ID]

为什么要脚本：dump_id 唯一性、ISO 8601 带时区、路径正确——
这些是确定性的活，让模型每次现编只会引入不一致。
语义部分（真正写内容）仍然归模型。

规范见 references/protocol.md。
"""

import argparse
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

SKELETON = """---
schema_version: contour-dump-v1
dump_id: {dump_id}
endpoint_id: {endpoint_id}
provider: {provider}
surface: {surface}
model: {model}
captured_at: {captured_at}
dump_type: {dump_type}
trigger: {trigger}
memory_scope: unknown
source_method: model-self-report
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

### 当前会话现场推断

### 已加载的知界文件

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
    p.add_argument("instance_repo", help="实例仓根目录")
    p.add_argument("endpoint_id", help="稳定端标识，全小写，不含模型名")
    p.add_argument("dump_type", choices=["baseline", "incremental", "verification"])
    p.add_argument("--model", default="unknown")
    p.add_argument("--provider", default="unknown")
    p.add_argument("--surface", default="web",
                   choices=["web", "desktop", "code", "cli"])
    p.add_argument("--trigger", default="user", choices=["user", "probe"],
                   help="MVP 只有这两种：所有倾倒都由用户确认后发起")
    p.add_argument("--last-revision", default="null",
                   help="本端最后读到的统一版本")
    p.add_argument("--previous-dump-id", default="null",
                   help="incremental 必填")
    p.add_argument("--contour-loaded", default="unknown",
                   choices=["true", "false", "unknown"])
    args = p.parse_args()

    if args.endpoint_id != args.endpoint_id.lower():
        p.error("endpoint_id 要全小写")
    if args.dump_type == "incremental" and args.previous_dump_id == "null":
        p.error("incremental 包必须给 --previous-dump-id")

    now = datetime.now(timezone.utc).astimezone()
    stamp = now.strftime("%Y%m%dT%H%M%S%z")

    target_dir = Path(args.instance_repo) / "dumps" / "inbox" / args.endpoint_id
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{stamp}__{args.dump_type}.md"

    if target.exists():
        # 包不可变：绝不覆盖已存在的文件。
        print(f"已存在，拒绝覆盖：{target}", file=sys.stderr)
        return 1

    target.write_text(SKELETON.format(
        dump_id=str(uuid.uuid4()),
        endpoint_id=args.endpoint_id,
        provider=args.provider,
        surface=args.surface,
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
