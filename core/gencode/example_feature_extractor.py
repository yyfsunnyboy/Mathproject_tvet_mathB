from __future__ import annotations

import re
from fractions import Fraction
from typing import Any

from core.gencode.answer_contract_bridge import legacy_fields_from_answer_contract
from core.gencode.validators.answer_contract_validator import CHOICE_EMBEDDED_PATTERN, LABEL_ONLY_PATTERN

_CHOICE_LINE = re.compile(r"[\(（]\s*([A-Da-d])\s*[\)）]")
_COORD_POINT = re.compile(r"[PQABCD]\s*\\?\s*\(?\s*[^)\n]{1,40}\)?", re.I)
_SYMBOLIC_COND = re.compile(r"a\s*<\s*b|a\s*<\s*b\s*<\s*0|變數|符號", re.I)
_AXIS_DIST = re.compile(r"到\s*[xyXY]\s*軸|距離.*軸|axis", re.I)
_QUADRANT = re.compile(r"象限|quadrant", re.I)
_PROB = re.compile(r"機率|樣本空間|probability", re.I)
_COMB = re.compile(r"排列|組合|選法|permutation|combination", re.I)
_STATS = re.compile(r"平均數|中位數|標準差|mean|median|std", re.I)
_GRAPH = re.compile(r"函數圖形|座標圖|graph", re.I)
_TABLE = re.compile(r"表格|table", re.I)
_VAR = re.compile(r"\b[a-zA-Z]\b")


def _source_text(ex: dict[str, Any]) -> str:
    for k in ("problem_text", "problem", "question", "stem", "content"):
        v = str(ex.get(k, "")).strip()
        if v:
            return v
    return ""


def _source_answer(ex: dict[str, Any]) -> str:
    return str(ex.get("correct_answer") or ex.get("answer") or "").strip()


def _parse_embedded_choices(question_text: str) -> list[str]:
    choices: list[str] = []
    for m in _CHOICE_LINE.finditer(question_text):
        label = m.group(1).upper()
        start = m.end()
        nxt = _CHOICE_LINE.search(question_text, start)
        end = nxt.start() if nxt else len(question_text)
        text = question_text[start:end].strip(" 　\r\n\t:：.")
        if text:
            choices.append(text)
    return choices


def _infer_answer_type(question_text: str, answer: str, choices: list[str], has_choices: bool) -> str:
    ans = answer.strip()
    if has_choices or LABEL_ONLY_PATTERN.match(ans) or (choices and ans in choices):
        return "single_choice"
    if re.fullmatch(r"-?\d+(\.\d+)?", ans):
        return "numeric"
    if re.fullmatch(r"-?\d+/\d+", ans):
        return "fraction"
    try:
        Fraction(ans)
        if "/" in ans:
            return "fraction"
    except Exception:
        pass
    if re.search(r"[+\-*/^]|\\frac|=", ans):
        return "expression"
    if ans and not has_choices:
        return "short_answer"
    if CHOICE_EMBEDDED_PATTERN.search(question_text):
        return "single_choice"
    return "short_answer"


def _detect_math_objects(text: str) -> list[str]:
    objs: list[str] = []
    if _COORD_POINT.search(text) or "坐標" in text or "座標" in text:
        objs.append("coordinate_point")
    if _SYMBOLIC_COND.search(text):
        objs.append("symbolic_condition")
    if _AXIS_DIST.search(text):
        objs.append("axis_distance")
    if re.search(r"代數|expression|多項式", text, re.I):
        objs.append("expression")
    if _TABLE.search(text):
        objs.append("table")
    if _GRAPH.search(text):
        objs.append("graph")
    if _PROB.search(text):
        objs.append("probability_context")
    if _COMB.search(text):
        objs.append("combinatorics_context")
    if _STATS.search(text):
        objs.append("statistics_context")
    return sorted(set(objs))


def _infer_target_task(text: str, math_objects: list[str], answer_type: str) -> str:
    if _QUADRANT.search(text) and answer_type == "short_answer":
        return "classify_quadrant"
    if _AXIS_DIST.search(text):
        return "choose_possible_coordinate"
    if answer_type == "single_choice" and _QUADRANT.search(text):
        return "choose_correct_statement"
    if _PROB.search(text):
        return "compute_probability"
    if _COMB.search(text):
        return "count_arrangements"
    if _STATS.search(text):
        return "read_table"
    if _GRAPH.search(text):
        return "read_graph"
    if _TABLE.search(text):
        return "read_table"
    if re.search(r"化簡|因式|expand|simplify", text, re.I):
        return "simplify_expression"
    if re.search(r"解方程式|solve", text, re.I):
        return "solve_equation"
    if "coordinate_point" in math_objects:
        return "classify_quadrant"
    return "compute_numeric"


def _infer_reasoning_type(text: str, math_objects: list[str], target_task: str) -> list[str]:
    types: list[str] = []
    if _AXIS_DIST.search(text) or target_task == "choose_possible_coordinate":
        types.append("axis_distance_reasoning")
    if _QUADRANT.search(text) or "symbolic_condition" in math_objects:
        types.append("sign_reasoning")
    if _PROB.search(text):
        types.append("probability_reasoning")
    if _COMB.search(text):
        types.append("combinatorics_counting")
    if _STATS.search(text):
        types.append("statistics_computation")
    if _GRAPH.search(text):
        types.append("graph_reading")
    if _TABLE.search(text):
        types.append("table_reading")
    if re.search(r"代數|符號", text):
        types.append("symbolic_algebra")
    if not types:
        types.append("numeric_computation")
    return sorted(set(types))


def extract_example_feature(ex: dict[str, Any]) -> dict[str, Any]:
    ex_id = ex.get("id") or ex.get("example_id")
    question_text = _source_text(ex)
    answer = _source_answer(ex)
    embedded = _parse_embedded_choices(question_text)
    raw_choices = ex.get("choices") or ex.get("options")
    choices_list: list[str] = []
    if isinstance(raw_choices, list):
        for ch in raw_choices:
            if isinstance(ch, dict):
                choices_list.append(str(ch.get("text", "")).strip())
            else:
                choices_list.append(str(ch).strip())
    if embedded:
        choices_list = embedded
    has_choices = len(choices_list) >= 2
    stem_embeds_choices = bool(CHOICE_EMBEDDED_PATTERN.search(question_text)) or bool(embedded)
    answer_type = _infer_answer_type(question_text, answer, choices_list, has_choices)
    math_objects = _detect_math_objects(question_text)
    target_task = _infer_target_task(question_text, math_objects, answer_type)
    reasoning_type = _infer_reasoning_type(question_text, math_objects, target_task)
    variables = sorted(set(_VAR.findall(question_text)))
    givens = [v for v in variables if v.isalpha()]
    bridge = legacy_fields_from_answer_contract({"answer_type": answer_type, "answer_equivalence": "choice_label" if answer_type == "single_choice" else "exact_text"})
    return {
        "source_example_id": ex_id,
        "question_text": question_text,
        "answer": answer,
        "choices": choices_list,
        "has_choices": has_choices,
        "stem_embeds_choices": stem_embeds_choices,
        "answer_type": answer_type,
        "answer_shape": bridge["answer_shape"],
        "checker": bridge["checker_key"],
        "equivalence": bridge["equivalence_type"],
        "math_objects": math_objects,
        "target_task": target_task,
        "reasoning_type": reasoning_type,
        "required_derivation": True,
        "variables": variables,
        "givens": givens,
        "target": target_task,
    }
