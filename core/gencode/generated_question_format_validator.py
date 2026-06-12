# -*- coding: utf-8 -*-
"""
core/gencode/generated_question_format_validator.py
====================================================
全域題目格式與語系驗證器 (Global Question Format & Localization Validator)

版本: V1.0  日期: 2026-06-12
設計原則:
  - 單一來源 (Single Source of Truth)：runtime_skill_wrapper 與 runtime_smoke 均呼叫此模組
  - 只做 fail-fast 檢查，不做修復
  - 不丟 exception，回傳 blocker list
  - 不修改 DB schema，不修改個別 skill

Blockers（每種最多出現一次）:
  markdown_code_fence_detected   任何欄位含 ``` 標記
  latex_unbalanced               $ 數量為奇數（LaTeX 未閉合）
  latex_delimiter_not_allowed    使用 \\( \\) \\[ \\] 等非允許分隔符
  latex_empty_formula            出現 $ <空白> $ 空公式
  formula_not_wrapped            複雜公式出現在 $...$ 之外
  localization_violation         question_text 或選項出現整句英文
  choices_missing                選擇題但 choices 為空或缺失
  choices_duplicate              choices 有重複文字
  answer_not_in_choices          答案標籤超出 choices 數量範圍
"""
from __future__ import annotations

import re
from typing import Any

# ─────────────────────────────────────────────────────────────────────────────
# Compiled regexes (module-level, compiled once)
# ─────────────────────────────────────────────────────────────────────────────

# Markdown code fence
_RE_CODE_FENCE = re.compile(r"```")

# LaTeX delimiters that are NOT allowed: \( \) \[ \]
_RE_BAD_DELIMITERS = re.compile(r"\\\(|\\\)|\\\[|\\\]")

# Empty formula: $ followed by only whitespace then $
_RE_EMPTY_FORMULA = re.compile(r"\$[ \t]+\$")

# Strip $...$ inline blocks (non-greedy, does not cross newlines)
_RE_STRIP_LATEX = re.compile(r"\$[^$\n]*?\$")

# Escaped dollar \$ – not a real math delimiter
_RE_ESCAPED_DOLLAR = re.compile(r"\\\$")

# Named coordinate-point notation: single uppercase letter + (int, int)
# e.g. P(3,5)  A(-2,4)  B(0,-1)
# These are acceptable without $...$ in Chinese context and must NOT be
# flagged as formula_not_wrapped (false positive for _RE_COMBINATORICS).
_RE_COORD_POINT = re.compile(r"\b[A-Z]\s*\(\s*[+-]?\d+\s*,\s*[+-]?\d+\s*\)")

# ─────────────────────────────────────────────────────────────────────────────
# "formula_not_wrapped" detection patterns
# Applied to text AFTER stripping $...$ blocks.
# ─────────────────────────────────────────────────────────────────────────────

# Superscript notation: letter or ) followed by ^digit  e.g. x^2, y^3, a^2
_RE_SUPERSCRIPT = re.compile(r"[a-zA-Z\)]\^[0-9]")

# LaTeX commands that appeared outside $...$: \frac, \sqrt
_RE_LATEX_CMD = re.compile(r"\\(?:frac|sqrt)\b")

# Combinatorics: C(n,r) or P(n,r) style
_RE_COMBINATORICS = re.compile(r"\b[CP]\s*\(\s*[0-9a-z]")

# Factorial: letter or digit immediately followed by !  e.g. n!, r!, 5!
_RE_FACTORIAL = re.compile(r"[0-9a-zA-Z]!")

# Function definition style: f(x)=  f(t)=  etc.
_RE_FUNC_DEF = re.compile(r"\bf\s*\([a-z]\)\s*=")

# y= followed by an algebraic expression (not a plain number or Chinese text)
# Matches: y=x  y=2x-1  y=ax^2  but NOT y=3  y=第三象限
_RE_EQ_Y = re.compile(r"\by\s*=\s*(?=[a-zA-Z]|\d+[a-zA-Z])")

# ax^2 style: letter or digit immediately before x^
_RE_QUAD_COEFF = re.compile(r"[0-9a-zA-Z]x\^")

# Grouped for iteration
_FORMULA_CHECKS = [
    _RE_SUPERSCRIPT,
    _RE_LATEX_CMD,
    _RE_COMBINATORICS,
    _RE_FACTORIAL,
    _RE_FUNC_DEF,
    _RE_EQ_Y,
    _RE_QUAD_COEFF,
]

# Field roots where formula_not_wrapped applies
_FORMULA_CHECK_ROOTS = frozenset({
    "question_text", "question", "choices", "explanation", "hints",
})

# Answer types treated as choice-type for structural checks
_CHOICE_ANSWER_TYPES = frozenset({
    "single_choice", "choice",
    "multi_choice", "multiple_choice",
})

# problem_type_id prefixes that imply a choice answer type
_CHOICE_PT_PREFIXES = (
    "single_choice_", "choice_",
    "multi_choice_", "multiple_choice_",
)

# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _has_chinese(text: str) -> bool:
    """Return True iff text contains at least one CJK character."""
    return bool(re.search(r"[\u4e00-\u9fff]", text))


# Single-letter variables and common math function names that should NOT
# count as "English words" when determining localization violations.
_MATH_TOKENS_LC = frozenset({
    "x", "y", "z", "t", "n", "m", "r", "k", "a", "b", "c",
    "f", "g", "h", "p", "q",
    "sin", "cos", "tan", "log", "ln", "exp",
    "a", "b", "c", "d", "e",
    "a0", "a1", "a2",
})


def _is_math_token(word: str) -> bool:
    return len(word) <= 1 or word.lower() in _MATH_TOKENS_LC


def _is_english_sentence(text: str) -> bool:
    """
    Conservative check for an English-sentence choice or question.
    Returns True only when ALL of:
      - no Chinese characters
      - length > 12
      - contains ≥ 3 distinct multi-char non-math English words
    Single-letter labels (A, B, C, D) and math tokens are excluded.
    """
    if _has_chinese(text):
        return False
    if len(text.strip()) <= 12:
        return False
    words = re.findall(r"[a-zA-Z]{2,}", text)
    non_math = [w for w in words if not _is_math_token(w)]
    return len(non_math) >= 3


def _collect_text_fields(payload: dict[str, Any]) -> list[tuple[str, str]]:
    """
    Traverse the payload and yield (field_path, text_value) for every
    non-empty string field that should be validated.
    """
    fields: list[tuple[str, str]] = []

    # Top-level string fields
    for key in ("question_text", "question", "explanation", "display_answer"):
        val = payload.get(key, "")
        if isinstance(val, str) and val.strip():
            fields.append((key, val))

    # choices (list of str or dict)
    choices = payload.get("choices") or []
    if isinstance(choices, list):
        for i, ch in enumerate(choices):
            if isinstance(ch, str):
                if ch.strip():
                    fields.append((f"choices[{i}]", ch))
            elif isinstance(ch, dict):
                for k in ("text", "value"):
                    v = ch.get(k, "")
                    if isinstance(v, str) and v.strip():
                        fields.append((f"choices[{i}].{k}", v))

    # hints (list of str or dict)
    hints = payload.get("hints") or []
    if isinstance(hints, list):
        for i, h in enumerate(hints):
            if isinstance(h, str) and h.strip():
                fields.append((f"hints[{i}]", h))
            elif isinstance(h, dict):
                t = h.get("text", "")
                if isinstance(t, str) and t.strip():
                    fields.append((f"hints[{i}].text", t))

    # metadata sub-fields
    meta = payload.get("metadata") or {}
    if isinstance(meta, dict):
        # givens[].text
        for i, g in enumerate(meta.get("givens") or []):
            if isinstance(g, dict):
                t = g.get("text", "")
                if isinstance(t, str) and t.strip():
                    fields.append((f"metadata.givens[{i}].text", t))

        # target text-like fields
        target = meta.get("target") or {}
        if isinstance(target, dict):
            for k in ("text", "label", "description"):
                v = target.get(k, "")
                if isinstance(v, str) and v.strip():
                    fields.append((f"metadata.target.{k}", v))

        # derivation[].text / description / expression
        for i, d in enumerate(meta.get("derivation") or []):
            if isinstance(d, dict):
                for k in ("text", "description", "expression"):
                    v = d.get(k, "")
                    if isinstance(v, str) and v.strip():
                        fields.append((f"metadata.derivation[{i}].{k}", v))

    return fields


def _check_code_fence(text: str) -> bool:
    return bool(_RE_CODE_FENCE.search(text))


def _check_latex_balance(text: str) -> tuple[bool, bool, bool]:
    """
    Returns (unbalanced, bad_delimiters, empty_formula).
    unbalanced:     raw $ count (after removing \\$) is odd
    bad_delimiters: \\( \\) \\[ \\] found
    empty_formula:  $<whitespace>$ found
    """
    clean = _RE_ESCAPED_DOLLAR.sub("XX", text)  # neutralise \$ before counting
    dollar_count = clean.count("$")
    unbalanced = (dollar_count % 2 != 0)
    bad_delimiters = bool(_RE_BAD_DELIMITERS.search(text))
    empty_formula = bool(_RE_EMPTY_FORMULA.search(text))
    return unbalanced, bad_delimiters, empty_formula


def _check_formula_not_wrapped(text: str) -> bool:
    """
    Return True if text contains formula-like patterns OUTSIDE of $...$ blocks.
    Strategy: strip all $...$ spans first, then apply regex checks to the remainder.
    Named coordinate-point notation (e.g. P(3,5)) is excluded to prevent
    false positives from the combinatorics pattern check.
    """
    stripped = _RE_STRIP_LATEX.sub("", text)
    stripped = _RE_ESCAPED_DOLLAR.sub("", stripped)
    # Remove named coordinate-point patterns before formula checks to avoid
    # false positives (P(3,5) coordinate point looks like P(n,r) combinatorics).
    stripped = _RE_COORD_POINT.sub("", stripped)
    return any(pat.search(stripped) for pat in _FORMULA_CHECKS)


def _get_effective_answer_type(payload: dict[str, Any]) -> str:
    at = str(payload.get("answer_type") or "").strip().lower()
    if not at:
        ac = payload.get("answer_contract") or {}
        if isinstance(ac, dict):
            at = str(ac.get("answer_type") or "").strip().lower()
    return at


def _check_choices_structure(payload: dict[str, Any]) -> list[str]:
    """
    Structural checks for choice-type answers:
      - choices must exist and be non-empty
      - no duplicate choice texts
      - answer label (A/B/C/D) must be within choices count
    """
    errors: list[str] = []
    answer_type = _get_effective_answer_type(payload)
    pt = str(payload.get("problem_type_id") or "").lower()

    is_choice = (
        answer_type in _CHOICE_ANSWER_TYPES
        or pt.startswith(_CHOICE_PT_PREFIXES)
    )
    if not is_choice:
        return errors

    choices = payload.get("choices") or payload.get("options")
    if not isinstance(choices, list) or len(choices) == 0:
        errors.append("choices_missing")
        return errors

    # Extract normalised text for dedup check
    choice_texts: list[str] = []
    for ch in choices:
        if isinstance(ch, str):
            choice_texts.append(ch.strip())
        elif isinstance(ch, dict):
            t = str(
                ch.get("text") or ch.get("value") or ch.get("label") or ""
            ).strip()
            choice_texts.append(t)
        else:
            choice_texts.append(str(ch).strip())

    if len(choice_texts) != len(set(choice_texts)):
        errors.append("choices_duplicate")

    # Answer label range check
    ans = payload.get("correct_answer") or payload.get("answer")
    if ans is not None:
        ans_str = str(ans).strip().upper()
        # Only validate single-letter A–Z labels
        if len(ans_str) == 1 and "A" <= ans_str <= "Z":
            label_idx = ord(ans_str) - ord("A")  # A→0, B→1, …
            if label_idx >= len(choices):
                errors.append("answer_not_in_choices")

    return errors


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def validate_generated_question_format(
    payload: dict[str, Any],
    *,
    skill_id: str = "",
    problem_type_spec: dict[str, Any] | None = None,
) -> list[str]:
    """
    Global format and localization validator for auto-generated question payloads.

    Parameters
    ----------
    payload:            The runtime question payload dict.
    skill_id:           Optional skill ID for context (not used in checks yet,
                        reserved for future per-skill overrides).
    problem_type_spec:  Optional spec dict (reserved; not required for current rules).

    Returns
    -------
    Sorted list of blocker strings.  Empty list means no issues.
    Never raises an exception.
    """
    if not isinstance(payload, dict) or not payload:
        return []

    blockers: set[str] = set()

    # ── Collect all text fields ───────────────────────────────────────────
    try:
        fields = _collect_text_fields(payload)
    except Exception:  # pragma: no cover – defensive
        fields = []

    # ── Per-field checks ─────────────────────────────────────────────────
    for field_path, text in fields:
        field_root = field_path.split("[")[0].split(".")[0]

        # 1. Markdown code fence
        if _check_code_fence(text):
            blockers.add("markdown_code_fence_detected")

        # 2. LaTeX balance & delimiter checks
        try:
            unbalanced, bad_delim, empty_formula = _check_latex_balance(text)
        except Exception:  # pragma: no cover
            unbalanced = bad_delim = empty_formula = False

        if unbalanced:
            blockers.add("latex_unbalanced")
        if bad_delim:
            blockers.add("latex_delimiter_not_allowed")
        if empty_formula:
            blockers.add("latex_empty_formula")

        # 3. Formula wrapping (content-bearing fields only)
        if field_root in _FORMULA_CHECK_ROOTS:
            try:
                if _check_formula_not_wrapped(text):
                    blockers.add("formula_not_wrapped")
            except Exception:  # pragma: no cover
                pass

    # ── Localization: question_text ───────────────────────────────────────
    qt = str(payload.get("question_text") or payload.get("question") or "").strip()
    if qt and len(qt) > 12 and not _has_chinese(qt):
        blockers.add("localization_violation")

    # Localization: choices (each choice text)
    choices_raw = payload.get("choices") or []
    if isinstance(choices_raw, list):
        for ch in choices_raw:
            text_val: str = ""
            if isinstance(ch, str):
                text_val = ch
            elif isinstance(ch, dict):
                text_val = str(ch.get("text") or ch.get("value") or "")
            if _is_english_sentence(text_val):
                blockers.add("localization_violation")
                break

    # ── Choices structural checks ────────────────────────────────────────
    try:
        blockers.update(_check_choices_structure(payload))
    except Exception:  # pragma: no cover
        pass

    return sorted(blockers)
