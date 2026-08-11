#!/usr/bin/env python3
"""校验倾倒包的 frontmatter 与正文结构是否合规。

用法：
    python validate_dump.py <倾倒包路径> [更多路径...]
    python validate_dump.py --inbox <实例仓路径>     # 校验整个 inbox

规范见 references/protocol.md。这里做的全是确定性检查——
字段在不在、值合不合法、章节缺不缺。语义判断不归它管。

退出码：0 全部通过；1 有不合规；2 用法错误。
"""

import re
import sys
from datetime import datetime
from pathlib import Path

REQUIRED_FIELDS = [
    "schema_version", "dump_id", "endpoint_id", "provider", "surface",
    "model", "captured_at", "dump_type", "trigger", "memory_scope",
    "source_method", "contour_context_loaded", "last_contour_revision_read",
    "previous_dump_id",
]

ENUMS = {
    "schema_version": ["contour-dump-v1"],
    "surface": ["web", "desktop", "code", "cli"],
    "dump_type": ["baseline", "incremental", "verification"],
    # 没有 event / poll：MVP 不做逐轮 hook，也不做定时倾倒，
    # 所有倾倒都由用户确认后发起。见 references/drive.md。
    "trigger": ["user", "probe"],
    "memory_scope": ["global", "project", "workspace", "mixed", "unknown"],
    "source_method": [
        "native-view", "model-self-report", "export", "file-memory", "mixed",
    ],
    "contour_context_loaded": ["true", "false", "unknown"],
}

REQUIRED_SECTIONS = [
    "## 导出边界与已知限制",
    "## 可访问的持久记忆",
    "## 记忆中的过期项、矛盾与不确定项",
    "## 非原生记忆来源",
    "## 本端无法确认的内容",
]

FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)

MODEL_NAME = re.compile(
    r"(?:gpt|claude|gemini|llama|qwen)[-_]?\d"   # 族名后面跟版本号
    r"|(?<![a-z])(?:opus|sonnet|haiku)(?![a-z])"  # 这几个单独出现就是模型名
)


def parse_frontmatter(text):
    m = FRONTMATTER.match(text)
    if not m:
        return None, text
    fields = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields, text[m.end():]


def check(path):
    """返回该文件的问题列表，空列表表示通过。"""
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"读不出来：{exc}"]

    fields, body = parse_frontmatter(text)
    if fields is None:
        return ["缺 frontmatter（文件必须以 --- 开头）"]

    for name in REQUIRED_FIELDS:
        if name not in fields:
            problems.append(f"缺字段 {name}")

    for name, allowed in ENUMS.items():
        value = fields.get(name)
        if value is not None and value not in allowed:
            problems.append(f"{name} = {value!r}，只允许 {'/'.join(allowed)}")

    captured = fields.get("captured_at")
    if captured:
        try:
            parsed = datetime.fromisoformat(captured.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                problems.append("captured_at 缺时区")
        except ValueError:
            problems.append(f"captured_at 不是 ISO 8601：{captured!r}")

    dump_id = fields.get("dump_id", "")
    if not dump_id or dump_id in {"null", "<全局唯一>"}:
        problems.append("dump_id 必须是真实的全局唯一值")

    if fields.get("dump_type") == "incremental":
        prev = fields.get("previous_dump_id", "")
        if not prev or prev == "null":
            problems.append("incremental 包必须给 previous_dump_id")

    endpoint_id = fields.get("endpoint_id", "")
    if endpoint_id and endpoint_id != endpoint_id.lower():
        problems.append(f"endpoint_id 要全小写：{endpoint_id!r}")
    # 端标识描述产品表面，不含模型名——换模型不是换端。
    # 匹配「模型族 + 版本号」，不匹配裸的族名：chatgpt-web 里的 "gpt" 是产品名不是模型名。
    hit = MODEL_NAME.search(endpoint_id)
    if hit:
        problems.append(
            f"endpoint_id 里疑似含模型名（{hit.group(0)}），模型名属于每次倾倒的元数据——"
            "换模型不是换端"
        )

    for section in REQUIRED_SECTIONS:
        if section not in body:
            problems.append(f"缺章节 {section}")

    if "## 可访问的持久记忆" in body and "## 非原生记忆来源" not in body:
        problems.append("持久记忆与非原生来源必须分开，否则冲突消解无法工作")

    parent = path.parent.name
    if endpoint_id and parent != endpoint_id and parent != "inbox":
        problems.append(
            f"包放错目录：endpoint_id 是 {endpoint_id!r}，却在 {parent!r} 下。"
            "每个端只写自己的收件区"
        )

    return problems


def main(argv):
    # Windows 控制台默认不是 UTF-8，中文输出会变乱码。显式指定。
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass

    args = argv[1:]
    if not args:
        print(__doc__)
        return 2

    if args[0] == "--inbox":
        if len(args) != 2:
            print("用法：validate_dump.py --inbox <实例仓路径>", file=sys.stderr)
            return 2
        inbox = Path(args[1]) / "dumps" / "inbox"
        if not inbox.is_dir():
            print(f"找不到 {inbox}", file=sys.stderr)
            return 2
        targets = sorted(inbox.rglob("*.md"))
        if not targets:
            print(f"{inbox} 下没有倾倒包")
            return 0
    else:
        targets = [Path(a) for a in args]

    failed = 0
    for path in targets:
        problems = check(path)
        # 标记用纯 ASCII：Windows 控制台默认 GBK，打不出勾叉符号会直接崩。
        if problems:
            failed += 1
            print(f"[FAIL] {path}")
            for p in problems:
                print(f"       {p}")
        else:
            print(f"[ OK ] {path}")

    print(f"\n{len(targets)} 个包，{failed} 个不合规")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
