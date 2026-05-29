from __future__ import annotations

import math
import random
from typing import Any, Callable

from core.gencode.answer_payload import answer_type_family
from core.gencode.problem_type_spec import get_answer_contract, get_stem_contract
from core.gencode.symbolic_coordinate_templates import (
    SYMBOLIC_QUADRANT_SHORT_ANSWER_TEMPLATES,
    SYMBOLIC_STATEMENT_CHOICE_TEMPLATES,
    build_symbolic_quadrant_metadata,
    build_symbolic_quadrant_question_text,
)
from core.gencode.template_slot_resolver import resolve_template_slot
from core.gencode.validators import validate_generator_payload

GeneratorFn = Callable[[str, str, dict[str, Any], int | None], dict[str, Any]]


def _quadrant_name(x: int, y: int) -> str:
    if x > 0 and y > 0:
        return "第一象限"
    if x < 0 and y > 0:
        return "第二象限"
    if x < 0 and y < 0:
        return "第三象限"
    return "第四象限"


def _build_choice_payload(
    skill_id: str,
    problem_type_id: str,
    stem: str,
    correct_text: str,
    wrong_texts: list[str],
    *,
    answer_type: str,
    checker_type: str,
    metadata: dict[str, Any],
    diagnosis_tags: list[str],
    explanation: str,
    seed: int | None,
) -> dict[str, Any]:
    rng = random.Random(seed)
    option_pool = [{"is_correct": True, "text": correct_text}] + [
        {"is_correct": False, "text": t} for t in wrong_texts[:3]
    ]
    rng.shuffle(option_pool)
    choices: list[dict[str, str]] = []
    ans = "A"
    for i, opt in enumerate(option_pool):
        label = chr(ord("A") + i)
        choices.append({"label": label, "text": str(opt.get("text", ""))})
        if opt.get("is_correct"):
            ans = label
    return {
        "skill_id": skill_id,
        "problem_type_id": problem_type_id,
        "question_text": stem,
        "question": stem,
        "choices": choices,
        "options": [str(c["text"]) for c in choices],
        "answer": ans,
        "correct_answer": ans,
        "answer_type": answer_type,
        "checker_type": checker_type,
        "explanation": explanation,
        "diagnosis_tags": diagnosis_tags,
        "metadata": metadata,
        "source": "gencode_slot_generator",
    }


def _slot_point_quadrant(skill_id: str, pt: str, spec: dict[str, Any], seed: int | None) -> dict[str, Any]:
    rng = random.Random(seed)
    x = rng.choice([i for i in range(-9, 10) if i != 0])
    y = rng.choice([i for i in range(-9, 10) if i != 0])
    quadrant = _quadrant_name(x, y)
    q = f"點 P({x},{y}) 位於第幾象限？"
    return {
        "skill_id": skill_id,
        "problem_type_id": pt,
        "question_text": q,
        "question": q,
        "choices": [],
        "answer": quadrant,
        "correct_answer": quadrant,
        "answer_type": "short_answer",
        "checker_type": "text_checker",
        "explanation": "依 x 與 y 的正負判斷象限。",
        "diagnosis_tags": ["quadrant_sign_reasoning"],
        "metadata": {
            "givens": [f"x={x}", f"y={y}"],
            "target": quadrant,
            "derivation": [f"x={x}", f"y={y}", f"象限={quadrant}"],
        },
        "source": "gencode_slot_generator",
    }


def _slot_point_quadrant_choice(skill_id: str, pt: str, spec: dict[str, Any], seed: int | None) -> dict[str, Any]:
    rng = random.Random(seed)
    x = rng.choice([i for i in range(-9, 10) if i != 0])
    y = rng.choice([i for i in range(-9, 10) if i != 0])
    quadrant = _quadrant_name(x, y)
    stem = f"點 P({x},{y}) 位於第幾象限？"
    return _build_choice_payload(
        skill_id,
        pt,
        stem,
        quadrant,
        [q for q in ["第一象限", "第二象限", "第三象限", "第四象限"] if q != quadrant],
        answer_type="single_choice",
        checker_type="choice_label_checker",
        metadata={"givens": [f"x={x}", f"y={y}"], "target": quadrant, "derivation": [f"x={x}", f"y={y}", f"象限={quadrant}"]},
        diagnosis_tags=["quadrant_sign_reasoning"],
        explanation="依座標符號判斷象限。",
        seed=seed,
    )


def _requires_symbolic_coordinate(spec: dict[str, Any]) -> bool:
    required = get_stem_contract(spec).get("required_math_objects", [])
    if not isinstance(required, list):
        return False
    return "symbolic_condition" in required and "coordinate_point" in required


def _slot_symbolic_quadrant(skill_id: str, pt: str, spec: dict[str, Any], seed: int | None) -> dict[str, Any]:
    rng = random.Random(seed)
    template = SYMBOLIC_QUADRANT_SHORT_ANSWER_TEMPLATES[rng.randrange(len(SYMBOLIC_QUADRANT_SHORT_ANSWER_TEMPLATES))]
    metadata = build_symbolic_quadrant_metadata(template)
    q = build_symbolic_quadrant_question_text(template)
    answer = str(template["answer"])
    return {
        "skill_id": skill_id,
        "problem_type_id": pt,
        "question_text": q,
        "question": q,
        "choices": [],
        "answer": answer,
        "correct_answer": answer,
        "answer_type": "short_answer",
        "checker_type": "text_checker",
        "explanation": " ".join(metadata["derivation"]),
        "diagnosis_tags": ["symbolic_sign_reasoning", f"template_{template['template_id']}"],
        "metadata": metadata,
        "source": "gencode_slot_generator",
    }


def _slot_symbolic_quadrant_choice(skill_id: str, pt: str, spec: dict[str, Any], seed: int | None) -> dict[str, Any]:
    rng = random.Random(seed)
    a = rng.randint(-9, -2)
    b = rng.randint(a + 1, -1)
    x = a * b
    y = a + b
    stem = f"設 $a,b$ 為實數，且 $a<b<0$，則點 $Q({x},{y})$ 位於第幾象限？"
    correct = "第四象限"
    return _build_choice_payload(
        skill_id,
        pt,
        stem,
        correct,
        ["第一象限", "第二象限", "第三象限"],
        answer_type="single_choice",
        checker_type="choice_label_checker",
        metadata={
            "givens": ["a<b<0", f"x={x}", f"y={y}"],
            "target": correct,
            "derivation": ["a<0,b<0", f"x={x}>0", f"y={y}<0", "故為第四象限"],
        },
        diagnosis_tags=["symbolic_sign_reasoning"],
        explanation="由符號條件推得象限。",
        seed=seed,
    )


def _slot_axis_distance_choice(skill_id: str, pt: str, spec: dict[str, Any], seed: int | None) -> dict[str, Any]:
    rng = random.Random(seed)
    x = rng.choice([i for i in range(-9, 10) if i != 0])
    y = rng.choice([i for i in range(-9, 10) if i != 0])
    axis = rng.choice(["x_axis", "y_axis"])
    if axis == "x_axis":
        target = abs(y)
        axis_label = "x 軸"
        derivation = f"到 x 軸距離為 |y|=|{y}|={target}"
        explanation = f"點 P({x},{y}) 到 x 軸的距離為 y 座標的絕對值 |y|={target}。"
        wrong_axis_value = abs(x)
    else:
        target = abs(x)
        axis_label = "y 軸"
        derivation = f"到 y 軸距離為 |x|=|{x}|={target}"
        explanation = f"點 P({x},{y}) 到 y 軸的距離為 x 座標的絕對值 |x|={target}。"
        wrong_axis_value = abs(y)
    stem = f"點 P({x},{y}) 到 {axis_label}的距離為何？"
    correct = str(target)
    distractors: list[str] = []
    for candidate in (wrong_axis_value, target + 1, max(1, target - 1), target + 2, wrong_axis_value + 1):
        text = str(candidate)
        if text != correct and text not in distractors:
            distractors.append(text)
    while len(distractors) < 3:
        filler = str(target + len(distractors) + 3)
        if filler not in distractors and filler != correct:
            distractors.append(filler)
    return _build_choice_payload(
        skill_id,
        pt,
        stem,
        correct,
        distractors[:3],
        answer_type="single_choice",
        checker_type="choice_label_checker",
        metadata={
            "givens": [
                {
                    "type": "coordinate_point",
                    "text": f"P({x},{y})",
                    "variables": [],
                }
            ],
            "target": {
                "type": "axis_distance",
                "label": "P",
                "x_expr": str(x),
                "y_expr": str(y),
                "variables": [],
                "distance_to": axis,
                "value": correct,
            },
            "derivation": [derivation],
        },
        diagnosis_tags=["axis_distance"],
        explanation=explanation,
        seed=seed,
    )


def _slot_symbolic_quadrant_statement_choice(skill_id: str, pt: str, spec: dict[str, Any], seed: int | None) -> dict[str, Any]:
    rng = random.Random(seed)
    template = SYMBOLIC_STATEMENT_CHOICE_TEMPLATES[rng.randrange(len(SYMBOLIC_STATEMENT_CHOICE_TEMPLATES))]
    meta = template["metadata"]
    return _build_choice_payload(
        skill_id,
        pt,
        str(template["stem"]),
        str(template["correct"]),
        list(template["wrongs"]),
        answer_type="single_choice",
        checker_type="choice_label_checker",
        metadata={
            "givens": list(meta.get("givens", [])),
            "target": dict(meta.get("target", {})),
            "derivation": list(meta.get("derivation", [])),
        },
        diagnosis_tags=["symbolic_sign_reasoning", f"template_{template['template_id']}"],
        explanation=" ".join(meta.get("derivation", [])),
        seed=seed,
    )


def _slot_generic_single_choice(skill_id: str, pt: str, spec: dict[str, Any], seed: int | None) -> dict[str, Any]:
    rng = random.Random(seed)
    a = rng.randint(2, 12)
    b = rng.randint(2, 12)
    stem = f"已知 a={a}, b={b}，下列何者為 a+b？"
    correct = str(a + b)
    return _build_choice_payload(
        skill_id,
        pt,
        stem,
        correct,
        [str(a + b + 1), str(a + b - 1), str(a + b + 2)],
        answer_type="single_choice",
        checker_type="choice_label_checker",
        metadata={"givens": [f"a={a}", f"b={b}"], "target": correct, "derivation": [f"a+b={correct}"]},
        diagnosis_tags=["generic_arithmetic"],
        explanation="計算 a+b。",
        seed=seed,
    )


def _slot_generic_short_answer(skill_id: str, pt: str, spec: dict[str, Any], seed: int | None) -> dict[str, Any]:
    if _requires_symbolic_coordinate(spec):
        raise RuntimeError("generator_not_semantically_safe:symbolic_condition_requires_symbolic_coordinate_template")
    rng = random.Random(seed)
    a = rng.randint(2, 12)
    b = rng.randint(2, 12)
    ans = str(a + b)
    q = f"計算 {a}+{b} 的值。"
    return {
        "skill_id": skill_id,
        "problem_type_id": pt,
        "question_text": q,
        "question": q,
        "choices": [],
        "answer": ans,
        "correct_answer": ans,
        "answer_type": "short_answer",
        "checker_type": "text_checker",
        "explanation": f"{a}+{b}={ans}",
        "diagnosis_tags": ["generic_arithmetic"],
        "metadata": {
            "givens": [{"type": "numeric", "text": f"a={a}", "variables": []}],
            "target": {"type": "numeric", "label": "", "x_expr": ans, "y_expr": "", "variables": []},
            "derivation": [f"{a}+{b}={ans}"],
        },
        "source": "gencode_slot_generator",
    }


def _slot_two_point_distance_solution_set(
    skill_id: str, pt: str, spec: dict[str, Any], seed: int | None
) -> dict[str, Any]:
    rng = random.Random(seed)
    for _ in range(80):
        mid = rng.randint(-4, 8)
        t = rng.randint(2, 6)
        dx = rng.choice([4, 6, 8])
        d2 = dx * dx + t * t
        d = math.isqrt(d2)
        if d * d != d2:
            continue
        x1, x2 = 3, 3 + dx
        y2 = mid
        k1, k2 = mid - t, mid + t
        solutions = sorted({k1, k2})
        q = f"已知 A({x1}, k)、B({x2}, {y2})，且 AB={d}，求 k 的所有可能值。"
        ac = get_answer_contract(spec)
        return {
            "skill_id": skill_id,
            "problem_type_id": pt,
            "question_text": q,
            "question": q,
            "choices": [],
            "answer": solutions,
            "correct_answer": solutions,
            "answer_type": str(ac.get("answer_type", "solution_set")),
            "checker_type": str(ac.get("checker", "solution_set_checker")),
            "explanation": f"由距離公式得 (k-{y2})^2+{dx}^2={d}^2，解得 k={solutions[0]} 或 k={solutions[1]}。",
            "diagnosis_tags": ["distance_formula_reasoning"],
            "metadata": {
                "givens": [f"A=({x1},k)", f"B=({x2},{y2})", f"AB={d}"],
                "target": "k",
                "derivation": [f"(k-{y2})^2+{dx}^2={d}^2", f"k∈{solutions}"],
            },
            "source": "gencode_slot_generator",
        }
    raise RuntimeError("two_point_distance_solution_set_generation_failed")


def _slot_two_point_distance_compute(
    skill_id: str, pt: str, spec: dict[str, Any], seed: int | None
) -> dict[str, Any]:
    rng = random.Random(seed)
    for _ in range(80):
        x1, y1 = rng.randint(-6, 6), rng.randint(-6, 6)
        x2, y2 = rng.randint(-6, 6), rng.randint(-6, 6)
        dx, dy = x2 - x1, y2 - y1
        d2 = dx * dx + dy * dy
        if d2 <= 0:
            continue
        d = math.isqrt(d2)
        if d * d == d2:
            ans = str(d)
        else:
            ans = f"\\sqrt{{{d2}}}"
        q = f"求 A({x1},{y1}) 與 B({x2},{y2}) 的距離。"
        ac = get_answer_contract(spec)
        return {
            "skill_id": skill_id,
            "problem_type_id": pt,
            "question_text": q,
            "question": q,
            "choices": [],
            "answer": ans,
            "correct_answer": ans,
            "answer_type": str(ac.get("answer_type", "numeric_or_radical")),
            "checker_type": str(ac.get("checker", "expression_equivalence_checker")),
            "explanation": f"AB=\\sqrt{{({dx})^2+({dy})^2}}={ans}。",
            "diagnosis_tags": ["distance_formula_reasoning"],
            "metadata": {
                "givens": [f"A=({x1},{y1})", f"B=({x2},{y2})"],
                "target": "AB",
                "derivation": [f"dx={dx}", f"dy={dy}", f"AB={ans}"],
            },
            "source": "gencode_slot_generator",
        }
    raise RuntimeError("two_point_distance_compute_generation_failed")


SLOT_REGISTRY: dict[str, GeneratorFn] = {
    "point_quadrant": _slot_point_quadrant,
    "point_quadrant_choice": _slot_point_quadrant_choice,
    "symbolic_quadrant": _slot_symbolic_quadrant,
    "symbolic_quadrant_choice": _slot_symbolic_quadrant_choice,
    "axis_distance_choice": _slot_axis_distance_choice,
    "symbolic_quadrant_statement_choice": _slot_symbolic_quadrant_statement_choice,
    "two_point_distance_solution_set": _slot_two_point_distance_solution_set,
    "two_point_distance_compute": _slot_two_point_distance_compute,
}


def generate_from_problem_type_spec(
    skill_id: str,
    problem_type_spec: dict[str, Any],
    *,
    seed: int | None = None,
) -> dict[str, Any]:
    pt = str(problem_type_spec.get("problem_type_id", "")).strip()
    slot = resolve_template_slot(problem_type_spec, seed)
    fn = SLOT_REGISTRY.get(slot)
    if fn is None:
        if _requires_symbolic_coordinate(problem_type_spec):
            raise RuntimeError("pending_template:symbolic_coordinate_slot_required")
        ac = get_answer_contract(problem_type_spec)
        at = str(ac.get("answer_type", "")).strip()
        if at == "single_choice":
            fn = _slot_generic_single_choice
        elif at == "short_answer":
            fn = _slot_generic_short_answer
        elif answer_type_family(at) == "solution_set":
            fn = _slot_two_point_distance_solution_set
        elif answer_type_family(at) in {"numeric_or_radical", "numeric"}:
            fn = _slot_two_point_distance_compute
        else:
            raise RuntimeError(f"slot_generator_not_registered:{slot or at}")
    payload = fn(skill_id, pt, problem_type_spec, seed)
    errors = validate_generator_payload(payload, skill_id=skill_id, problem_type_spec=problem_type_spec)
    if errors:
        raise RuntimeError(f"generator_semantically_unsafe:{','.join(errors)}")
    return payload
