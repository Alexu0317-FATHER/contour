#!/usr/bin/env python3
"""校验倾倒包的 frontmatter 与正文结构是否合规。

新包使用 contour-dump-v2（按记忆存储 store_id 记）；v1 旧包（按 endpoint_id 记）
不可改写，仍按 v1 字段校验。

这是 references/protocol.md「包的确定性校验」的一种本地实现；
能给出同样结论的其他工具同样可用。

用法：
    python validate_dump.py <倾倒包路径> [更多路径...]
        # 内容与批次检查；路径位于 dumps/inbox/ 下时加查入库位置
    python validate_dump.py --inbox <档案根目录>     # 校验受管收件区全部包
    python validate_dump.py --cold-start-ready <档案根目录> [--store-map <endpoint-id>=<store-id> ...]
        # 先报告格式检查，再判断首发门槛：是否至少两个不同记忆存储各有一份合规 baseline。
        # 不合规或撞号的包列出并排除，不计入门槛，也不单独阻断。
        # v1 旧包按端记录，用 --store-map 按 config.md 给出对应的存储；
        # 没有给出时列为“存储身份待确认”，不计入门槛。

这里做的全是确定性检查——字段在不在、值合不合法、章节缺不缺。
语义判断、来源真实性、存储是否登记都不归它管。

退出码：0 通过（--cold-start-ready 时表示已有至少两个不同存储的合规 baseline）；
        1 有不合规（--cold-start-ready 时表示门槛未满足或存储身份待确认）；
        2 用法错误。
"""

import re
import sys
from datetime import datetime
from pathlib import Path

COMMON_FIELDS = [
    "schema_version", "dump_id", "provider", "model", "captured_at",
    "dump_type", "trigger", "memory_scope", "source_method",
    "contour_context_loaded", "last_contour_revision_read", "previous_dump_id",
]

# v2 按记忆存储记包；v1 旧包按端记。包不可改写，所以 v1 仍按原字段校验。
SCHEMA_FIELDS = {
    "contour-dump-v2": ["store_id", "collected_via"],
    "contour-dump-v1": ["endpoint_id", "surface"],
}

# 包属于哪个记忆存储。v1 的 endpoint_id 要由执行者按 config.md 对应到存储。
IDENTITY_FIELD = {"contour-dump-v2": "store_id", "contour-dump-v1": "endpoint_id"}

# 必填字段都要有值。允许未知的字段写明确的 unknown，没有对应版本或上一个包时写 null；
# 空白不等于“未知”，也不能用来绕过日期和标识检查。
UNKNOWN_ALLOWED = {"provider", "model", "collected_via", "memory_scope", "contour_context_loaded"}
NULL_ALLOWED = {"last_contour_revision_read", "previous_dump_id"}
EMPTY_VALUES = {"", '""', "''"}

ENUMS = {
    "schema_version": list(SCHEMA_FIELDS),
    "surface": ["web", "desktop", "code", "cli"],   # 只有 v1 有这个字段
    "dump_type": ["baseline", "incremental", "verification"],
    # trigger 记录本次倾倒由什么发起（user = 用户本轮请求，probe = 探测检查），
    # 不表示授权依据。目前只定义这两个值；自动发起的倾倒要以新的
    # schema 版本增加取值，不伪装成 user 或 probe。见 references/protocol.md。
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

# 存储标识会被拼进路径，字符集必须封死；collected_via 沿用同一字符集。
IDENTIFIER = re.compile(r"\A[a-z0-9]+(?:-[a-z0-9]+)*\Z")
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


def check_content(path):
    """内容与来源字段检查，包放在哪里都适用。返回 (问题列表, frontmatter 字段)。

    撞号只能在批次层面发现，入库位置只对受管收件区有意义，都不在这里查。
    """
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        # 不猜编码，也不当成空内容：这份输入无效，其他文件照常检查。
        return [f"不是有效的 UTF-8，无法读取（第 {exc.start} 字节附近）"], None
    except OSError as exc:
        return [f"读不出来：{exc}"], None

    fields, body = parse_frontmatter(text)
    if fields is None:
        return ["缺 frontmatter（文件必须以 --- 开头）"], None

    schema = fields.get("schema_version")
    incremental = fields.get("dump_type") == "incremental"
    for name in COMMON_FIELDS + SCHEMA_FIELDS.get(schema, SCHEMA_FIELDS["contour-dump-v2"]):
        if name not in fields:
            problems.append(f"缺字段 {name}")
        elif fields[name] in EMPTY_VALUES:
            if name == "previous_dump_id" and incremental:
                continue   # 下面的 incremental 检查会给出更准确的提示
            if name in NULL_ALLOWED:
                hint = "没有时写 null"
            elif name in UNKNOWN_ALLOWED:
                hint = "未知时写 unknown"
            else:
                hint = "不能留空"
            problems.append(f"字段 {name} 没有值：{hint}")

    for name, allowed in ENUMS.items():
        value = fields.get(name)
        if value is not None and value not in EMPTY_VALUES and value not in allowed:
            problems.append(f"{name} = {value!r}，只允许 {'/'.join(allowed)}")

    captured = fields.get("captured_at", "")
    if captured not in EMPTY_VALUES:
        try:
            parsed = datetime.fromisoformat(captured.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                problems.append("captured_at 缺时区")
        except ValueError:
            problems.append(f"captured_at 不是 ISO 8601：{captured!r}")

    dump_id = fields.get("dump_id", "")
    if dump_id not in EMPTY_VALUES and not UUID4.match(dump_id):
        problems.append(f"dump_id 必须是 UUID4：{dump_id!r}")

    if incremental:
        prev = fields.get("previous_dump_id", "")
        if prev in EMPTY_VALUES or prev == "null":
            problems.append("incremental 包必须给 previous_dump_id")

    names = [IDENTITY_FIELD.get(schema, "store_id")]
    if schema != "contour-dump-v1":
        names.append("collected_via")
    for name in names:
        value = fields.get(name, "")
        if value not in EMPTY_VALUES and not IDENTIFIER.match(value):
            problems.append(
                f"{name} 不合规：{value!r}。只允许小写字母、数字和单个连字符分隔"
                "——存储标识会被拼进路径"
            )
        # 标识描述存储或产品表面，不含模型名——换模型不是换存储或换端。
        # 匹配「模型族 + 版本号」，不匹配裸的族名：chatgpt-web 里的 "gpt" 是产品名不是模型名。
        hit = MODEL_NAME.search(value)
        if hit:
            problems.append(
                f"{name} 里疑似含模型名（{hit.group(0)}），模型名属于每次倾倒的元数据——"
                "换模型不是换存储或换端"
            )

    for section in REQUIRED_SECTIONS:
        if section not in body:
            problems.append(f"缺章节 {section}")

    if "## 可访问的持久记忆" in body and "## 非原生记忆来源" not in body:
        problems.append("持久记忆与非原生来源必须分开，否则冲突消解无法工作")

    return problems, fields


def identity(fields):
    """包所属的记忆存储标识；v1 旧包返回 endpoint_id。"""
    fields = fields or {}
    return fields.get(IDENTITY_FIELD.get(fields.get("schema_version"), "store_id"), "")


def in_managed_inbox(path):
    """路径位于某个 dumps/inbox/ 之下时为 True。

    临时下载或工具返回、尚未入库的包不受入库位置约束——运输落点不是来源身份。
    """
    return any(
        ancestor.name == "inbox" and ancestor.parent.name == "dumps"
        for ancestor in path.resolve().parents
    )


def check_location(path, store_id):
    """受管收件区内的包必须直接放在 dumps/inbox/<store_id>/ 下。"""
    parent = path.resolve().parent
    inbox = parent.parent
    if parent.name == store_id and inbox.name == "inbox" and inbox.parent.name == "dumps":
        return []
    # inbox 根部的裸文件也是放错了——它不属于任何存储的收件区，
    # 谁该为它负责、该不该参与合并都无从判断。
    where = "inbox 根部" if parent.name == "inbox" else f"{parent.name!r} 下"
    return [
        f"包放错位置：存储标识是 {store_id!r}，却在{where}。"
        "受管收件区的包必须直接放在 dumps/inbox/<store-id>/ 里"
    ]


def parse_store_map(pairs):
    """把 --store-map <endpoint-id>=<store-id> 解析成字典；格式不对返回 None。"""
    mapping = {}
    for pair in pairs:
        endpoint_id, sep, store_id = pair.partition("=")
        if not sep or not IDENTIFIER.match(endpoint_id) or not IDENTIFIER.match(store_id):
            return None
        mapping[endpoint_id] = store_id
    return mapping


def counted_store(fields, store_map):
    """门槛计数用的记忆存储；v1 旧包没有对应关系时返回 None（存储身份待确认）。"""
    if fields.get("schema_version") == "contour-dump-v1":
        # v1 按端记包，端标识不是存储标识；不换算就无法和 v2 包一起去重。
        return store_map.get(fields.get("endpoint_id", ""))
    return fields.get("store_id", "")


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

    mode = args[0] if args[0] in {"--inbox", "--cold-start-ready"} else None
    cold_start_ready = mode == "--cold-start-ready"
    store_map = {}
    if mode:
        rest = args[2:]
        pairs = rest[1::2]
        valid = (
            len(args) >= 2
            and (cold_start_ready or not rest)
            and len(rest) % 2 == 0
            and all(flag == "--store-map" for flag in rest[0::2])
        )
        store_map = parse_store_map(pairs) if valid else None
        if store_map is None:
            print(
                "用法：validate_dump.py --inbox <档案根目录>\n"
                "      validate_dump.py --cold-start-ready <档案根目录> "
                "[--store-map <endpoint-id>=<store-id> ...]",
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
                print("[BLOCK] 首发门槛未满足：至少需要两个不同记忆存储的合规 baseline")
                return 1
            return 0
    else:
        # 同一路径传两次不算撞号。
        targets = list(dict.fromkeys(Path(a) for a in args))

    results = []       # (路径, 问题列表, 字段, 是否在受管收件区)
    by_id = {}         # dump_id -> 用它的全部文件
    for path in targets:
        problems, fields = check_content(path)
        located = in_managed_inbox(path)
        store_id = identity(fields)
        if located and store_id:
            problems += check_location(path, store_id)
        results.append((path, problems, fields, located))
        dump_id = (fields or {}).get("dump_id", "")
        if dump_id:
            by_id.setdefault(dump_id, []).append(path)

    # dump_id 是包的唯一身份，消费 manifest 靠它记账。撞号时无法判断哪个才是
    # 那个身份，所以撞号的每个包都不能消费——不只是后出现的那个。
    collided = {d: paths for d, paths in by_id.items() if len(paths) > 1}
    for path, problems, fields, _ in results:
        dump_id = (fields or {}).get("dump_id", "")
        if dump_id in collided:
            others = ", ".join(p.name for p in collided[dump_id] if p != path)
            problems.append(f"dump_id 与 {others} 重复")

    print("== 格式检查 ==")
    failed = 0
    baseline_stores = set()
    pending = set()    # 没有对应关系的 v1 端标识
    for path, problems, fields, located in results:
        # 标记用纯 ASCII：Windows 控制台默认 GBK，打不出勾叉符号会直接崩。
        if problems:
            failed += 1
            print(f"[FAIL] {path}")
            for p in problems:
                print(f"       {p}")
            continue
        note = "" if located else "  （不在受管收件区，未检查入库位置）"
        print(f"[ OK ] {path}{note}")
        if fields.get("dump_type") == "baseline":
            store = counted_store(fields, store_map)
            if store is None:
                pending.add(fields.get("endpoint_id", ""))
            elif store:
                baseline_stores.add(store)

    print(f"\n{len(results)} 个包，{failed} 个不合规")
    if collided:
        count = sum(len(paths) for paths in collided.values())
        print(f"其中 {count} 个包的 dump_id 撞号——消费 manifest 会记错账，这些包都不能消费")
    if not cold_start_ready:
        return 1 if failed else 0

    # 格式合规只说明包本身没问题；下面单独判断首发门槛。
    print("\n== 首发门槛 ==")
    stores = ", ".join(sorted(baseline_stores)) or "无"
    print(f"合规 baseline 来自 {len(baseline_stores)} 个不同记忆存储：{stores}")
    if failed:
        # 坏包只排除它自己，不连坐其他存储的有效 baseline。
        print(
            f"[WARN] {failed} 个不合规包已排除：不计入门槛、不进入本轮整合；"
            "原因记入 review/，交用户处理"
        )
    if pending:
        print(
            "[PENDING] 以下 v1 旧包的存储身份待确认，未计入门槛："
            f"{', '.join(sorted(pending))}。请按 config.md 用 --store-map 给出对应关系"
        )
    if len(baseline_stores) >= 2:
        print("[READY] 已有至少两个不同记忆存储的合规 baseline；存储是否已登记仍需对照 config.md")
        return 0
    if pending:
        print("[PENDING] 存储身份待确认，暂不能判断是否满足两个不同记忆存储的条件")
    else:
        print("[BLOCK] 首发门槛未满足：至少需要两个不同记忆存储的合规 baseline")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
