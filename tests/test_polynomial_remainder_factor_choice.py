# -*- coding: utf-8 -*-
"""Generic remainder / factor choice modes reuse existing operations."""

from __future__ import annotations

import re
from fractions import Fraction

from core.domain.polynomial_domain import (
    _eval,
    _frac_plain,
    _verify_and_factor_distractors,
    build_polynomial_matrix,
)
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload
from core.gencode.runtime_skill_wrapper import check_answer

_TECH_SUFFIX = re.compile(r"_(?:[123]|duplicate|copy)\b")


def _choice_texts(payload: dict) -> list[str]:
    out: list[str] = []
    for item in payload.get("choices") or []:
        if isinstance(item, dict):
            out.append(str(item.get("text") or "").strip())
        else:
            out.append(str(item).strip())
    return out


def _collect_verify_and_factor_seeds(limit: int = 100, search_upto: int = 800) -> list[int]:
    found: list[int] = []
    for seed in range(search_upto):
        matrix = build_polynomial_matrix(
            seed=seed,
            domain_operation="factor_theorem_root_factor",
            constraints={},
        )
        question = str(matrix.get("question_text") or "")
        if "驗證" in question and "因式分解" in question:
            found.append(seed)
            if len(found) >= limit:
                break
    return found


def test_remainder_eval_choice_has_unique_distractors():
    matrix = build_polynomial_matrix(
        seed=11,
        domain_operation="remainder_theorem_evaluate",
        constraints={
            "presentation_mode": "single_choice",
            "source_problem_text": "則 f(7)= (A) 9 (B) 8 (C) 7 (D) 6",
        },
    )
    ans = str(matrix["answer"]["value"])
    distractors = list(matrix.get("distractors") or [])
    assert len(distractors) == 3
    assert ans not in {str(x) for x in distractors}
    assert "餘式" in str(matrix.get("question_text") or "") or "f(" in str(matrix.get("question_text") or "")


def test_remainder_product_mode_from_source_text():
    matrix = build_polynomial_matrix(
        seed=3,
        domain_operation="remainder_theorem_evaluate",
        constraints={
            "presentation_mode": "single_choice",
            "source_problem_text": r"設兩多項式$f(x)$和$g(x)$除以x+5所得餘式分別為2和-2，則$f(x)\times g(x)$除以x+5的餘式為",
        },
    )
    givens = matrix.get("givens") or {}
    assert int(givens["r1"]) * int(givens["r2"]) == int(str(matrix["answer"]["value"]))


def test_factor_quadratic_remainder_eval_from_source_text():
    src = (
        r"已知多項式$f(x)$除以$(x+2)(x-7)$的餘式為$ax+3$。"
        r"若$(x-7)$為$f(x)$的因式，則$f(-2)=$？"
    )
    matrix = build_polynomial_matrix(
        seed=5,
        domain_operation="factor_theorem_root_factor",
        constraints={"presentation_mode": "single_choice", "source_problem_text": src},
    )
    givens = matrix.get("givens") or {}
    p = int(givens["p"])
    q = int(givens["q"])
    b = int(givens["b"])
    a = Fraction(str(givens["a"]))
    assert a * q + b == 0
    assert str(matrix["answer"]["value"]) == _frac_plain(a * p + b)
    assert len(matrix.get("distractors") or []) == 3


def test_factor_linear_param_choice_from_source_text():
    matrix = build_polynomial_matrix(
        seed=8,
        domain_operation="factor_theorem_root_factor",
        constraints={
            "presentation_mode": "single_choice",
            "source_problem_text": r"設x-1為$f(x)=2x^3-kx^2+7x-5$之因式，則k=",
        },
    )
    assert str(matrix["answer"]["value"])
    assert len(matrix.get("distractors") or []) == 3


def test_verify_and_factor_distractors_are_mathematical():
    distractors = _verify_and_factor_distractors(2, 3, -2)
    correct = "f(3)=0；2(x-3)(x+2)"
    assert len(distractors) == 3
    assert correct not in distractors
    assert len(set(distractors)) == 3
    assert "2(x-3)(x+2)_1" not in distractors
    assert any("2(x+3)" in item or "2(x-3)(x-2)" in item or "2(x-3)(x+2)" not in item for item in distractors)


def test_verify_and_factor_choice_payload_has_unique_semantic_choices():
    seeds = _collect_verify_and_factor_seeds(limit=8)
    assert seeds
    for seed in seeds:
        matrix = build_polynomial_matrix(
            seed=seed,
            domain_operation="factor_theorem_root_factor",
            constraints={},
        )
        payload = convert_domain_matrix_to_question_payload(
            matrix,
            presentation_mode="single_choice",
            answer_type="single_choice",
            problem_type_id="factor_theorem_root_factor",
            domain_operation="factor_theorem_root_factor",
            seed=seed,
        )
        texts = _choice_texts(payload)
        assert len(texts) == 4
        assert len(set(texts)) == 4
        assert not any(_TECH_SUFFIX.search(text) for text in texts)
        correct_label = str(payload.get("answer") or "").strip().upper()
        assert check_answer(correct_label, correct_label, payload=payload)
        for item in payload.get("choices") or []:
            label = str(item.get("label") or "").strip().upper()
            if label == correct_label:
                continue
            assert not check_answer(label, correct_label, payload=payload)


def test_verify_and_factor_100_seeds_choice_invariants():
    seeds = _collect_verify_and_factor_seeds(limit=100)
    assert len(seeds) == 100
    seen_replay: dict[int, str] = {}
    for seed in seeds:
        matrix = build_polynomial_matrix(
            seed=seed,
            domain_operation="factor_theorem_root_factor",
            constraints={},
        )
        givens = matrix.get("givens") or {}
        root = int(givens["root"])
        other = int(givens["other_root"])
        lead = int(givens["lead"])
        f = {int(k): Fraction(str(v)) for k, v in (givens.get("f") or {}).items()}
        assert _eval(f, root) == 0
        assert _eval(f, other) == 0
        assert int(f.get(2, 0)) == lead
        distractors = list(matrix.get("distractors") or [])
        canonical = str(matrix["answer"]["canonical_form"])
        assert len(distractors) == 3
        assert canonical not in distractors
        assert len({canonical, *distractors}) == 4
        payload = convert_domain_matrix_to_question_payload(
            matrix,
            presentation_mode="single_choice",
            answer_type="single_choice",
            problem_type_id="factor_theorem_root_factor",
            domain_operation="factor_theorem_root_factor",
            seed=seed,
        )
        texts = _choice_texts(payload)
        assert len(texts) == 4
        assert len(set(texts)) == 4
        assert not any(_TECH_SUFFIX.search(text) for text in texts)
        replay = convert_domain_matrix_to_question_payload(
            build_polynomial_matrix(
                seed=seed,
                domain_operation="factor_theorem_root_factor",
                constraints={},
            ),
            presentation_mode="single_choice",
            answer_type="single_choice",
            problem_type_id="factor_theorem_root_factor",
            domain_operation="factor_theorem_root_factor",
            seed=seed,
        )
        assert _choice_texts(replay) == texts
        seen_replay[seed] = "|".join(texts)
    assert len(seen_replay) == 100


def _is_root_to_factor(question: str) -> bool:
    return "一次因式" in question and "已知" in question and "一根" in question


def _convert_factor_short(matrix: dict, seed: int) -> dict:
    return convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="short_answer",
        answer_type="expression",
        problem_type_id="factor_theorem_root_factor",
        domain_operation="factor_theorem_root_factor",
        seed=seed,
    )


def test_root_to_factor_is_single_expression_not_fake_multipart():
    matrix = build_polynomial_matrix(
        seed=677,
        domain_operation="factor_theorem_root_factor",
        constraints={},
    )
    question = str(matrix.get("question_text") or "")
    assert _is_root_to_factor(question)
    compact = question.replace(" ", "")
    assert "x^{2}-9" in compact or "x^2-9" in compact
    value = matrix["answer"]["value"]
    assert value == "x-3"
    assert not isinstance(value, dict)
    payload = _convert_factor_short(matrix, 677)
    assert payload["answer_type"] != "multi_part" or not isinstance(payload.get("answer"), dict)
    assert str(payload.get("answer")) == "x-3"
    assert payload.get("checker") in {None, "expression_checker"} or str(
        (payload.get("answer_contract") or {}).get("checker")
    ) in {"expression_checker", "multi_part_answer_checker"}
    assert check_answer("x-3", payload.get("answer"), payload=payload)
    assert check_answer("(x-3)", payload.get("answer"), payload=payload)
    assert not check_answer("x+3", payload.get("answer"), payload=payload)


def test_root_to_factor_100_seeds_expression_contract():
    found: list[int] = []
    for seed in range(0, 2000):
        matrix = build_polynomial_matrix(
            seed=seed,
            domain_operation="factor_theorem_root_factor",
            constraints={},
        )
        question = str(matrix.get("question_text") or "")
        if not _is_root_to_factor(question):
            continue
        found.append(seed)
        payload = _convert_factor_short(matrix, seed)
        answer = payload.get("answer")
        assert not isinstance(answer, dict), seed
        factor = str(answer)
        assert factor
        ac = payload.get("answer_contract") or {}
        parts = ac.get("parts") if isinstance(ac.get("parts"), list) else []
        keys = [str(row.get("key") or "") for row in parts if isinstance(row, dict)]
        assert len(keys) == len(set(keys))
        assert check_answer(factor, answer, payload=payload)
        replay = _convert_factor_short(
            build_polynomial_matrix(
                seed=seed,
                domain_operation="factor_theorem_root_factor",
                constraints={},
            ),
            seed,
        )
        assert replay.get("answer") == answer
        if len(found) >= 100:
            break
    assert len(found) == 100
