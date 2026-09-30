"""Regression: graph-translation descriptions are graded by meaning, not by string order.

Uses real B1 generator payloads and the production grading path
(``grade_answer_for_current_question`` and the ``/check_answer`` route).
"""
from __future__ import annotations

import importlib
import uuid
from pathlib import Path
from urllib.parse import quote

import pytest
from werkzeug.security import generate_password_hash

ROOT = Path(__file__).resolve().parents[1]
QFG = "vh_數學B1_QuadraticFunctionGraph"
VERTEX = "vh_數學B1_VertexFormOfQuadraticFunction"
# QFG seed 750: 比較 y=-x^2 與 y=-(x+2)^2-4 如何平移，標準答案「向左 2、向下 4」。
REPORTED_SEED = 750


def _current(skill_id: str, seed: int) -> dict:
    from core.gencode.answer_payload import refresh_runtime_question_session
    from core.legacy_generator_adapter import invoke_skill_generate, normalize_runtime_value

    mod = importlib.import_module(f"skills.{skill_id}")
    raw = invoke_skill_generate(mod, level=1, seed=seed, component_id=None, problem_type_id=None, skill_id=skill_id)
    current = refresh_runtime_question_session(normalize_runtime_value(raw), skill_id=skill_id)
    current["skill"] = skill_id
    return current


def _grade(answer: str, current: dict) -> bool:
    from core.gencode.answer_grading import grade_answer_for_current_question

    result = grade_answer_for_current_question(answer, dict(current), current["skill"])
    assert result is not None, "translation answers must use contract-aware production grading"
    return bool(result.get("correct"))


@pytest.fixture(scope="module")
def reported() -> dict:
    current = _current(QFG, REPORTED_SEED)
    assert current["correct_answer"] == "向左 2、向下 4"
    assert "(x+2)^2-4" in current["question_text"]
    assert current["checker"] == "text_short_checker"
    return current


@pytest.mark.parametrize(
    "answer",
    [
        "向左 2、向下 4",
        "向下4,向左2",
        "向下4、向左2",
        "向下４，向左２",
        "左移2單位，下降4單位",
        "往左平移兩個單位，再向下平移四個單位",
        "先向下 4 再向左 2。",
        "水平向左 2 單位，鉛直向下 4 單位",
        "向左$2$、向下$4$",
        "向左 2；向下 4",
    ],
)
def test_reported_question_accepts_semantically_equal_answers(reported: dict, answer: str) -> None:
    assert _grade(answer, reported) is True


@pytest.mark.parametrize(
    ("answer", "case"),
    [
        ("向右2、向下4", "left_right_reversed"),
        ("向下4,向右2", "left_right_reversed_swapped"),
        ("向左2、向上4", "up_down_reversed"),
        ("向左3、向下4", "wrong_horizontal_distance"),
        ("向左2、向下5", "wrong_vertical_distance"),
        ("向左4、向下2", "distances_swapped_between_axes"),
        ("向左2", "missing_vertical"),
        ("向下4", "missing_horizontal"),
        ("向左2、向下4、向上1", "extra_wrong_item"),
        ("向左2、向下4、向右1", "extra_conflicting_horizontal"),
        ("向左2、向左2、向下4", "duplicated_item"),
        ("向左2、向下4、頂點(-2,-4)", "extra_non_translation_content"),
        ("向左-2、向下4", "signed_distance"),
        ("左下", "keywords_without_values"),
        ("2、4", "values_without_directions"),
        ("", "empty"),
    ],
)
def test_reported_question_rejects_wrong_answers(reported: dict, answer: str, case: str) -> None:
    assert _grade(answer, reported) is False, case


def _translation_currents() -> list[tuple[str, int]]:
    from core.gencode.runtime_skill_wrapper import dispatch_problem_type

    picked: list[tuple[str, int]] = []
    for skill_id in (QFG, VERTEX):
        mod = importlib.import_module(f"skills.{skill_id}")
        per_pt: dict[str, int] = {}
        for seed in range(400):
            pt, _strategy, _ids = dispatch_problem_type(skill_id, mod.GENERATOR_SPECS, level=1, seed=seed)
            if "graph_translation" in pt and per_pt.get(pt, 0) < 4:
                per_pt[pt] = per_pt.get(pt, 0) + 1
                picked.append((skill_id, seed))
    return picked


@pytest.mark.parametrize(("skill_id", "seed"), _translation_currents())
def test_every_translation_problem_type_is_order_insensitive(skill_id: str, seed: int) -> None:
    current = _current(skill_id, seed)
    items = [s.strip() for s in current["correct_answer"].split("、")]
    assert _grade(current["correct_answer"], current) is True
    assert _grade(",".join(reversed(items)), current) is True
    flipped = current["correct_answer"].translate(str.maketrans("左右上下", "右左下上"))
    assert _grade(flipped, current) is False
    if len(items) == 2:
        assert _grade(items[0], current) is False


def test_non_translation_text_answer_keeps_exact_matching() -> None:
    from core.checkers.translation_description_checker import check_translation_description_answer
    from core.gencode.runtime_skill_wrapper import check_answer

    contract = {"answer_type": "text_short", "checker": "text_short_checker", "answer_equivalence": "exact_string"}
    assert check_translation_description_answer("向上", "向上") is None
    assert check_answer("向上", "向上", answer_contract=contract) is True
    assert check_answer("向下", "向上", answer_contract=contract) is False


def test_multi_part_text_part_uses_translation_semantics() -> None:
    from core.checkers.multi_part_answer_checker import check_multi_part_answer

    contract = {
        "answer_type": "multi_part",
        "checker": "multi_part_answer_checker",
        "parts": [
            {"key": "shift", "checker": "text_short_checker", "expected_answer": "向左 2、向下 4"},
            {"key": "k", "checker": "integer_checker", "expected_answer": "-4"},
        ],
    }
    ok = check_multi_part_answer({"shift": "下降4單位，左移2單位", "k": "-4"}, None, answer_contract=contract)
    bad = check_multi_part_answer({"shift": "向右2、向下4", "k": "-4"}, None, answer_contract=contract)
    assert ok["overall_correct"] is True
    assert bad["overall_correct"] is False and bad["failed_parts"] == ["shift"]


# ---------------------------------------------------------------------------
# Real /get_next_question -> /check_answer route
# ---------------------------------------------------------------------------


@pytest.fixture()
def student_client():
    import config as _cfg

    db_path = ROOT / "reports" / f"pytest_b1_translation_{uuid.uuid4().hex[:8]}.db"
    previous_uri = _cfg.Config.SQLALCHEMY_DATABASE_URI
    _cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + db_path.resolve().as_posix()
    try:
        from app import create_app
        from models import SkillCurriculum, SkillInfo, User, db

        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            db.session.add(SkillInfo(skill_id=QFG, skill_en_name="QuadraticFunctionGraph", skill_ch_name="B1",
                                     description="translation grading", gemini_prompt="gate", is_active=True))
            db.session.add(SkillCurriculum(skill_id=QFG, curriculum="vocational", grade=10, volume="數學B1",
                                           chapter="B1", section="translation", display_order=1))
            username = f"b1_translation_{uuid.uuid4().hex[:8]}"
            db.session.add(User(username=username, role="student", curriculum_code="vocational",
                                password_hash=generate_password_hash("pw", method="pbkdf2:sha256")))
            db.session.commit()
        client = app.test_client()
        assert client.post("/login", data={"username": username, "password": "pw", "role": "student"}).status_code == 302
        yield client
    finally:
        _cfg.Config.SQLALCHEMY_DATABASE_URI = previous_uri
        for candidate in (db_path, Path(str(db_path) + "-wal"), Path(str(db_path) + "-shm")):
            try:
                candidate.unlink(missing_ok=True)
            except OSError:
                pass


def _route_check(client, answer: str) -> dict:
    question = client.get(f"/get_next_question?skill={quote(QFG)}&level=1&gen_seed={REPORTED_SEED}").get_json()
    assert question["correct_answer"] == "向左 2、向下 4"
    resp = client.post("/check_answer", json={
        "answer": answer, "skill_id": QFG, "question_uid": question["question_uid"],
    })
    assert resp.status_code == 200
    return resp.get_json()


@pytest.mark.parametrize(
    ("answer", "expected"),
    [
        ("向下4,向左2", True),
        ("左移2單位，下降4單位", True),
        ("向右2、向下4", False),
        ("向左2、向上4", False),
        ("向左2", False),
        ("向左2、向下4、向上1", False),
    ],
)
def test_check_answer_route_grades_translation_by_meaning(student_client, answer: str, expected: bool) -> None:
    body = _route_check(student_client, answer)
    assert bool(body.get("correct")) is expected, body
