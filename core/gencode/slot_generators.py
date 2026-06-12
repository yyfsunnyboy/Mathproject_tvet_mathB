from __future__ import annotations

import math
import random
from fractions import Fraction
from typing import Any, Callable

from core.gencode.answer_payload import answer_type_family, apply_coordinate_pair_runtime_fields
from core.gencode.problem_type_spec import get_answer_contract, get_semantic_contract, get_stem_contract
from core.gencode.symbolic_coordinate_templates import (
    SYMBOLIC_QUADRANT_SHORT_ANSWER_TEMPLATES,
    SYMBOLIC_STATEMENT_CHOICE_TEMPLATES,
    build_symbolic_quadrant_metadata,
    build_symbolic_quadrant_question_text,
)
from core.gencode.division_point_slot_engine import (
    DIVISION_POINT_SLOT,
    generate_division_point_payload,
    is_division_point_target_task,
)
from core.gencode.template_slot_resolver import infer_registered_task_token, resolve_template_slot
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


def _slot_division_point_coordinates(
    skill_id: str, pt: str, spec: dict[str, Any], seed: int | None
) -> dict[str, Any]:
    target = str(spec.get("target_task", "")).strip()
    if not is_division_point_target_task(target):
        raise RuntimeError(f"division_point_slot_unsupported_target:{target}")
    return generate_division_point_payload(skill_id, pt, spec, seed)


def _slot_linear_triangle_median_compute(
    skill_id: str, pt: str, spec: dict[str, Any], seed: int | None
) -> dict[str, Any]:
    rng = random.Random(f"{seed}|triangle_median|{pt}")
    ac = get_answer_contract(spec)
    answer_family = answer_type_family(str(ac.get("answer_type", "")))

    def _fmt_fraction(value: Fraction) -> str:
        return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"

    def _sqrt_fraction(value: Fraction) -> tuple[str, bool]:
        numerator_root = math.isqrt(value.numerator)
        denominator_root = math.isqrt(value.denominator)
        if numerator_root * numerator_root == value.numerator and denominator_root * denominator_root == value.denominator:
            return _fmt_fraction(Fraction(numerator_root, denominator_root)), True
        return f"\\sqrt{{{_fmt_fraction(value)}}}", False

    for _ in range(200):
        ax, ay = rng.randint(-8, 8), rng.randint(-8, 8)
        bx, by = rng.randint(-8, 8), rng.randint(-8, 8)
        cx, cy = rng.randint(-8, 8), rng.randint(-8, 8)
        determinant = (bx - ax) * (cy - ay) - (cx - ax) * (by - ay)
        if determinant == 0:
            continue
        mx = Fraction(bx + cx, 2)
        my = Fraction(by + cy, 2)
        dx = mx - ax
        dy = my - ay
        distance_squared = dx * dx + dy * dy
        answer, is_rational = _sqrt_fraction(distance_squared)
        if answer_family == "numeric" and (not is_rational or "/" in answer):
            continue
        break
    else:
        raise RuntimeError("triangle_median_generation_failed")

    question = (
        "在平面直角坐標系中，已知三角形 ABC 的三個頂點坐標分別為 "
        f"$A({ax},{ay})$、$B({bx},{by})$、$C({cx},{cy})$。"
        "若 $M$ 為線段 $BC$ 的中點，請先使用中點公式，再求頂點 $A$ 到對邊中點 "
        "$M$ 的中線線段 $\\overline{AM}$ 長度。"
    )
    explanation = (
        f"由中點公式得 $M=({_fmt_fraction(mx)},{_fmt_fraction(my)})$。"
        f"再由兩點距離公式得 $\\overline{{AM}}={answer}$。"
    )
    checker = str(ac.get("checker") or ac.get("checker_key") or "expression_equivalence_checker").strip()
    return {
        "skill_id": skill_id,
        "problem_type_id": pt,
        "question_text": question,
        "question": question,
        "choices": [],
        "answer": answer,
        "correct_answer": answer,
        "answer_type": str(ac.get("answer_type") or "numeric_or_radical"),
        "checker_type": checker,
        "checker": checker,
        "explanation": explanation,
        "diagnosis_tags": ["midpoint_coordinates", "triangle_median", "distance_formula"],
        "metadata": {
            "givens": [
                {"type": "coordinate_point", "text": f"A({ax},{ay})", "variables": []},
                {"type": "coordinate_point", "text": f"B({bx},{by})", "variables": []},
                {"type": "coordinate_point", "text": f"C({cx},{cy})", "variables": []},
            ],
            "target": "median_length",
            "derivation": [
                f"M=({_fmt_fraction(mx)},{_fmt_fraction(my)})",
                f"AM^2={_fmt_fraction(distance_squared)}",
                f"AM={answer}",
            ],
            "problem_type_id": pt,
            "template_slot": "linear_triangle_median_compute",
        },
        "source": "gencode_slot_generator",
    }


def _linear_expression(slope: int, intercept: int, variable: str = "x") -> str:
    slope_term = variable if slope == 1 else f"-{variable}" if slope == -1 else f"{slope}{variable}"
    if intercept == 0:
        return slope_term
    sign = "+" if intercept > 0 else "-"
    return f"{slope_term}{sign}{abs(intercept)}"


def _function_value_choice_requested(spec: dict[str, Any], ac: dict[str, Any]) -> bool:
    gc = spec.get("generator_contract") if isinstance(spec.get("generator_contract"), dict) else {}
    pt_key = str(spec.get("problem_type_id", "")).strip().lower()
    target_task = str(spec.get("target_task", "")).strip().lower()
    answer_type = str(ac.get("answer_type", "")).strip()
    return bool(
        answer_type_family(answer_type) == "single_choice"
        or "choice" in pt_key
        or target_task == "interpret_function_notation"
        or bool(ac.get("source_has_choices"))
        or bool(gc.get("has_choices"))
    )


def _function_value_application_requested(spec: dict[str, Any], ac: dict[str, Any]) -> bool:
    gc = spec.get("generator_contract") if isinstance(spec.get("generator_contract"), dict) else {}
    pt_key = str(spec.get("problem_type_id", "")).strip().lower()
    target_task = str(spec.get("target_task", "")).strip().lower()
    answer_type = str(ac.get("answer_type", "")).strip()
    checker = str(ac.get("checker") or ac.get("checker_key") or "").strip()
    return bool(
        "application" in pt_key
        or "word_problem" in pt_key
        or pt_key.startswith("expression_evaluate_function_value")
        or (
            target_task == "evaluate_function_value"
            and bool(gc.get("contextual_application"))
            and (answer_type == "expression" or checker == "expression_checker")
        )
    )


def _slot_linear_function_two_point_choice(
    skill_id: str, pt: str, spec: dict[str, Any], seed: int | None
) -> dict[str, Any]:
    rng = random.Random(seed)
    ac = get_answer_contract(spec)
    slope = rng.choice([i for i in range(-5, 6) if i != 0])
    intercept = rng.randint(-8, 8)
    x1 = rng.randint(-5, 2)
    x2 = rng.randint(x1 + 1, 7)
    y1 = slope * x1 + intercept
    y2 = slope * x2 + intercept
    correct = f"f(x)={_linear_expression(slope, intercept)}"
    wrong_candidates = [
        f"f(x)={_linear_expression(-slope, intercept)}",
        f"f(x)={_linear_expression(slope, intercept + 1)}",
        f"f(x)={_linear_expression(slope, intercept - 1)}",
        f"f(x)={_linear_expression(slope + 1 if slope != -1 else slope - 1, intercept)}",
    ]
    wrongs: list[str] = []
    for candidate in wrong_candidates:
        if candidate != correct and candidate not in wrongs:
            wrongs.append(candidate)
    choice_contract = dict(ac)
    choice_contract.update(
        {
            "answer_type": "single_choice",
            "answer_shape": "choice_label",
            "answer_equivalence": "choice_label",
            "equivalence_type": "choice_label",
            "checker": "choice_label_checker",
            "checker_key": "choice_label_checker",
            "choices_required": True,
            "choice_count": 4,
            "correct_choice_count": 1,
            "frontend_render_choices": True,
        }
    )
    spec["answer_contract"] = choice_contract
    payload = _build_choice_payload(
        skill_id,
        pt,
        (
            f"已知線型函數 $f(x)=ax+b$ 的圖形通過點 $({x1},{y1})$ 與點 $({x2},{y2})$，"
            "請利用兩點條件聯立求出斜率與截距，並選出正確的函數關係式。"
        ),
        correct,
        wrongs,
        answer_type="single_choice",
        checker_type="choice_label_checker",
        metadata={
            "givens": [f"f({x1})={y1}", f"f({x2})={y2}"],
            "target": "f(x)=ax+b",
            "derivation": [
                f"{slope}=({y2}-{y1})/({x2}-{x1})",
                f"{intercept}={y1}-{slope}*({x1})",
                correct,
            ],
            "problem_type_id": pt,
            "template_slot": "linear_function_two_point_choice",
            "scenario": "two_point_linear_function_choice",
        },
        diagnosis_tags=["linear_function_two_point_system", "slope_intercept_reasoning"],
        explanation=f"由兩點可得斜率為 {slope}，再代回任一點得到截距為 {intercept}，所以 {correct}。",
        seed=seed,
    )
    payload["answer_contract"] = choice_contract
    payload["checker"] = "choice_label_checker"
    return payload


def _slot_linear_function_contextual_word_problem(
    skill_id: str, pt: str, spec: dict[str, Any], seed: int | None
) -> dict[str, Any]:
    rng = random.Random(seed)
    ac = get_answer_contract(spec)
    answer_type = str(ac.get("answer_type", "")).strip()
    checker = str(ac.get("checker") or ac.get("checker_key") or "").strip()
    scenario = rng.choice(["fuel_remaining", "mobile_plan", "mileage_subscription"])
    expression_answer = answer_type == "expression" or checker == "expression_checker"
    if scenario == "fuel_remaining":
        initial = rng.randint(45, 75)
        rate = rng.randint(1, 4)
        query_x = rng.randint(4, 10)
        expression = _linear_expression(-rate, initial)
        evaluated = initial - rate * query_x
        stem = (
            f"某輛汽車油箱原有 {initial} 公升汽油，之後每行駛 10 公里固定消耗 {rate} 公升。"
            f"若以 $x$ 表示已行駛的 10 公里數，$f(x)$ 表示剩餘油量，"
            + ("請寫出線型函數 $f(x)$ 的關係式。" if expression_answer else f"請求行駛 {query_x * 10} 公里後的剩餘油量。")
        )
        givens = [f"initial={initial}", f"rate={rate}", f"x={query_x}"]
    elif scenario == "mobile_plan":
        base_fee = rng.choice([199, 299, 399, 499])
        unit_fee = rng.randint(2, 6)
        query_x = rng.randint(10, 40)
        expression = _linear_expression(unit_fee, base_fee)
        evaluated = base_fee + unit_fee * query_x
        stem = (
            f"某手機方案每月基本費為 {base_fee} 元，超過基本額度後每增加 1 分鐘需加收 {unit_fee} 元。"
            f"若以 $x$ 表示超額分鐘數，$f(x)$ 表示當月總費用，"
            + ("請寫出線型函數 $f(x)$ 的關係式。" if expression_answer else f"請求超額使用 {query_x} 分鐘時的總費用。")
        )
        givens = [f"base_fee={base_fee}", f"unit_fee={unit_fee}", f"x={query_x}"]
    else:
        base_mileage = rng.randint(80, 150)
        per_km = rng.randint(2, 5)
        query_x = rng.randint(20, 120)
        expression = _linear_expression(per_km, base_mileage)
        evaluated = base_mileage + per_km * query_x
        stem = (
            f"某訂閱制租車方案每月含 {base_mileage} 公里基本里程，超額後每公里加收 {per_km} 元。"
            f"若以 $x$ 表示超額公里數，$f(x)$ 表示當月額外里程費用，"
            + ("請寫出線型函數 $f(x)$ 的關係式。" if expression_answer else f"請求超額行駛 {query_x} 公里時的額外費用。")
        )
        givens = [f"base_mileage={base_mileage}", f"per_km={per_km}", f"x={query_x}"]
    answer = expression if expression_answer else str(evaluated)
    checker_type = "expression_checker" if expression_answer else "numeric_checker"
    return {
        "skill_id": skill_id,
        "problem_type_id": pt,
        "question_text": stem,
        "question": stem,
        "choices": [],
        "answer": answer,
        "correct_answer": answer,
        "answer_type": "expression" if expression_answer else "numeric",
        "checker_type": checker_type,
        "checker": checker_type,
        "answer_contract": dict(ac),
        "explanation": f"依題意建立線型函數 $f(x)={expression}$。",
        "diagnosis_tags": ["linear_function_contextual_application", scenario],
        "metadata": {
            "givens": givens,
            "target": "f(x)" if expression_answer else f"f({query_x})",
            "derivation": [f"f(x)={expression}", f"f({query_x})={evaluated}"],
            "problem_type_id": pt,
            "template_slot": "linear_function_contextual_word_problem",
            "scenario": scenario,
        },
        "source": "gencode_slot_generator",
    }


def _fmt_signed_int(value: int) -> str:
    return f"+{value}" if value > 0 else str(value)


# ── Raw formula helpers (no $...$ — for metadata/derivation/internal use) ────

def _quadratic_vertex_form(a: int, h: int, k: int) -> str:
    """Raw vertex-form string without $...$ (metadata / checker use)."""
    x_term = "(x)" if h == 0 else f"(x-{h})" if h > 0 else f"(x+{abs(h)})"
    tail = "" if k == 0 else _fmt_signed_int(k)
    if a == 1:
        return f"y={x_term}^2{tail}"
    if a == -1:
        return f"y=-{x_term}^2{tail}"
    return f"y={a}{x_term}^2{tail}"


def _quadratic_standard_form_from_vertex(a: int, h: int, k: int) -> str:
    """Raw standard-form string without $...$ (metadata / checker use)."""
    b = -2 * a * h
    c = a * h * h + k
    parts = [f"y={a}x^2"]
    if b:
        parts.append(_fmt_signed_int(b) + "x")
    if c:
        parts.append(_fmt_signed_int(c))
    return "".join(parts)


# ── Display formula helpers ($...$ wrapped — for student-facing fields) ───────

def _display_math(raw: str) -> str:
    """Wrap a raw formula string in $...$ for student-facing display."""
    return f"${raw}$"


def _quadratic_vertex_form_display(a: int, h: int, k: int) -> str:
    """Display vertex-form with $...$ (question_text / choices / explanation)."""
    return _display_math(_quadratic_vertex_form(a, h, k))


def _quadratic_standard_form_display(a: int, h: int, k: int) -> str:
    """Display standard-form with $...$ (question_text / choices / explanation)."""
    return _display_math(_quadratic_standard_form_from_vertex(a, h, k))


# ── Chinese-language phrase helpers ──────────────────────────────────────────

def _shift_phrase_zh(h: int, k: int) -> str:
    """Chinese description of 2-D translation e.g. '向左 2、向上 3'."""
    if h == 0 and k == 0:
        return "不移動"
    parts: list[str] = []
    if h != 0:
        parts.append(f"向右 {h}" if h > 0 else f"向左 {abs(h)}")
    if k != 0:
        parts.append(f"向上 {k}" if k > 0 else f"向下 {abs(k)}")
    return "、".join(parts)


def _vertical_shift_phrase_zh(k: int) -> str:
    """Chinese description of vertical-only translation e.g. '向上 5'."""
    return f"向上 {k}" if k > 0 else f"向下 {abs(k)}"


def _extreme_phrase_zh(a: int, k: int) -> str:
    """Chinese extreme-value description e.g. '最大值為 k' or '最小值為 k'."""
    return f"最大值為 {k}" if a < 0 else f"最小值為 {k}"


def _vertex_axis_option_zh(
    vertex: tuple[int, int], axis_x: int, extreme_zh: str
) -> str:
    """Chinese choice-option text: '頂點 (h,k)，對稱軸 $x=axis_x$，最小值為 k'."""
    return f"頂點 ({vertex[0]},{vertex[1]})，對稱軸 $x={axis_x}$，{extreme_zh}"


def _make_quadratic_choice_options_zh(
    h: int, k: int, a: int
) -> tuple[str, list[str]]:
    """
    Build correct option + 3 unique wrong options in Chinese.
    Uses a cascade of 8 deterministic candidate distractors to guarantee
    no duplicates even when h=0 or k=0.
    """
    correct_ext = _extreme_phrase_zh(a, k)
    correct = _vertex_axis_option_zh((h, k), h, correct_ext)
    seen: set[str] = {correct}

    def opt(vh: int, vk: int, ax: int, ea: int, ek: int) -> str:
        return _vertex_axis_option_zh((vh, vk), ax, _extreme_phrase_zh(ea, ek))

    candidates = [
        opt(-h,    k,    -h,    a,      k),       # flip vertex/axis sign
        opt(h,    -k,     h,    a,     -k),       # flip k sign
        opt(h + 1, k,   h + 1, -a,     k),       # offset h, flip a-sign
        opt(h,    k + 1,  h,    a,    k + 1),    # offset k up
        opt(h - 1, k,   h - 1,  a,     k),       # offset h the other way
        opt(h,    k - 1,  h,    a,    k - 1),    # offset k down
        opt(h + 2, k,   h + 2,  a,     k),       # larger h offset
        opt(h,    k + 2,  h,    a,    k + 2),    # larger k offset
    ]

    wrongs: list[str] = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            wrongs.append(c)
        if len(wrongs) == 3:
            break

    return correct, wrongs


# ── Legacy English helpers (kept for backward compatibility, not used in slots) ─

def _shift_phrase(h: int, k: int) -> str:
    horizontal = "none" if h == 0 else f"right {h}" if h > 0 else f"left {abs(h)}"
    vertical = "none" if k == 0 else f"up {k}" if k > 0 else f"down {abs(k)}"
    return f"{horizontal}, {vertical}"


def _extreme_phrase(a: int, k: int) -> str:
    return f"maximum {k}" if a < 0 else f"minimum {k}"


def _vertex_axis_option(vertex: tuple[int, int], axis_x: int, extreme: str) -> str:
    return f"vertex ({vertex[0]},{vertex[1]}), axis x={axis_x}, {extreme}"


def _slot_quadratic_graph_vertex_axis_choice(
    skill_id: str, pt: str, spec: dict[str, Any], seed: int | None
) -> dict[str, Any]:
    rng = random.Random(f"{seed}|quadratic_vertex_axis|{pt}")
    a = rng.choice([-3, -2, -1, 1, 2, 3])
    h = rng.randint(-4, 4)
    k = rng.randint(-4, 5)
    correct, wrongs = _make_quadratic_choice_options_zh(h, k, a)
    stem = (
        f"已知拋物線 {_quadratic_vertex_form_display(a, h, k)}，"
        "請選出其頂點、對稱軸與最大值或最小值的正確敘述。"
    )
    return _build_choice_payload(
        skill_id,
        pt,
        stem,
        correct,
        wrongs,
        answer_type="single_choice",
        checker_type="choice_label_checker",
        metadata={
            "givens": [f"equation={_quadratic_vertex_form(a, h, k)}"],
            "target": "vertex-axis-extreme",
            "derivation": [f"vertex=({h},{k})", f"axis=x={h}", _extreme_phrase_zh(a, k)],
            "template_slot": "quadratic_graph_vertex_axis_choice",
            "problem_type_id": pt,
        },
        diagnosis_tags=["quadratic_vertex", "quadratic_axis", "quadratic_extreme"],
        explanation=(
            f"拋物線 {_quadratic_vertex_form_display(a, h, k)} 的頂點為 $({h},{k})$，"
            f"對稱軸為 $x={h}$，{_extreme_phrase_zh(a, k)}。"
        ),
        seed=seed,
    )


def _slot_quadratic_graph_translation_fill_blank(
    skill_id: str, pt: str, spec: dict[str, Any], seed: int | None
) -> dict[str, Any]:
    rng = random.Random(f"{seed}|quadratic_translation_blank|{pt}")
    a = rng.choice([-3, -2, -1, 1, 2, 3])
    h = rng.choice([-3, -2, -1, 1, 2, 3])
    k = rng.choice([-4, -3, -2, -1, 1, 2, 3, 4])
    answer = _shift_phrase_zh(h, k)
    base_display = _display_math(f"y={a}x^2")
    shifted_display = _quadratic_vertex_form_display(a, h, k)
    stem = (
        f"相較於 {base_display}，拋物線 {shifted_display} 如何平移？"
        "請用「向左 2、向上 3」的格式作答。"
    )
    h_desc = f"向右 {h}" if h > 0 else f"向左 {abs(h)}"
    k_desc = f"向上 {k}" if k > 0 else f"向下 {abs(k)}"
    explanation = (
        f"水平方向平移：{h_desc}（頂點式中 $x$ 的位移）；"
        f"鉛直方向平移：{k_desc}（常數項的移動）。"
        f"答案為「{answer}」。"
    )
    return {
        "skill_id": skill_id,
        "problem_type_id": pt,
        "question_text": stem,
        "question": stem,
        "choices": [],
        "answer": answer,
        "correct_answer": answer,
        "answer_type": "text_short",
        "checker_type": "text_short_checker",
        "checker": "text_short_checker",
        "answer_contract": dict(get_answer_contract(spec)),
        "explanation": explanation,
        "diagnosis_tags": ["quadratic_translation", "vertex_form_shift"],
        "metadata": {
            "givens": [f"base=y={a}x^2", f"shifted={_quadratic_vertex_form(a, h, k)}"],
            "target": "translation",
            "derivation": [f"h={h}", f"k={k}", answer],
            "template_slot": "quadratic_graph_translation_fill_blank",
            "problem_type_id": pt,
        },
        "source": "gencode_slot_generator",
    }


def _slot_quadratic_graph_translation_short_answer(
    skill_id: str, pt: str, spec: dict[str, Any], seed: int | None
) -> dict[str, Any]:
    rng = random.Random(f"{seed}|quadratic_translation_short|{pt}")
    a = rng.choice([-3, -2, -1, 1, 2, 3])
    k = rng.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])
    answer = _vertical_shift_phrase_zh(k)
    base_raw = f"y={a}x^2"
    shifted_raw = f"y={a}x^2{_fmt_signed_int(k)}"
    base_display = _display_math(base_raw)
    shifted_display = _display_math(shifted_raw)
    stem = f"相較於 {base_display}，拋物線 {shifted_display} 在鉛直方向如何平移？"
    if k > 0:
        explanation = (
            f"函數 {shifted_display} 是在 {base_display} 外部加上 ${k}$，"
            f"圖形向上平移 ${k}$ 單位，答案為「{answer}」。"
        )
    else:
        explanation = (
            f"函數 {shifted_display} 是在 {base_display} 外部減去 ${abs(k)}$，"
            f"圖形向下平移 ${abs(k)}$ 單位，答案為「{answer}」。"
        )
    return {
        "skill_id": skill_id,
        "problem_type_id": pt,
        "question_text": stem,
        "question": stem,
        "choices": [],
        "answer": answer,
        "correct_answer": answer,
        "answer_type": "text_short",
        "checker_type": "text_short_checker",
        "checker": "text_short_checker",
        "answer_contract": dict(get_answer_contract(spec)),
        "explanation": explanation,
        "diagnosis_tags": ["quadratic_translation", "vertical_shift"],
        "metadata": {
            "givens": [f"base={base_raw}", f"shifted={shifted_raw}"],
            "target": "vertical-shift",
            "derivation": [f"k={k}", answer],
            "template_slot": "quadratic_graph_translation_short_answer",
            "problem_type_id": pt,
        },
        "source": "gencode_slot_generator",
    }


def _slot_quadratic_vertex_form_properties(
    skill_id: str, pt: str, spec: dict[str, Any], seed: int | None
) -> dict[str, Any]:
    rng = random.Random(f"{seed}|quadratic_vertex_form_properties|{pt}")
    a = rng.choice([-3, -2, -1, 1, 2, 3])
    h = rng.randint(-5, 5)
    k = rng.randint(-5, 5)
    correct, wrongs = _make_quadratic_choice_options_zh(h, k, a)
    stem = (
        f"已知二次函數 {_quadratic_vertex_form_display(a, h, k)}，"
        "請選出其圖形性質的正確敘述。"
    )
    return _build_choice_payload(
        skill_id,
        pt,
        stem,
        correct,
        wrongs,
        answer_type="single_choice",
        checker_type="choice_label_checker",
        metadata={
            "givens": [f"equation={_quadratic_vertex_form(a, h, k)}"],
            "target": "graph-properties",
            "derivation": [f"vertex=({h},{k})", f"axis=x={h}", _extreme_phrase_zh(a, k)],
            "template_slot": "quadratic_vertex_form_properties",
            "problem_type_id": pt,
        },
        diagnosis_tags=["quadratic_vertex_form", "quadratic_properties"],
        explanation=(
            f"對於 {_quadratic_vertex_form_display(a, h, k)}，"
            f"頂點為 $({h},{k})$，對稱軸為 $x={h}$，{_extreme_phrase_zh(a, k)}。"
        ),
        seed=seed,
    )


def _slot_quadratic_standard_to_vertex_properties(
    skill_id: str, pt: str, spec: dict[str, Any], seed: int | None
) -> dict[str, Any]:
    rng = random.Random(f"{seed}|quadratic_standard_to_vertex|{pt}")
    a = rng.choice([-2, -1, 1, 2])
    h = rng.randint(-4, 4)
    k = rng.randint(-4, 4)
    standard_raw = _quadratic_standard_form_from_vertex(a, h, k)
    vertex_raw = _quadratic_vertex_form(a, h, k)
    standard_display = _quadratic_standard_form_display(a, h, k)
    vertex_display = _quadratic_vertex_form_display(a, h, k)

    def ch_opt(vf_disp: str, vh: int, vk: int, ax: int) -> str:
        return f"{vf_disp}；頂點 $({vh},{vk})$；對稱軸 $x={ax}$"

    correct = ch_opt(vertex_display, h, k, h)

    # Cascade of 6 distinct distractor candidates — handles h=0 / k=0 edge cases
    cands = [
        ch_opt(vertex_display, -h, k, -h),
        ch_opt(standard_display, h, k, h),
        ch_opt(_quadratic_vertex_form_display(a, h, k + 1), h, k + 1, h),
        ch_opt(vertex_display, h, k - 1, h),
        ch_opt(_quadratic_vertex_form_display(a, h + 1, k), h + 1, k, h + 1),
        ch_opt(vertex_display, h, k + 2, h),
    ]
    seen: set[str] = {correct}
    wrongs: list[str] = []
    for c in cands:
        if c not in seen:
            seen.add(c)
            wrongs.append(c)
        if len(wrongs) == 3:
            break

    stem = f"將 {standard_display} 化為頂點式，並選出正確的頂點與對稱軸。"
    explanation = (
        f"{standard_display} 可化為 {vertex_display}，"
        f"頂點為 $({h},{k})$，對稱軸為 $x={h}$。"
    )
    return _build_choice_payload(
        skill_id,
        pt,
        stem,
        correct,
        wrongs,
        answer_type="single_choice",
        checker_type="choice_label_checker",
        metadata={
            "givens": [f"standard_form={standard_raw}"],
            "target": "vertex-form-conversion",
            "derivation": [vertex_raw, f"vertex=({h},{k})", f"axis=x={h}"],
            "template_slot": "quadratic_standard_to_vertex_properties",
            "problem_type_id": pt,
        },
        diagnosis_tags=["quadratic_complete_square", "quadratic_vertex_form"],
        explanation=explanation,
        seed=seed,
    )


def _slot_function_value_numeric(skill_id: str, pt: str, spec: dict[str, Any], seed: int | None) -> dict[str, Any]:
    ac = get_answer_contract(spec)
    if _function_value_choice_requested(spec, ac):
        return _slot_linear_function_two_point_choice(skill_id, pt, spec, seed)
    if _function_value_application_requested(spec, ac):
        return _slot_linear_function_contextual_word_problem(skill_id, pt, spec, seed)

    rng = random.Random(seed)
    a = rng.choice([i for i in range(-5, 6) if i not in {0}])
    b = rng.randint(-8, 8)
    c = rng.randint(-6, 6)
    fn_name = rng.choice(["f", "g", "h"])
    use_note = rng.random() < 0.35

    value = a * c + b
    sign_b = "+" if b >= 0 else "-"
    abs_b = abs(b)
    if abs_b == 0:
        fx_latex = f"${fn_name}(x)={a}x$"
        substitute = f"{a}\\times {c}"
    else:
        fx_latex = f"${fn_name}(x)={a}x{sign_b}{abs_b}$"
        substitute = f"{a}\\times {c}{sign_b}{abs_b}"

    if use_note:
        stem = f"已知 {fx_latex}，則 ${fn_name}({c})$ 的值為何？"
    else:
        stem = f"若 {fx_latex}，求 ${fn_name}({c})$。"

    explanation = f"${fn_name}({c})={substitute}={value}$"
    return {
        "skill_id": skill_id,
        "problem_type_id": pt,
        "question_text": stem,
        "question": stem,
        "choices": [],
        "answer": str(value),
        "correct_answer": str(value),
        "answer_type": "numeric",
        "checker_type": "numeric_checker",
        "explanation": explanation,
        "diagnosis_tags": ["function_value_substitution", "linear_function_evaluation"],
        "metadata": {
            "givens": [f"{fn_name}(x)={a}x{sign_b}{abs_b}", f"x={c}"],
            "target": f"{fn_name}({c})",
            "derivation": [f"{fn_name}({c})={substitute}", f"{fn_name}({c})={value}"],
            "problem_type_id": pt,
            "template_slot": "function_value_numeric",
        },
        "source": "gencode_slot_generator",
    }


SLOT_REGISTRY: dict[str, GeneratorFn] = {
    "point_quadrant": _slot_point_quadrant,
    "point_quadrant_choice": _slot_point_quadrant_choice,
    "symbolic_quadrant": _slot_symbolic_quadrant,
    "symbolic_quadrant_choice": _slot_symbolic_quadrant_choice,
    "axis_distance_choice": _slot_axis_distance_choice,
    "symbolic_quadrant_statement_choice": _slot_symbolic_quadrant_statement_choice,
    "two_point_distance_solution_set": _slot_two_point_distance_solution_set,
    "two_point_distance_compute": _slot_two_point_distance_compute,
    "linear_triangle_median_compute": _slot_linear_triangle_median_compute,
    "function_value_numeric": _slot_function_value_numeric,
    "linear_function_two_point_choice": _slot_linear_function_two_point_choice,
    "linear_function_contextual_word_problem": _slot_linear_function_contextual_word_problem,
    "quadratic_graph_vertex_axis_choice": _slot_quadratic_graph_vertex_axis_choice,
    "quadratic_graph_translation_fill_blank": _slot_quadratic_graph_translation_fill_blank,
    "quadratic_graph_translation_short_answer": _slot_quadratic_graph_translation_short_answer,
    "quadratic_vertex_form_properties": _slot_quadratic_vertex_form_properties,
    "quadratic_standard_to_vertex_properties": _slot_quadratic_standard_to_vertex_properties,
    DIVISION_POINT_SLOT: _slot_division_point_coordinates,
}

TARGET_TASK_GENERATOR_REGISTRY: dict[str, GeneratorFn] = {
    "compute_internal_division_point_coordinates": _slot_division_point_coordinates,
    "compute_centroid_coordinates": _slot_division_point_coordinates,
    "compute_midpoint_coordinates": _slot_division_point_coordinates,
    "solve_point_from_section_ratio": _slot_division_point_coordinates,
}


def _semantic_required_concepts(problem_type_spec: dict[str, Any]) -> list[str]:
    raw = get_semantic_contract(problem_type_spec).get("required_concepts", [])
    values = [raw] if isinstance(raw, str) else raw if isinstance(raw, list) else []
    concepts: list[str] = []
    for value in values:
        if isinstance(value, dict):
            value = value.get("token") or value.get("concept") or value.get("name") or ""
        concept = str(value or "").strip()
        if concept and concept not in concepts:
            concepts.append(concept)
    return concepts


def _reinforce_slot_question_text(
    payload: dict[str, Any],
    problem_type_spec: dict[str, Any],
) -> dict[str, Any]:
    question_text = str(payload.get("question_text") or payload.get("question") or "").strip()
    concepts = _semantic_required_concepts(problem_type_spec)
    missing = [concept for concept in concepts if concept not in question_text]
    additions: list[str] = []
    if missing:
        additions.append(f"解題時請運用{'、'.join(missing)}。")
    if len(" ".join([question_text, *additions]).strip()) <= 30:
        focus = "、".join(concepts) or "題目中的數學條件"
        additions.append(f"請根據已知條件，運用{focus}完成計算，並寫出完整答案。")
    if additions:
        question_text = " ".join([question_text, *additions]).strip()
    payload["question_text"] = question_text
    payload["question"] = question_text
    metadata = dict(payload.get("metadata") or {})
    metadata["semantic_required_concepts"] = concepts
    payload["metadata"] = metadata
    return payload


def generate_from_problem_type_spec(
    skill_id: str,
    problem_type_spec: dict[str, Any],
    *,
    seed: int | None = None,
) -> dict[str, Any]:
    pt = str(problem_type_spec.get("problem_type_id", "")).strip()
    target_task = str(problem_type_spec.get("target_task", "")).strip()
    inferred_target_task = infer_registered_task_token(problem_type_spec)
    if target_task not in TARGET_TASK_GENERATOR_REGISTRY and inferred_target_task in TARGET_TASK_GENERATOR_REGISTRY:
        problem_type_spec = dict(problem_type_spec)
        problem_type_spec["target_task"] = inferred_target_task
        target_task = inferred_target_task
    slot = resolve_template_slot(problem_type_spec, seed)
    fn = TARGET_TASK_GENERATOR_REGISTRY.get(target_task) or SLOT_REGISTRY.get(slot)
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
    ac = get_answer_contract(problem_type_spec)
    payload = apply_coordinate_pair_runtime_fields(payload, ac)
    payload = _reinforce_slot_question_text(payload, problem_type_spec)
    errors = validate_generator_payload(payload, skill_id=skill_id, problem_type_spec=problem_type_spec)
    if errors:
        raise RuntimeError(f"generator_semantically_unsafe:{','.join(errors)}")
    return payload
