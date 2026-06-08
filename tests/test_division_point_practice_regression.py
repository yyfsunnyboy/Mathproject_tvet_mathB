# -*- coding: utf-8 -*-
"""Practice-facing regression: overline stems and coordinate_pair grading feedback."""

from __future__ import annotations

import re
from fractions import Fraction

import pytest

from app import create_app
from core.checkers.coordinate_pair_checker import check_coordinate_pair_answer
from core.gencode.answer_grading import format_correct_answer_display, grade_answer_for_current_question
from core.gencode.answer_payload import (
    coerce_correct_answer,
    format_coordinate_pair_display,
)
from core.gencode.division_point_slot_engine import (
    _gen_internal_stem,
    _internal_point,
    _ratio_relation_latex,
)
from core.gencode.generator_contract_schema import enrich_spec_generator_contract
from core.gencode.runtime_skill_wrapper import check_answer
from core.gencode.slot_generators import generate_from_problem_type_spec
from core.routes.practice import _normalize_gencode_runtime_payload


def _coord_spec() -> dict:
    return enrich_spec_generator_contract(
        {
            "problem_type_id": "ordered_pair_internal_division",
            "skill_id": "mock_skill",
            "target_task": "compute_internal_division_point_coordinates",
            "task_family": "division_point_coordinates_family",
            "answer_contract": {
                "answer_type": "ordered_pair",
                "answer_shape": "coordinate_pair",
                "answer_equivalence": "coordinate_pair_equivalence",
                "checker": "coordinate_pair_checker",
                "presentation_mode": "short_answer",
            },
            "generator_contract": {},
        }
    )


@pytest.fixture()
def client():
    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()


def test_internal_division_mn_5_1_unique_coordinate():
    px, py = _internal_point(0, -7, 12, -7, 5, 1)
    assert px == Fraction(10, 1)
    assert py == Fraction(-7, 1)
    q, _ = _gen_internal_stem("ratio_colon_form", ["M", "N", "T"], 0, -7, 12, -7, px, py, 5, 1)
    assert r"\overline{MN}" in q
    assert r"\overline{MT}" in q
    assert r"\overline{TN}" in q
    assert "$\\overline{MT}:\\overline{TN}=5:1$" in q
    assert not re.search(r"且\s+[0-9]*[A-Z]{2}[:=]", q)


def test_coerce_does_not_split_coordinate_pair_for_display():
    ac = _coord_spec()["answer_contract"]
    assert coerce_correct_answer("(10,-7)", ac) == "(10,-7)"
    assert format_correct_answer_display("(10,-7)", {"answer_contract": ac}) == "(10,-7)"
    assert format_correct_answer_display([10, -7], {"answer_contract": ac}) == "(10,-7)"


def test_grading_rejects_scalar_and_wrong_pair():
    ac = _coord_spec()["answer_contract"]
    current = {
        "correct_answer": "(10,-7)",
        "answer_contract": ac,
        "checker": "coordinate_pair_checker",
        "answer_type": "ordered_pair",
    }
    assert check_answer("(10,-7)", "(10,-7)", payload=current, answer_contract=ac) is True
    assert check_answer("10,-7", "(10,-7)", payload=current, answer_contract=ac) is True
    assert check_answer("T(10,-7)", "(10,-7)", payload=current, answer_contract=ac) is True
    assert check_answer("x=10,y=-7", "(10,-7)", payload=current, answer_contract=ac) is True
    assert check_answer("4", "(10,-7)", payload=current, answer_contract=ac) is False
    assert check_answer("10", "(10,-7)", payload=current, answer_contract=ac) is False
    assert check_answer("(4,10)", "(10,-7)", payload=current, answer_contract=ac) is False

    wrong = grade_answer_for_current_question("10", current, "mock_skill")
    assert wrong is not None
    assert wrong["correct"] is False
    assert "或" not in wrong["result"]
    assert "(10,-7)" in wrong["result"]


def test_coordinate_pair_checker_accepts_fraction_decimal_equivalence():
    accepted = [
        ("(1/2,-5/4)", "(0.5,-1.25)"),
        ("-5/3,13/3", "(-1.66667,4.33333)"),
        ("15/2,7", "(7.5,7)"),
        ("P(0,-2)", "(0,-2)"),
        ("T(-2,0)", "(-2,0)"),
        ("x=0,y=-2", "(0,-2)"),
        ("（0，-2）", "(0,-2)"),
    ]
    for user_answer, correct_answer in accepted:
        assert check_coordinate_pair_answer(user_answer, correct_answer), user_answer


@pytest.mark.parametrize(
    "user_answer",
    ["(2,1)", "(1/2,4/3)", "(1,2,3)", "(1/0,2)", "abc", "(1,)", "(,2)", "(1;2)"],
)
def test_coordinate_pair_checker_rejects_malformed_or_wrong_pairs(user_answer: str):
    assert check_coordinate_pair_answer(user_answer, "(1,2)") is False


def test_check_answer_route_coordinate_pair_fraction_decimal(client):
    current = {
        "skill": "vh_?詨飛B1_MidpointCoordinates",
        "question_text": "Find centroid coordinates.",
        "problem_type_id": "text_short_compute_centroid_coordinates",
        "answer_type": "coordinate_pair",
        "checker": "coordinate_pair_checker",
        "equivalence": "coordinate_pair_equivalence",
        "correct_answer": "(-1.66667,4.33333)",
        "answer": "(-1.66667,4.33333)",
        "choices": [],
        "answer_contract": {
            "answer_type": "coordinate_pair",
            "answer_shape": "coordinate_pair",
            "answer_semantics": "coordinate_pair",
            "checker": "coordinate_pair_checker",
            "checker_key": "coordinate_pair_checker",
            "answer_equivalence": "coordinate_pair_equivalence",
            "equivalence_type": "ordered_tuple_exact",
            "order_matters": True,
        },
    }
    with client.session_transaction() as sess:
        sess["current_data"] = dict(current)
    response = client.post("/check_answer", json={"answer": "-5/3,13/3"}).get_json() or {}
    assert response.get("correct") is True, response


def test_practice_normalize_session_payload():
    raw = {
        "correct_answer": "(10,-7)",
        "answer_contract": _coord_spec()["answer_contract"],
    }
    out = _normalize_gencode_runtime_payload(raw)
    assert out["display_answer"] == "(10,-7)"
    assert out["correct_answer"] == "(10,-7)"


def test_ratio_relation_latex_variants():
    assert _ratio_relation_latex("ratio_colon_form", "P", "R", "Q", 1, 2) == "$\\overline{PR}:\\overline{RQ}=1:2$"
    assert _ratio_relation_latex("multiple_form", "A", "P", "B", 2, 1) == "$\\overline{AP}=2\\overline{PB}$"
    assert _ratio_relation_latex("linear_relation_form", "M", "T", "N", 5, 4) == "$5\\overline{MT}=4\\overline{TN}$"


def test_generator_ratio_clauses_use_overline_not_plain_text():
    spec = _coord_spec()
    variants_seen: set[str] = set()
    for seed in range(120):
        p = generate_from_problem_type_spec("mock_skill", spec, seed=seed)
        q = str(p.get("question_text", ""))
        meta = p.get("metadata") if isinstance(p.get("metadata"), dict) else {}
        vid = str(meta.get("template_variant", ""))
        variants_seen.add(vid)
        assert r"\overline" in q
        if vid == "word_context_form":
            continue
        assert q.count(r"\overline") >= 3, q
        assert not re.search(r"且\s+[0-9]*[A-Z]{2}[:=]", q), q
        assert not re.search(r"且\s+[A-Z]{2}:[A-Z]{2}=", q), q
    assert "ratio_colon_form" in variants_seen
    assert "linear_relation_form" in variants_seen or "multiple_form" in variants_seen


def test_generator_stem_has_overline():
    spec = _coord_spec()
    for seed in range(40):
        p = generate_from_problem_type_spec("mock_skill", spec, seed=seed)
        q = str(p.get("question_text", ""))
        assert r"\overline" in q
        assert p.get("checker") == "coordinate_pair_checker"
        ca = p.get("correct_answer")
        assert format_coordinate_pair_display(ca)
        assert " 或 " not in format_correct_answer_display(
            ca, {"answer_contract": p.get("answer_contract", spec["answer_contract"])}
        )
