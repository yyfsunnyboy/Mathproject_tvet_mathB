"""Final-answer disclosure guard shared by every AI Tutor reply surface.

Before a reply is shown, the math it states is compared with the server-side
answer by symbolic equivalence, so a rearranged form (``3y=2x-15`` for
``y=2x/3-5``) is caught while a general formula (``y=mx+b``) or a partial
substitution (``\\sqrt{1^2+7^2}``) is not.

Capability boundary: answer parts that are not parseable math (proof text,
constructions, free drawings, worded conclusions) are only matched literally,
and list rubrics (tree paths, Pascal rows) only as complete sequences.  A
paraphrased proof or a described drawing cannot be detected here; those rely
on the prompt-level teaching-round policy.
"""

from __future__ import annotations

import re
import string
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Iterable

REDACTION_TEXT = "（這一步留給你自己完成）"

_MAX_MATH_LEN = 120
_FULLWIDTH = {code: code - 0xFEE0 for code in range(0xFF01, 0xFF5F)}
_FULLWIDTH.update({0x3000: 0x20, 0x2212: 0x2D, 0x2013: 0x2D, 0x2014: 0x2D})

_SYMBOL_RULES = (
    (re.compile(r"\\(?:left|right|displaystyle|bigl|bigr|Bigl|Bigr|big|Big)(?![a-z])"), ""),
    (re.compile(r"\\(?:quad|qquad|[,;:! ])"), " "),
    (re.compile(r"\\[dt]frac"), r"\\frac"),
    (re.compile(r"\\(?:times|cdot|ast)(?![a-z])|[×·∙]"), "*"),
    (re.compile(r"\\div(?![a-z])|÷"), "/"),
    (re.compile(r"\\pi(?![a-z])|π"), "pi"),
    (re.compile(r"\\(?:leqslant|leq|le)(?![a-z])|[≤≦]"), "<="),
    (re.compile(r"\\(?:geqslant|geq|ge)(?![a-z])|[≥≧]"), ">="),
    (re.compile(r"\\(?:neq|ne)(?![a-z])|≠"), "!="),
    (re.compile(r"\\lt(?![a-z])"), "<"),
    (re.compile(r"\\gt(?![a-z])"), ">"),
    (re.compile(r"²"), "^2"),
    (re.compile(r"³"), "^3"),
)
_RELATION_SPLIT = re.compile(r"(<=|>=|!=|=|<|>)")
_FLIPPED = {"<": ">", ">": "<", "<=": ">=", ">=": "<=", "=": "=", "!=": "!="}
_ALLOWED_MATH = re.compile(r"^[0-9A-Za-z+\-*/^().,\s]+$")
_FUNCTION_NAMES = {"sqrt", "root", "pi"}

_DELIMITED = re.compile(r"\$\$(.+?)\$\$|\$(.+?)\$|\\\((.+?)\\\)|\\\[(.+?)\\\]", re.S)
_PLAIN_RUN = re.compile(r"[0-9A-Za-z\\{}()\[\]+\-*/^=<>≤≥≦≧≠√π×÷·.,'＝＋－（） \t]+")
_RAW_RELATION = re.compile(r"\\(?:leqslant|geqslant|leq|geq|neq|le|ge|ne|lt|gt)(?![a-z])|<=|>=|!=|[=<>≤≥≦≧≠＝]")
_TUPLE = re.compile(r"\(\s*([^(),]+?)\s*,\s*([^(),]+?)\s*\)")

_PRE_MARKERS = (
    "答案", "結果", "等於", "得到", "算出", "所以", "因此", "就是", "即為", "即", "得", "為", "是",
)
_POST_MARKERS = ("就是答案", "是答案", "為所求", "即為所求", "是最後答案", "就是最後答案")
_CHOICE_ANSWER = re.compile(r"^[(（]?\s*([A-Ea-e])\s*[)）]?$")


@dataclass
class DisclosureFinding:
    disclosed: bool = False
    method: str = "none"
    spans: list[tuple[int, int, str]] = field(default_factory=list)


@dataclass
class _Claim:
    kind: str  # relation | value
    start: int  # replacement start in the reply
    end: int  # replacement end in the reply
    replacement: str
    lhs: Any = None
    op: str = ""
    rhs: Any = None
    lhs_ops: int = 0
    rhs_ops: int = 0
    value: Any = None
    value_ops: int = 0
    marked: bool = False


def _latex_to_plain(text: str) -> str:
    t = str(text or "").translate(_FULLWIDTH).replace("$", "")
    t = re.sub(r"\\[()\[\]]", " ", t)
    for pattern, repl in _SYMBOL_RULES:
        t = pattern.sub(repl, t)
    previous = None
    while previous != t:
        previous = t
        t = re.sub(r"\\frac\s*\{([^{}]*)\}\s*\{([^{}]*)\}", r"((\1)/(\2))", t)
        t = re.sub(r"\\sqrt\s*\[([^\]]*)\]\s*\{([^{}]*)\}", r"root((\2),(\1))", t)
        t = re.sub(r"\\sqrt\s*\{([^{}]*)\}", r"sqrt(\1)", t)
        t = re.sub(r"\^\s*\{([^{}]*)\}", r"^(\1)", t)
    t = re.sub(r"\\frac\s*(\w)\s*(\w)", r"(\1/\2)", t)
    t = re.sub(r"\\sqrt\s*(\d+(?:\.\d+)?|[A-Za-z])", r"sqrt(\1)", t)
    t = re.sub(r"√\s*\(", "sqrt(", t)
    t = re.sub(r"√\s*(\d+(?:\.\d+)?|[A-Za-z])", r"sqrt(\1)", t)
    t = t.replace("{", "(").replace("}", ")").replace("[", "(").replace("]", ")")
    return re.sub(r"\s+", " ", t).strip()


@lru_cache(maxsize=1024)
def _parse(plain: str, evaluate: bool = True):
    text = str(plain or "").strip()
    if not text or len(text) > _MAX_MATH_LEN or not _ALLOWED_MATH.match(text):
        return None
    if "__" in text or "**" in text:
        return None
    if any(len(word) > 3 and word not in _FUNCTION_NAMES for word in re.findall(r"[A-Za-z]+", text)):
        return None
    if text.count("(") != text.count(")"):
        return None
    try:
        from sympy import Symbol, pi, root, sqrt
        from sympy.parsing.sympy_parser import (
            convert_xor,
            implicit_multiplication_application,
            parse_expr,
            standard_transformations,
        )

        local = {letter: Symbol(letter) for letter in string.ascii_letters}
        local.update({"sqrt": sqrt, "root": root, "pi": pi})
        return parse_expr(
            text,
            local_dict=local,
            transformations=standard_transformations + (convert_xor, implicit_multiplication_application),
            evaluate=evaluate,
        )
    except Exception:
        return None


def _ops(plain: str) -> int:
    expr = _parse(plain, False)
    if expr is None:
        expr = _parse(plain, True)
    try:
        from sympy import count_ops

        return int(count_ops(expr)) if expr is not None else 99
    except Exception:
        return 99


def _same_value(left, right) -> bool:
    try:
        from sympy import N, simplify

        diff = left - right
        if not diff.free_symbols and not right.free_symbols:
            return abs(complex(N(diff))) < 1e-9 * (1 + abs(complex(N(right))))
        return simplify(diff) == 0
    except Exception:
        return False


def _relations_equivalent(claim_lhs, claim_op, claim_rhs, ans_lhs, ans_op, ans_rhs) -> bool:
    try:
        from sympy import simplify

        claim_diff = claim_lhs - claim_rhs
        answer_diff = ans_lhs - ans_rhs
        if claim_diff == 0 or answer_diff == 0:
            return False
        ratio = simplify(claim_diff / answer_diff)
        if ratio.free_symbols or not ratio.is_number or ratio == 0:
            return False
        if ans_op in ("=", "!="):
            return claim_op == ans_op
        return claim_op == (ans_op if bool(ratio > 0) else _FLIPPED[ans_op])
    except Exception:
        return False


def _split_top_level(text: str, separators: tuple[str, ...]) -> list[tuple[int, str]]:
    """Split at depth-0 separators; returns (offset, piece) pairs."""
    pieces: list[tuple[int, str]] = []
    depth = 0
    start = 0
    i = 0
    while i < len(text):
        ch = text[i]
        if ch in "({[（":
            depth += 1
        elif ch in ")}]）":
            depth = max(0, depth - 1)
        elif depth == 0:
            sep = next((s for s in separators if text.startswith(s, i)), None)
            if sep:
                pieces.append((start, text[start:i]))
                start = i + len(sep)
                i = start
                continue
        i += 1
    pieces.append((start, text[start:]))
    return pieces


_ANSWER_SEPARATORS = (";", "；", ",", "，", "、", "或", "且", "及", " or ", " and ")


def _strip_units(text: str) -> str:
    return re.sub(r"\s*[\u4e00-\u9fff]+\s*$", "", str(text or "")).strip()


@dataclass
class _AnswerPart:
    kind: str  # solution | relation | value | tuple | choice | text
    raw: str
    symbol: Any = None
    op: str = ""
    lhs: Any = None
    rhs: Any = None
    value: Any = None
    value_ops: int = 0
    items: tuple = ()


def _relation_parts(plain: str, raw: str) -> list[_AnswerPart] | None:
    pieces = _RELATION_SPLIT.split(plain)
    if len(pieces) < 3:
        return None
    segments, ops = pieces[0::2], pieces[1::2]
    parts: list[_AnswerPart] = []
    for index, op in enumerate(ops):
        left_text, right_text = segments[index].strip(), segments[index + 1].strip()
        left, right = _parse(left_text), _parse(right_text)
        if left is None or right is None:
            return None
        if getattr(left, "is_Symbol", False) and not right.free_symbols:
            parts.append(_AnswerPart("solution", raw, symbol=left, op=op, value=right,
                                     value_ops=_ops(right_text)))
        elif getattr(right, "is_Symbol", False) and not left.free_symbols:
            parts.append(_AnswerPart("solution", raw, symbol=right, op=_FLIPPED[op], value=left,
                                     value_ops=_ops(left_text)))
        else:
            parts.append(_AnswerPart("relation", raw, op=op, lhs=left, rhs=right))
    return parts


def _answer_parts(correct_answer: Any) -> list[_AnswerPart]:
    if isinstance(correct_answer, (list, tuple)):
        texts = [str(item) for item in correct_answer if str(item).strip()]
    else:
        texts = [str(correct_answer or "").strip()]
    parts: list[_AnswerPart] = []
    for text in texts:
        if not text:
            continue
        choice = _CHOICE_ANSWER.match(text)
        if choice:
            parts.append(_AnswerPart("choice", text, value=choice.group(1).upper()))
            continue
        plain_whole = _latex_to_plain(text)
        tuple_match = re.fullmatch(r"\s*\(\s*([^(),]+?)\s*,\s*([^(),]+?)\s*\)\s*", plain_whole)
        if tuple_match:
            items = tuple(_parse(v) for v in tuple_match.groups())
            if all(item is not None for item in items):
                parts.append(_AnswerPart("tuple", text, items=items))
                continue
        for _offset, piece in _split_top_level(text, _ANSWER_SEPARATORS):
            piece = piece.strip()
            if not piece:
                continue
            plain = _latex_to_plain(_strip_units(piece))
            relations = _relation_parts(plain, piece)
            if relations:
                parts.extend(relations)
                continue
            value = _parse(plain)
            if value is not None and plain:
                parts.append(_AnswerPart("value", piece, value=value, value_ops=_ops(plain)))
            else:
                parts.append(_AnswerPart("text", piece))
    return parts


def _has_marker(text: str, start: int, end: int) -> bool:
    before = re.sub(r"[\s:：$]", "", text[max(0, start - 10):start])
    after = re.sub(r"[\s$]", "", text[end:end + 10])
    return any(before.endswith(m) for m in _PRE_MARKERS) or any(after.startswith(m) for m in _POST_MARKERS)


def _snippets(text: str) -> list[tuple[int, int, int, int]]:
    """(outer_start, outer_end, inner_start, inner_end) for every math-looking run."""
    found: list[tuple[int, int, int, int]] = []
    masked = list(text)
    for match in _DELIMITED.finditer(text):
        group = next(i for i in range(1, 5) if match.group(i) is not None)
        found.append((match.start(), match.end(), match.start(group), match.end(group)))
        for i in range(match.start(), match.end()):
            masked[i] = "\x00"
    masked_text = "".join(masked)
    for match in _PLAIN_RUN.finditer(masked_text):
        run = match.group(0)
        lead = len(run) - len(run.lstrip(" .,'"))
        trail = len(run) - len(run.rstrip(" .,'"))
        start, end = match.start() + lead, match.end() - trail
        if end <= start:
            continue
        body = text[start:end]
        if not re.search(r"\d", body) and not _RAW_RELATION.search(body):
            continue
        found.append((start, end, start, end))
    return sorted(found)


def _claims(text: str, require_marker: bool = True) -> tuple[list[_Claim], list[tuple]]:
    claims: list[_Claim] = []
    tuples: list[tuple] = []
    for outer_start, outer_end, inner_start, inner_end in _snippets(text):
        inner = text[inner_start:inner_end]
        for tuple_match in _TUPLE.finditer(_latex_to_plain(inner)):
            items = tuple(_parse(v) for v in tuple_match.groups())
            if all(item is not None for item in items):
                tuples.append((outer_start, outer_end, items))
        delimited = outer_start != inner_start
        for offset, piece in _split_top_level(inner, (";", "；", ",", "，", "、")):
            if not piece.strip():
                continue
            piece_start = inner_start + offset
            boundaries = [m for m in _RAW_RELATION.finditer(piece)]
            seg_bounds = []
            cursor = 0
            for m in boundaries:
                seg_bounds.append((cursor, m.start()))
                cursor = m.end()
            seg_bounds.append((cursor, len(piece)))
            plains = [_latex_to_plain(piece[a:b]) for a, b in seg_bounds]
            ops = [_latex_to_plain(m.group(0)) or "=" for m in boundaries]
            whole_start = outer_start if delimited and len(_split_top_level(inner, (";", "；", ",", "，", "、"))) == 1 else piece_start
            whole_end = outer_end if whole_start == outer_start else piece_start + len(piece)
            if not boundaries:
                value = _parse(plains[0])
                if value is None:
                    continue
                marked = _has_marker(text, outer_start if delimited else piece_start,
                                     outer_end if delimited else piece_start + len(piece))
                if marked or not require_marker:
                    claims.append(_Claim("value", whole_start, whole_end, REDACTION_TEXT,
                                         value=value, value_ops=_ops(plains[0]), marked=True))
                continue
            parsed = [_parse(p) for p in plains]
            for index, op in enumerate(ops):
                left, right = parsed[index], parsed[index + 1]
                if left is None or right is None:
                    continue
                claims.append(_Claim(
                    "relation", whole_start, whole_end, REDACTION_TEXT,
                    lhs=left, op=op, rhs=right,
                    lhs_ops=_ops(plains[index]), rhs_ops=_ops(plains[index + 1]),
                ))
                if op == "=":
                    cut = piece_start + seg_bounds[index + 1][0]
                    end = piece_start + len(piece)
                    claims.append(_Claim(
                        "value", cut, end, " ?", value=right, value_ops=_ops(plains[index + 1]),
                    ))
    return claims, tuples


def _simple_enough(claim_ops: int, answer_ops: int) -> bool:
    return claim_ops <= max(answer_ops, 1)


def _match_part(part: _AnswerPart, text: str, claims: list[_Claim], tuples: list[tuple],
                require_marker: bool) -> list[tuple[int, int, str]]:
    hits: list[tuple[int, int, str]] = []
    if part.kind == "choice":
        letter = re.escape(part.value)
        pattern = rf"(?:答案|選項|應選|選擇|選|正確的是|是)\s*[:：]?\s*[（(]?\s*{letter}\s*[)）]?(?![A-Za-z])"
        if not require_marker:
            pattern = rf"(?<![A-Za-z]){letter}(?![A-Za-z])"
        return [(m.start(), m.end(), REDACTION_TEXT) for m in re.finditer(pattern, text)]
    if part.kind == "text":
        needle = re.sub(r"\s+", "", part.raw)
        if len(needle) < 2:
            return []
        for m in re.finditer(re.escape(part.raw.strip()), text):
            if not require_marker or _has_marker(text, m.start(), m.end()):
                hits.append((m.start(), m.end(), REDACTION_TEXT))
        return hits
    if part.kind == "tuple":
        for start, end, items in tuples:
            if len(items) == len(part.items) and all(_same_value(a, b) for a, b in zip(items, part.items)):
                hits.append((start, end, REDACTION_TEXT))
        return hits
    for claim in claims:
        if part.kind == "relation" and claim.kind == "relation":
            if _relations_equivalent(claim.lhs, claim.op, claim.rhs, part.lhs, part.op, part.rhs):
                hits.append((claim.start, claim.end, claim.replacement))
        elif part.kind == "solution" and claim.kind == "relation":
            for side, other, op, other_ops in (
                (claim.lhs, claim.rhs, claim.op, claim.rhs_ops),
                (claim.rhs, claim.lhs, _FLIPPED[claim.op], claim.lhs_ops),
            ):
                if side == part.symbol and not other.free_symbols and op == part.op \
                        and _same_value(other, part.value) and _simple_enough(other_ops, part.value_ops):
                    hits.append((claim.start, claim.end, claim.replacement))
                    break
        elif part.kind in ("value", "solution") and claim.kind == "value":
            if part.kind == "solution" and not claim.marked:
                continue
            if _same_value(claim.value, part.value) and _simple_enough(claim.value_ops, part.value_ops):
                hits.append((claim.start, claim.end, claim.replacement))
    return hits


def _sequence_hits(text: str, items: Iterable[Any]) -> list[tuple[int, int, str]]:
    values = [str(item).strip() for item in items if str(item).strip()]
    if len(values) < 2:
        return []
    if all(re.fullmatch(r"-?\d+(?:\.\d+)?", v) for v in values):
        pattern = r"(?<![\d.])" + r"[^\d\n]{1,4}".join(re.escape(v) for v in values) + r"(?![\d.])"
        return [(m.start(), m.end(), REDACTION_TEXT) for m in re.finditer(pattern, text)]
    hits = []
    for value in values:
        idx = text.find(value)
        if idx < 0:
            return []
        hits.append((idx, idx + len(value), REDACTION_TEXT))
    return hits


def _detect(text: str, correct_answer: Any, answer_items: Iterable[Any] | None,
            require_marker: bool) -> DisclosureFinding:
    text = str(text or "")
    if not text.strip():
        return DisclosureFinding()
    if answer_items:
        hits = _sequence_hits(text, answer_items)
        if hits:
            return DisclosureFinding(True, "sequence", hits)
    parts = _answer_parts(correct_answer)
    if not parts:
        return DisclosureFinding()
    claims, tuples = _claims(text, require_marker=require_marker)
    spans: list[tuple[int, int, str]] = []
    methods = set()
    for part in parts:
        hits = _match_part(part, text, claims, tuples, require_marker)
        if not hits:
            return DisclosureFinding()
        spans.extend(hits)
        methods.add("literal" if part.kind in ("text", "choice") else "symbolic")
    return DisclosureFinding(True, "+".join(sorted(methods)), spans)


def find_answer_disclosure(reply: str, correct_answer: Any, *, student_work: str = "",
                           answer_items: Iterable[Any] | None = None) -> DisclosureFinding:
    """Does ``reply`` state every part of the final answer the student has not written yet?"""
    items = list(answer_items or [])
    finding = _detect(reply, correct_answer, items, require_marker=True)
    if finding.disclosed and str(student_work or "").strip():
        if _detect(student_work, correct_answer, items, require_marker=False).disclosed:
            return DisclosureFinding()
    return finding


def redact_answer_disclosure(reply: str, finding: DisclosureFinding) -> str:
    """Replace only the disclosing math so the rest of the guidance survives."""
    text = str(reply or "")
    if not finding.disclosed:
        return text
    applied: list[tuple[int, int]] = []
    for start, end, replacement in sorted(finding.spans, key=lambda s: (s[0], -s[1])):
        if any(start < b and end > a for a, b in applied):
            continue
        applied.append((start, end))
    for start, end in sorted(applied, reverse=True):
        replacement = next(r for s, e, r in finding.spans if s == start and e == end)
        text = text[:start] + replacement + text[end:]
    return text


__all__ = [
    "REDACTION_TEXT",
    "DisclosureFinding",
    "find_answer_disclosure",
    "redact_answer_disclosure",
]
