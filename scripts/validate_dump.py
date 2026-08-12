#!/usr/bin/env python3
"""校验倾倒包的 frontmatter 与正文结构是否合规。

用法：
    python validate_dump.py <倾倒包路径> [更多路径...]
    python validate_dump.py --inbox <实例仓路径>     # 校验整个 inbox
    python validate_dump.py --cold-start-ready <实例仓路径>
        # 校验 inbox，并要求至少两个不同端各有一份合法 baseline

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

# endpoint-id 会被拼进路径，字符集必须封死。
ENDPOINT_ID = re.compile(r"\A[a-z0-9]+(?:-[a-z0-9]+)*\Z")
UUID4 = re.compile(
    r"\A[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\Z",
    re.I,
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
    """返回 (问题列表, dump_id)。问题列表为空表示单文件层面通过。

    dump_id 单独返回，是因为撞号只能在批次层面发现——单看一个文件永远合规。
    """
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"读不出来：{exc}"], None

    fields, body = parse_frontmatter(text)
    if fields is None:
        return ["缺 frontmatter（文件必须以 --- 开头）"], None

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
    if not UUID4.match(dump_id):
        problems.append(f"dump_id 必须是 UUID4：{dump_id!r}")

    if fields.get("dump_type") == "incremental":
        prev = fields.get("previous_dump_id", "")
        if not prev or prev == "null":
            problems.append("incremental 包必须给 previous_dump_id")

    endpoint_id = fields.get("endpoint_id", "")
    if endpoint_id and not ENDPOINT_ID.match(endpoint_id):
        problems.append(
            f"endpoint_id 不合规：{endpoint_id!r}。只允许小写字母、数字和单个连字符分隔"
            "——它会被拼进路径"
        )
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

    # 位置检查没有例外：inbox 根部的裸文件也是放错了——它不属于任何端的收件区，
    # 谁该为它负责、该不该参与合并都无从判断。
    parent = path.parent.name
    if endpoint_id and parent != endpoint_id:
        where = "inbox 根部" if parent == "inbox" else f"{parent!r} 下"
        problems.append(
            f"包放错位置：endpoint_id 是 {endpoint_id!r}，却在{where}。"
            "每个包必须在 dumps/inbox/<endpoint-id>/ 里"
        )

    return problems, dump_id


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

    cold_start_ready = args[0] == "--cold-start-ready"
    if args[0] in {"--inbox", "--cold-start-ready"}:
        if len(args) != 2:
            print(
                "用法：validate_dump.py --inbox|--cold-start-ready <实例仓路径>",
                file=sys.stderr,
            )
            return 2
        inbox = Path(args[1]) / "dumps" / "inbox"
        if not inbox.is_dir():
            print(f"找不到 {inbox}", file=sys.stderr)
            return 2
        targets = sorted(inbox.rglob("*.md"))
        if not targets:
            print(f"{inbox} 下没有倾倒包")
            if cold_start_ready:
                print("[BLOCK] 第一版发布至少需要两个不同端的合法 baseline")
                return 1
            return 0
    else:
        targets = [Path(a) for a in args]

    failed = 0
    seen = {}          # dump_id -> 第一个用它的文件
    collisions = 0
    baseline_endpoints = set()
    for path in targets:
        problems, dump_id = check(path)
        # dump_id 是包的唯一身份，消费 manifest 靠它记账。撞号会造成重复消费或漏包，
        # 而单看一个文件永远发现不了——必须在批次层面查。
        if dump_id:
            if dump_id in seen:
                collisions += 1
                problems = problems + [f"dump_id 与 {seen[dump_id].name} 重复"]
            else:
                seen[dump_id] = path
        # 标记用纯 ASCII：Windows 控制台默认 GBK，打不出勾叉符号会直接崩。
        if problems:
            failed += 1
            print(f"[FAIL] {path}")
            for p in problems:
                print(f"       {p}")
        else:
            print(f"[ OK ] {path}")
            if cold_start_ready:
                fields, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
                if fields and fields.get("dump_type") == "baseline":
                    baseline_endpoints.add(fields.get("endpoint_id", ""))

    print(f"\n{len(targets)} 个包，{failed} 个不合规")
    if collisions:
        print(f"其中 {collisions} 个 dump_id 撞号——消费 manifest 会记错账")
    if cold_start_ready:
        baseline_endpoints.discard("")
        endpoints = ", ".join(sorted(baseline_endpoints)) or "无"
        print(f"合法 baseline 来自 {len(baseline_endpoints)} 个不同端：{endpoints}")
        if len(baseline_endpoints) < 2:
            print("[BLOCK] 第一版发布至少需要两个不同端的合法 baseline")
            return 1
        if failed:
            print("[BLOCK] inbox 仍有不合规包，修复后才能发布第一版")
            return 1
        print("[READY] 已通过第一版发布的两端 baseline 门槛；仍需对照 config.md 确认端已登记")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
