# -*- coding: utf-8 -*-
"""Domain helpers for vh_數學B1_FunctionConcept."""
from __future__ import annotations

import random
from typing import Any


def _choice_payload(
    *,
    skill_id: str,
    problem_type_id: str,
    stem: str,
    correct: str,
    wrongs: list[str],
    seed: int | None,
    explanation: str,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    rng = random.Random(seed)
    pool = [{"is_correct": True, "text": correct}] + [{"is_correct": False, "text": w} for w in wrongs[:3]]
    rng.shuffle(pool)
    choices = []
    ans = "A"
    for i, opt in enumerate(pool):
        label = chr(ord("A") + i)
        choices.append({"label": label, "text": str(opt["text"])})
        if opt["is_correct"]:
            ans = label
    return {
        "skill_id": skill_id,
        "problem_type_id": problem_type_id,
        "question_text": stem,
        "question": stem,
        "choices": choices,
        "options": [c["text"] for c in choices],
        "answer": ans,
        "correct_answer": ans,
        "answer_type": "single_choice",
        "checker_key": "choice_label_checker",
        "answer_contract": {
            "answer_type": "single_choice",
            "answer_shape": "choice_label",
            "equivalence_type": "choice_label",
            "checker_key": "choice_label_checker",
            "checker": "choice_label_checker",
            "presentation_mode": "single_choice",
            "choices_required": True,
            "choice_count": 4,
            "correct_choice_count": 1,
            "frontend_render_choices": True,
        },
        "explanation": explanation,
        "metadata": metadata,
        "presentation_mode": "single_choice",
        "source": "function_concept_domain",
    }


def build_function_concept_matrix(
    *,
    seed: int | None = None,
    curriculum_profile: str = "vocational_high_b",
    difficulty_profile: str = "easy",
    constraints: dict[str, Any] | None = None,
    domain_operation: str | None = None,
    line_type: str | None = None,
) -> dict[str, Any]:
    """Return a Domain-Matrix-like payload already usable as question payload."""
    op = str(domain_operation or line_type or "").strip()
    extra = constraints or {}
    skill_id = str(extra.get("skill_id") or "vh_數學B1_FunctionConcept")
    rng = random.Random(0 if seed is None else seed)

    if op in {"free_fall_function_value_choice", "function_concept_free_fall_evaluation"}:
        # S(t) = (1/2)*g*t^2 with g=9.8 approximated as 98/10 → use g=10 for classroom ints
        g = 10
        t = rng.choice([2, 3, 4, 5, 6])
        value = (g * t * t) // 2
        stem = (
            f"自由落體公式 $S(t)=\\dfrac{{1}}{{2}}gt^{{2}}$，取 $g={g}$（公尺/秒$^2$）。"
            f"當 $t={t}$ 秒時，落下距離 $S({t})$ 為多少公尺？"
        )
        correct = str(value)
        distractors = []
        for d in (t, g, 2 * t, t * t, value + 5, value + 10, max(1, value - 5)):
            cand = str(d)
            if cand != correct and cand not in distractors:
                distractors.append(cand)
            if len(distractors) >= 3:
                break
        while len(distractors) < 3:
            cand = str(value + 11 + len(distractors))
            if cand != correct and cand not in distractors:
                distractors.append(cand)
        wrongs = distractors[:3]
        payload = _choice_payload(
            skill_id=skill_id,
            problem_type_id=op,
            stem=stem,
            correct=correct,
            wrongs=wrongs[:3],
            seed=seed,
            explanation=f"$S({t})=\\frac{{1}}{{2}}\\cdot{g}\\cdot{t}^{{2}}={value}$。",
            metadata={
                "givens": [f"g={g}", f"t={t}"],
                "target": correct,
                "derivation": [f"S=0.5*g*t^2", f"S={value}"],
                "template_slot": "free_fall_function_value_choice",
            },
        )
        return {"answer": {"canonical_form": payload["correct_answer"]}, "payload": payload, **payload}

    if op in {"piecewise_utility_bill_savings_choice", "function_concept_piecewise_evaluation"}:
        # Simplified piecewise: f(x)=3x if x<=100 else 5x-200
        x1 = rng.choice([120, 140, 160, 180])
        x2 = rng.choice([60, 70, 80, 90])
        f1 = 5 * x1 - 200
        f2 = 3 * x2
        savings = f1 - f2
        stem = (
            "電費函數 "
            "$f(x)=\\begin{cases}3x,&x\\le 100\\\\5x-200,&x>100\\end{cases}$（單位：元）。"
            f"若本月用電 ${x1}$ 度、次月用電 ${x2}$ 度，則次月比本月省下多少元？"
        )
        correct = str(savings)
        distractors = []
        for d in (x1 - x2, 50, 100, f1, f2, abs(savings - 30), savings + 40):
            cand = str(abs(int(d)))
            if cand != correct and cand not in distractors:
                distractors.append(cand)
            if len(distractors) >= 3:
                break
        while len(distractors) < 3:
            cand = str(int(correct) + 17 + len(distractors))
            if cand != correct and cand not in distractors:
                distractors.append(cand)
        wrongs = distractors[:3]
        payload = _choice_payload(
            skill_id=skill_id,
            problem_type_id=op,
            stem=stem,
            correct=correct,
            wrongs=wrongs[:3],
            seed=seed,
            explanation=(
                f"$f({x1})=5\\cdot{x1}-200={f1}$，"
                f"$f({x2})=3\\cdot{x2}={f2}$，差額={savings}。"
            ),
            metadata={
                "givens": [f"x1={x1}", f"x2={x2}"],
                "target": correct,
                "derivation": [f"f(x1)={f1}", f"f(x2)={f2}", f"savings={savings}"],
                "template_slot": "piecewise_utility_bill_savings_choice",
            },
        )
        return {"answer": {"canonical_form": payload["correct_answer"]}, "payload": payload, **payload}

    raise RuntimeError(f"unsupported_function_concept_operation:{op}")


def generate_function_concept_payload(
    *,
    skill_id: str,
    problem_type_id: str,
    seed: int | None = None,
    component_id: str | None = None,
    textbook_example_id: int | None = None,
) -> dict[str, Any]:
    matrix = build_function_concept_matrix(
        seed=seed,
        domain_operation=problem_type_id,
        constraints={"skill_id": skill_id},
    )
    payload = dict(matrix.get("payload") or matrix)
    if component_id:
        payload["component_id"] = component_id
    if textbook_example_id is not None:
        payload["textbook_example_id"] = textbook_example_id
    payload["seed"] = seed
    return payload
