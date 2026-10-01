"""Shared question-quality gates: equivalence/display, undefined variables, payload sync."""

from __future__ import annotations

import importlib
import random
import uuid
from pathlib import Path
from urllib.parse import quote

import pytest

from core.checkers.expression_equivalence_checker import check_expression_equivalence_answer
from core.checkers.inequality_solution_checker import check_inequality_solution_answer
from core.checkers.multi_part_answer_checker import check_multi_part_answer
from core.checkers.quadrant_checker import angle_location_label, check_quadrant_answer
from core.gencode.answer_payload import refresh_runtime_question_session
from core.gencode.choice_contract_validator import validate_choice_answer_shapes
from core.gencode.descriptive_statistics_answer_contract import normalize_answer_contract
from core.gencode.question_quality_gate import (
    display_answer_errors,
    internal_representation_errors,
    multipart_contract_errors,
    natural_inequality_display,
    question_quality_errors,
    undefined_variable_errors,
)


def _interval_payload(display: str) -> dict:
    return {
        "skill_id": "vh_數學B1_AbsoluteValueInequality",
        "question_text": "解不等式 $|x|\\ge 15$。",
        "problem_type_id": "absolute_value_inequality_ge",
        "answer_type": "inequality_solution",
        "correct_answer": display,
        "display_answer": display,
        "answer_contract": {
            "answer_type": "inequality_solution",
            "checker": "inequality_solution_checker",
            "canonical_answer": display,
        },
    }


# --- A. equivalence / student display ------------------------------------------------


@pytest.mark.parametrize(
    "student",
    ["x<=-15,x>=15", "x>=15,x<=-15", "x<=-15 或 x>=15", "x≤-15 或 x≥15", "(-∞,-15]∪[15,∞)"],
)
def test_abs_inequality_equivalent_forms_accepted(student: str) -> None:
    assert check_inequality_solution_answer(student, "(-inf,-15] U [15,inf)") is True


@pytest.mark.parametrize("student", ["x<-15 或 x>15", "x<=-14 或 x>=15", "-15<=x<=15"])
def test_abs_inequality_wrong_forms_rejected(student: str) -> None:
    assert check_inequality_solution_answer(student, "x<=-15 或 x>=15") is False


def test_interval_display_rewritten_to_natural_form() -> None:
    payload = _interval_payload("(-∞,-15] ∪ [15,∞)")
    assert display_answer_errors(payload) == ["display_answer_uses_internal_interval_form"]
    out = refresh_runtime_question_session(payload, skill_id=payload["skill_id"])
    assert out["display_answer"] == "x <= -15 或 x >= 15"
    assert check_inequality_solution_answer(out["display_answer"], out["correct_answer"]) is True


def test_interval_display_kept_when_skill_teaches_interval_notation() -> None:
    payload = _interval_payload("(-∞,-15] ∪ [15,∞)")
    payload["question_text"] = "以區間表示 $|x|\\ge 15$ 的解。"
    assert display_answer_errors(payload) == []


@pytest.mark.parametrize("answer", ["(-4,3)", "[-5, 1]"])
def test_coordinate_pairs_and_root_lists_are_not_inequalities(answer: str) -> None:
    payload = {
        "question_text": "求交點坐標。",
        "correct_answer": answer,
        "display_answer": answer,
        "answer_contract": {"answer_type": "coordinate_pair", "checker": "coordinate_pair_checker"},
    }
    assert natural_inequality_display(payload) is None
    assert display_answer_errors(payload) == []


def test_trig_degree_arguments_are_radians() -> None:
    assert check_expression_equivalence_answer("tan20°", "tan(pi/9)") is True
    assert check_expression_equivalence_answer("tan(20°)", "tan(pi/9)") is True
    assert check_expression_equivalence_answer("sin20°", "tan(pi/9)") is False
    assert check_expression_equivalence_answer("tan21°", "tan(pi/9)") is False
    assert check_expression_equivalence_answer("30°", "30") is True


def test_inequality_parser_accepts_unicode_radicals() -> None:
    expected = "-5*sqrt(10) - 7 < k < -7 + 5*sqrt(10)"
    assert check_inequality_solution_answer("-7-5√10<k<-7+5√10", expected) is True
    assert check_inequality_solution_answer("-7-5√10<k<5", expected) is False


def test_line_circle_range_canonical_is_natural_and_order_free() -> None:
    mod = importlib.import_module("skills.vh_數學B2_SubSection_4_2_2")
    payload = mod.generate(level=1, seed=1009, component_id="src_11855")
    canonical = str(payload["correct_answer"])
    assert "Interval" not in canonical and "\\cup" not in canonical
    assert internal_representation_errors(payload) == []
    multipart = mod.generate(level=1, seed=1009, component_id="src_11868")
    parts = multipart["answer_contract"]["parts"]
    swapped = {}
    for part in parts:
        pieces = str(part["expected_answer"]).split(" 或 ")
        swapped[part["key"]] = " 或 ".join(reversed(pieces))
    assert check_multi_part_answer(swapped, multipart["correct_answer"], answer_contract=multipart["answer_contract"])["is_correct"] is True


def test_quadrant_and_axis_labels() -> None:
    assert angle_location_label("negative_y") == "y軸負向"
    assert angle_location_label("2") == "第二象限"
    for answer in ("y軸負向", "負y軸", "y軸負半軸", "-y軸"):
        assert check_quadrant_answer(answer, "y軸負向") is True
    for answer in ("x軸負向", "y軸正向", "象限角", "第三象限"):
        assert check_quadrant_answer(answer, "y軸負向") is False


def test_standard_position_angle_multipart_uses_student_labels() -> None:
    mod = importlib.import_module("skills.vh_數學B2_SubSection_1_3_1")
    payload = mod.generate(level=1, seed=1009, component_id="src_11626")
    assert payload["correct_answer"] == {"part_1": "y軸負向", "part_2": "第二象限", "part_3": "第三象限"}
    contract = payload["answer_contract"]
    good = {"part_1": "負y軸", "part_2": "二", "part_3": "3"}
    bad = {"part_1": "y軸負向", "part_2": "第三象限", "part_3": "第三象限"}
    assert check_multi_part_answer(good, payload["correct_answer"], answer_contract=contract)["is_correct"] is True
    assert check_multi_part_answer(bad, payload["correct_answer"], answer_contract=contract)["is_correct"] is False


# --- B. undefined / stale variables --------------------------------------------------


def test_asked_variable_must_be_defined() -> None:
    bad = {"question_text": "已知 $a=3$，試求 $a+b$ 之值。", "correct_answer": "5"}
    good = {"question_text": "已知 $a=3$、$b=2$，試求 $a+b$ 之值。", "correct_answer": "5"}
    assert "asked_variable_undefined:b" in undefined_variable_errors(bad)
    assert undefined_variable_errors(good) == []


@pytest.mark.parametrize(
    "stem",
    [
        "設直線 $y=kx+2$ 過 $(1,5)$，試求 $k$。",
        "試求直線的斜率：$6x - 2y + 5 = 0$。",
        "已知△ABC中，$a=8$，$\\angle A=30^\\circ$，試求 $c$。",
        "成等比數列，設公比為r，且\\(a_1+a_2=3\\)，試求\\(r\\)。",
    ],
)
def test_defined_or_conventional_symbols_not_flagged(stem: str) -> None:
    assert undefined_variable_errors({"question_text": stem, "correct_answer": "3"}) == []


def test_answer_symbol_absent_from_stem_is_flagged() -> None:
    payload = {
        "question_text": "利用基本關係填空：(1) sin20°/cos20°。",
        "correct_answer": {"part_1": "tan(theta)"},
        "answer_contract": {"parts": [{"key": "part_1", "label": "(1)"}], "canonical_answer": {"part_1": "tan(theta)"}},
    }
    assert "answer_variable_not_in_stem:θ" in undefined_variable_errors(payload)
    assert undefined_variable_errors({"question_text": "化簡 sin(180°−θ)/sin(90°−θ)", "correct_answer": "tan(theta)"}) == []


def test_trig_identity_answers_use_stem_angles() -> None:
    mod = importlib.import_module("skills.vh_數學B2_FundamentalTrigonometricIdentities")
    payload = mod.generate(level=1, seed=1009, component_id="src_11562")
    assert "theta" not in str(payload["correct_answer"])
    assert question_quality_errors(payload) == []
    contract = payload["answer_contract"]
    assert check_multi_part_answer({"part_1": "tan20°", "part_2": "sin25°"}, payload["correct_answer"], answer_contract=contract)["is_correct"] is True
    assert check_multi_part_answer({"part_1": "tan(theta)", "part_2": "sin(theta)"}, payload["correct_answer"], answer_contract=contract)["is_correct"] is False


# --- C. question / answer / payload sync ---------------------------------------------


def test_multipart_canonical_keys_must_match_parts() -> None:
    payload = {
        "question_text": "依圖回答。",
        "correct_answer": {"x_intercept": "-3", "function_equation": "f(x)=x", "line_equation": "f(x)=x"},
        "answer_contract": {
            "checker": "multi_part_answer_checker",
            "parts": [{"key": "x_intercept", "label": "x 截距"}, {"key": "function_equation", "label": "f(x)"}],
            "canonical_answer": {"x_intercept": "-3", "function_equation": "f(x)=x", "line_equation": "f(x)=x"},
        },
    }
    assert any(e.startswith("multipart_canonical_key_mismatch") for e in multipart_contract_errors(payload))


def test_linear_function_graph_canonical_matches_parts() -> None:
    mod = importlib.import_module("skills.vh_數學B1_LinearFunction")
    payload = mod.generate(level=1, seed=1009, component_id="src_4424")
    keys = {part["key"] for part in payload["answer_contract"]["parts"]}
    assert set(payload["correct_answer"]) == keys
    assert multipart_contract_errors(payload) == []


def test_internal_representation_is_flagged() -> None:
    leak = {"question_text": "求 $k$ 的範圍。", "correct_answer": "k\\in Interval.open(-1, 2)", "display_answer": "k\\in Interval.open(-1, 2)"}
    assert internal_representation_errors(leak) == ["answer_exposes_internal_representation:display_answer"]


def test_latex_subscripts_and_choice_option_keys_are_not_internal() -> None:
    choice = {
        "question_text": "比較 $a,b,c$ 的大小。",
        "question_type": "single_choice",
        "choices": ["$\\mu_y = 2\\mu_x + 3$", "$\\sigma_y = 2\\sigma_x$", "$b<c<a$", "$a<b<c$"],
        "correct_answer": "order_bca",
        "display_answer": "order_bca",
    }
    assert internal_representation_errors(choice) == []
    choice["choices"][3] = "order_abc"
    assert internal_representation_errors(choice)


@pytest.mark.parametrize(
    ("student", "expected"),
    [
        ("m = -\\frac{1}{2}, b = 1", True),
        ("\\(m = -\\frac{1}{2}, b = 1\\)", True),
        ("b=1, m=-1/2", True),
        ("m=-0.5,b=1", True),
        ("m = 1/2, b = 1", False),
        ("m = -1/2", False),
    ],
)
def test_text_assignment_list_answers_are_value_equivalent(student: str, expected: bool) -> None:
    from core.gencode.runtime_skill_wrapper import check_answer

    contract = {"answer_type": "text", "checker": "text_short_checker"}
    assert check_answer(student, "m = -1/2, b = 1", answer_contract=contract) is expected


def test_statistics_rounding_is_one_authoritative_value() -> None:
    contract = normalize_answer_contract(70 / 6, "single_numeric", rounding_policy={"decimal_places": 0, "prefer_integer": True})
    assert contract["canonical_answer"] == "12"
    assert contract["checker"] == "decimal_tolerance_checker"
    mod = importlib.import_module("skills.vh_數學B4_CentralTendencyMeasures")
    payload = mod.generate(level=1, seed=1016, component_id="src_3835")
    assert "四捨五入至整數" in payload["question_text"]
    assert payload["correct_answer"] == payload["display_answer"] == payload["answer_contract"]["canonical_answer"]
    boundary = normalize_answer_contract(11.75, "single_numeric", rounding_policy={"decimal_places": 1, "prefer_integer": False})
    assert boundary["canonical_answer"] == "11.8"
    exact = normalize_answer_contract("79.8", "single_numeric", rounding_policy={"decimal_places": 1, "prefer_integer": False})
    assert exact["canonical_answer"] == "79.8"


def test_choice_pack_values_are_distinct_and_same_shape() -> None:
    from core.domain.exact_choice_pack import build_exact_choice_payload
    from core.domain.trigonometry_law_of_sines_domain import canonical_exact

    pack = build_exact_choice_payload("4*sqrt(6)", ["2*sqrt(6)", "8*sqrt(3)", "2*sqrt(6)"], random.Random(1), format_value=canonical_exact)
    values = [c["value"] for c in pack["choices"]]
    assert len(values) == 4 and len(set(values)) == 4
    assert pack["choices"]["ABCD".index(pack["correct_label"])]["value"] == "4*sqrt(6)"


def test_numeric_constant_choices_share_number_shape() -> None:
    ok = {"choices": ["1", "$\\sqrt{3}$", "$\\frac{\\sqrt{3}}{3}$", "$\\sqrt{2}$"], "correct_answer": "A", "semantic_answer": "1"}
    bad = {"choices": ["1", "y=2x+1", "3", "4"], "correct_answer": "A", "semantic_answer": "1"}
    assert validate_choice_answer_shapes(ok) == []
    assert validate_choice_answer_shapes(bad) == ["vocational_choice_shape_mismatch"]


# --- runtime route: authoritative/display answer passes, wrong answer fails ----------


@pytest.fixture()
def logged_client():
    import config as _cfg
    from app import create_app
    from models import User, db

    db_path = Path("reports") / f"pytest_quality_gate_{uuid.uuid4().hex[:8]}.db"
    previous_uri = _cfg.Config.SQLALCHEMY_DATABASE_URI
    _cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path.resolve()).replace("\\", "/")
    try:
        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            user = User(username=f"quality_gate_{uuid.uuid4().hex[:10]}", password_hash="test-hash", role="student")
            db.session.add(user)
            db.session.commit()
            uid = user.id
        client = app.test_client()
        with client.session_transaction() as sess:
            sess["_user_id"] = str(uid)
            sess["_fresh"] = True
        yield client
    finally:
        _cfg.Config.SQLALCHEMY_DATABASE_URI = previous_uri
        try:
            db_path.unlink(missing_ok=True)
        except OSError:
            pass


def test_b4_statistics_displayed_answer_is_accepted_by_route(logged_client) -> None:
    skill = "vh_數學B4_WeightedMean"
    url = f"/get_next_question?skill={quote(skill)}&level=1&gen_seed=1016"
    assert logged_client.get(url).status_code == 200
    wrong = logged_client.post("/check_answer", json={"answer": "-999"}).get_json() or {}
    assert wrong.get("correct") is False
    shown = wrong.get("correct_answer_display") or {}
    assert shown.get("value"), wrong
    assert logged_client.get(url).status_code == 200
    right = logged_client.post("/check_answer", json={"answer": str(shown["value"])}).get_json() or {}
    assert right.get("correct") is True, right
