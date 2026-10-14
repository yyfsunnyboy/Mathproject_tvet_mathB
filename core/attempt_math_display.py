"""Display-only copies of stored question / answer text for math rendering.

Nothing here is written back: the database keeps the original values and the
returned text is escaped by Jinja and typeset by MathJax in the browser.
"""

from __future__ import annotations

import json
import re

UNANSWERED_LABEL = "未作答"
STATUS_CLEAN = "clean"
STATUS_REPAIRED = "repaired"
STATUS_UNCERTAIN = "uncertain"

# A JSON escape such as "\t" eats the first letter of a LaTeX command
# ("\text" -> TAB + "ext").  Only commands whose remainder is recognised are restored.
_COMMANDS_AFTER_CONTROL = {
    "\t": ("t", "text textbf textit textrm times theta tau tanh tan tfrac tilde therefore triangle top to"),
    "\f": ("f", "frac forall flat"),
    "\b": ("b", "beta bar binom because bigg big bmod boxed bullet backslash"),
    "\r": ("r", "rightarrow right rangle rho rfloor rceil rbrace rm"),
    "\n": ("n", "neq nleq ngeq neg nabla notin nexists"),
}
_CONTROL_REPAIRS = [
    (re.compile(re.escape(char) + r"(?=(?:" + "|".join(
        re.escape(name[1:]) for name in sorted(names.split(), key=len, reverse=True)
    ) + r")(?![A-Za-z]))"), "\\" + letter)
    for char, (letter, names) in _COMMANDS_AFTER_CONTROL.items()
]
_UNRECOVERABLE_CONTROL = re.compile(r"[\x00-\x09\x0b-\x1f\x7f]")
_MATH_SPAN = re.compile(r"\$\$[\s\S]*?\$\$|\$[^$]*?\$|\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\]")
_PART_KEY = re.compile(r"^part_(\d+)$")


def repair_display_text(value: object) -> tuple[str, str]:
    """Return (display text, status); unknown control characters become U+FFFD."""
    text = ("" if value is None else str(value)).replace("\r\n", "\n")
    original = text
    for pattern, replacement in _CONTROL_REPAIRS:
        text = pattern.sub(lambda _m, r=replacement: r, text)
    status = STATUS_REPAIRED if text != original else STATUS_CLEAN
    if _UNRECOVERABLE_CONTROL.search(text):
        text = _UNRECOVERABLE_CONTROL.sub("\ufffd", text)
        status = STATUS_UNCERTAIN
    return text, status


def _worst(statuses: list[str]) -> str:
    for status in (STATUS_UNCERTAIN, STATUS_REPAIRED):
        if status in statuses:
            return status
    return STATUS_CLEAN


def _multi_part_values(text: str) -> list[object] | None:
    """Values of a stored multi-part answer; None when the text is not one.

    Only a JSON object, or a JSON array of strings, counts: "[1, 2]" is an
    interval and "{x | x > 3}" is a set, not storage format.
    """
    stripped = text.strip()
    if not stripped.startswith(("{", "[")):
        return None
    try:
        parsed = json.loads(stripped)
    except (TypeError, ValueError):
        return None
    if isinstance(parsed, dict) and parsed and all(
        value is None or isinstance(value, (str, int, float)) for value in parsed.values()
    ):
        def order(item: tuple[int, str]) -> tuple[int, int]:
            index, key = item
            match = _PART_KEY.match(str(key))
            return (int(match.group(1)), index) if match else (10**9, index)
        return [parsed[key] for _, key in sorted(enumerate(parsed), key=order)]
    if isinstance(parsed, list) and parsed and all(isinstance(value, str) for value in parsed):
        return list(parsed)
    return None


def answer_display(raw: object) -> dict:
    """Split a stored answer into display parts: {"parts": [{label, text, blank}], "status"}."""
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return {"parts": [], "status": STATUS_CLEAN}
    text = raw if isinstance(raw, str) else json.dumps(raw, ensure_ascii=False)
    values = _multi_part_values(text)
    sources = values if values is not None else [text]
    parts, statuses = [], []
    for index, value in enumerate(sources, start=1):
        blank = value is None or not str(value).strip()
        shown, status = repair_display_text("" if blank else str(value).strip())
        statuses.append(status)
        parts.append({
            "label": f"({index})" if len(sources) > 1 else "",
            "text": UNANSWERED_LABEL if blank else shown,
            "blank": blank,
        })
    return {"parts": parts, "status": _worst(statuses)}


def _open_brace_depth(text: str) -> int:
    depth = 0
    for index, char in enumerate(text):
        if char == "{" and (index == 0 or text[index - 1] != "\\"):
            depth += 1
        elif char == "}" and (index == 0 or text[index - 1] != "\\") and depth:
            depth -= 1
    return depth


def question_summary(raw: object, limit: int = 120) -> dict:
    """Shorten question text without cutting a math span or a TeX group in half."""
    text, status = repair_display_text(raw)
    text = text.strip()
    if len(text) <= limit:
        return {"text": text, "status": status, "truncated": False}
    cut = limit
    for span in _MATH_SPAN.finditer(text):
        if span.start() < cut < span.end():
            cut = span.start() if span.start() >= limit // 2 else span.end()
            break
    head = text[:cut]
    while _open_brace_depth(head) and "\\" in head:
        head = head[:head.rfind("\\")]
    return {"text": head.rstrip() + "…", "status": status, "truncated": True}


def install_attempt_math_display(app) -> None:
    app.add_template_filter(answer_display, "attempt_answer_display")
    app.add_template_filter(question_summary, "attempt_question_summary")
