"""B3_CH2_SUBMIT_CHECKER_GATE

Authenticated practice submit path for vocational B3 chapter 2.

browser field values
  -> the same JSON body templates/index.html posts from buildCheckAnswerPayload
  -> POST /check_answer
  -> grade_answer_for_current_question
  -> correct / incorrect

The session user exists only in a temporary sqlite database created by this
test. No production password is read or changed, and no student history row
is written outside that database.

Chapter 3 can reuse fetch_question(), submit_answer(), and the multipart
mutation helpers. The chapter 2 cases below name the components that must
keep passing.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

import pytest

os.environ.setdefault("ADV_RAG_EAGER_INIT", "0")


SKILL_211 = "vh_數學B3_SubSection_2_1_1"
SKILL_212 = "vh_數學B3_SubSection_2_1_2"
SKILL_221 = "vh_數學B3_SubSection_2_2_1"
SKILL_222 = "vh_數學B3_SubSection_2_2_2"
SKILL_223 = "vh_數學B3_SubSection_2_2_3"
SKILL_224 = "vh_數學B3_SubSection_2_2_4"

FIXTURE_PASSWORD = "pass1234"


def _canonical_parts(question: dict) -> dict[str, str]:
    contract = question.get("answer_contract") or {}
    parts = contract.get("parts") or []
    found: dict[str, str] = {}
    for index, part in enumerate(parts):
        if not isinstance(part, dict):
            continue
        key = str(part.get("key") or part.get("id") or f"part_{index + 1}")
        expected = part.get("expected_answer", part.get("answer"))
        if expected is None:
            continue
        found[key] = str(expected)
    return found


def _scalar_answer(question: dict) -> str:
    parts = _canonical_parts(question)
    if len(parts) == 1:
        return next(iter(parts.values()))
    for key in ("correct_answer", "answer", "display_answer"):
        value = question.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise AssertionError(f"no scalar answer on {question.get('component_id')}")


def _is_multipart(question: dict) -> bool:
    return len(_canonical_parts(question)) >= 2


@pytest.fixture(scope="module")
def auth_client(tmp_path_factory):
    import config
    from werkzeug.security import generate_password_hash

    db_path = tmp_path_factory.mktemp("b3ch2") / "b3_ch2_submit_gate.db"
    db_uri = "sqlite:///" + str(db_path.resolve()).replace("\\", "/")
    patch = pytest.MonkeyPatch()
    patch.setattr(config.Config, "SQLALCHEMY_DATABASE_URI", db_uri)

    from app import create_app
    from models import User, db

    app = create_app()
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    assert db_path.name in str(app.config["SQLALCHEMY_DATABASE_URI"])

    with app.app_context():
        user = User(
            username="b3_ch2_submit_gate",
            password_hash=generate_password_hash(FIXTURE_PASSWORD),
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    client = app.test_client()
    login = client.post(
        "/login",
        data={"username": "b3_ch2_submit_gate", "password": FIXTURE_PASSWORD},
        follow_redirects=False,
    )
    assert login.status_code in {302, 303}
    try:
        yield {"client": client, "app": app, "user_id": user_id, "db_path": str(db_path)}
    finally:
        with app.app_context():
            db.session.remove()
            db.engine.dispose()
        patch.undo()


def fetch_question(client, *, skill: str, component_id: str, seed: int = 3) -> dict:
    response = client.get(
        "/get_next_question",
        query_string={
            "skill": skill,
            "level": 1,
            "component_id": component_id,
            "gen_seed": seed,
        },
    )
    assert response.status_code == 200, response.get_data(as_text=True)[:800]
    question = response.get_json()
    assert question.get("question_uid"), question
    assert question.get("component_id") == component_id, question.get("component_id")
    return question


def submit_answer(client, question: dict, answer):
    """POST the same fields the practice page sends for this answer shape."""
    body = {
        "skill_id": question.get("skill_id"),
        "question_uid": question.get("question_uid"),
        "problem_type_id": question.get("problem_type_id") or "",
    }
    if isinstance(answer, dict):
        body["answer"] = answer
        body["answers"] = answer
        body["user_answer"] = answer
    else:
        body["answer"] = answer
    response = client.post(
        "/check_answer",
        data=json.dumps(body),
        content_type="application/json",
    )
    payload = response.get_json(silent=True) or {}
    return response.status_code, payload


def _assert_accepted(status: int, payload: dict, label: str) -> None:
    assert status == 200, (label, status, payload)
    assert payload.get("correct") is True, (label, payload)


def _assert_rejected(status: int, payload: dict, label: str) -> None:
    assert status == 200, (label, status, payload)
    assert payload.get("correct") is False, (label, payload)


def _mutate(value: str) -> str:
    text = str(value).strip()
    if text in {"0", "0.0"}:
        return "1"
    if text.startswith("-"):
        return text[1:] or "1"
    return f"-{text}" if text else "1"


_RELATION = re.compile(r"^\s*([A-Za-z_][\w]*)\s*(<=|>=|<|>)\s*(\S.*?)\s*$")
_OP_REVERSE = {"<": ">", ">": "<", "<=": ">=", ">=": "<="}


def _reversed_relation(text: str) -> str:
    match = _RELATION.match(str(text))
    assert match, text
    var, op, number = match.groups()
    return f"{number} {_OP_REVERSE[op]} {var}"


def _unicode_relation(text: str) -> str:
    raw = str(text)
    if "<=" in raw:
        return raw.replace("<=", "≤")
    if ">=" in raw:
        return raw.replace(">=", "≥")
    if ">" in raw:
        return raw.replace(">", "＞")
    if "<" in raw:
        return raw.replace("<", "＜")
    raise AssertionError(raw)


def _wrong_boundary(text: str) -> str:
    raw = str(text)
    if "<=" in raw:
        return raw.replace("<=", "<", 1)
    if ">=" in raw:
        return raw.replace(">=", ">", 1)
    if "<" in raw:
        return raw.replace("<", "<=", 1)
    if ">" in raw:
        return raw.replace(">", ">=", 1)
    raise AssertionError(raw)


def _choice_label(choice: dict, index: int) -> str:
    label = choice.get("label") or choice.get("key")
    if label:
        return str(label).strip()
    return "ABCD"[index]


def _mcq_correct_label(question: dict) -> str:
    answer = question.get("answer") or question.get("correct_answer")
    assert isinstance(answer, str) and len(answer.strip()) == 1, answer
    return answer.strip().upper()


def test_single_integer_and_fraction_submit(auth_client):
    client = auth_client["client"]
    integer_q = fetch_question(client, skill=SKILL_211, component_id="src_11988", seed=3)
    integer_answer = _scalar_answer(integer_q)
    assert "/" not in integer_answer
    status, payload = submit_answer(client, integer_q, integer_answer)
    _assert_accepted(status, payload, "single integer")
    integer_q = fetch_question(client, skill=SKILL_211, component_id="src_11988", seed=3)
    status, payload = submit_answer(client, integer_q, _mutate(integer_answer))
    _assert_rejected(status, payload, "single integer wrong")

    fraction_seed = None
    import importlib

    linear = importlib.import_module("skills.vh_數學B3_SubSection_2_1_1")
    for seed in range(1, 20):
        generated = linear.generate(level=1, seed=seed, component_id="src_11989")
        if "frac" in str(generated.get("question_text") or ""):
            fraction_seed = seed
            break
    assert fraction_seed is not None
    fraction_q = fetch_question(client, skill=SKILL_211, component_id="src_11989", seed=fraction_seed)
    fraction_answer = _scalar_answer(fraction_q)
    assert "frac" in str(fraction_q.get("question_text") or "")
    status, payload = submit_answer(client, fraction_q, fraction_answer)
    _assert_accepted(status, payload, "fraction exact")
    number = int(fraction_answer)
    equivalent = f"{number * 2}/2" if number >= 0 else f"-{abs(number) * 2}/2"
    fraction_q = fetch_question(client, skill=SKILL_211, component_id="src_11989", seed=fraction_seed)
    status, payload = submit_answer(client, fraction_q, equivalent)
    _assert_accepted(status, payload, "fraction equivalent")
    fraction_q = fetch_question(client, skill=SKILL_211, component_id="src_11989", seed=fraction_seed)
    status, payload = submit_answer(client, fraction_q, _mutate(fraction_answer))
    _assert_rejected(status, payload, "fraction wrong")


def _grade_relation(client, *, skill: str, component_id: str, seed: int, label: str) -> str:
    question = fetch_question(client, skill=skill, component_id=component_id, seed=seed)
    canonical = _scalar_answer(question)
    status, payload = submit_answer(client, question, canonical)
    _assert_accepted(status, payload, f"{label} canonical")
    for equivalent in (_reversed_relation(canonical), _unicode_relation(canonical)):
        assert equivalent != canonical
        question = fetch_question(client, skill=skill, component_id=component_id, seed=seed)
        status, payload = submit_answer(client, question, equivalent)
        _assert_accepted(status, payload, f"{label} equivalent {equivalent}")
    question = fetch_question(client, skill=skill, component_id=component_id, seed=seed)
    status, payload = submit_answer(client, question, _wrong_boundary(canonical))
    _assert_rejected(status, payload, f"{label} wrong boundary")
    return canonical


def test_inequality_canonical_equivalent_and_strict_boundary(auth_client):
    client = auth_client["client"]
    strict = _grade_relation(
        client, skill=SKILL_223, component_id="src_12006", seed=5, label="strict range",
    )
    assert ">" in strict and ">=" not in strict

    import importlib

    skill = importlib.import_module("skills.vh_數學B3_SubSection_2_1_2")
    inclusive_seed = None
    inclusive_key = None
    for seed in range(1, 40):
        generated = skill.generate(level=1, seed=seed, component_id="src_11979")
        raw_answer = generated.get("answer") or {}
        if isinstance(raw_answer, dict) and isinstance(raw_answer.get("parts"), dict):
            parts = raw_answer["parts"]
        elif isinstance(raw_answer, dict):
            parts = {key: value for key, value in raw_answer.items() if isinstance(value, str)}
        else:
            parts = {}
        for key, shown in parts.items():
            if "<=" in str(shown) or ">=" in str(shown):
                inclusive_seed = seed
                inclusive_key = str(key)
                break
        if inclusive_seed is not None:
            break
    assert inclusive_seed is not None and inclusive_key is not None
    question = fetch_question(client, skill=SKILL_212, component_id="src_11979", seed=inclusive_seed)
    parts = _canonical_parts(question)
    canonical = parts[inclusive_key]
    assert "<=" in canonical or ">=" in canonical
    status, payload = submit_answer(client, question, parts)
    _assert_accepted(status, payload, "inclusive canonical")
    for equivalent in (_reversed_relation(canonical), _unicode_relation(canonical)):
        mutated = dict(parts)
        mutated[inclusive_key] = equivalent
        question = fetch_question(client, skill=SKILL_212, component_id="src_11979", seed=inclusive_seed)
        status, payload = submit_answer(client, question, mutated)
        _assert_accepted(status, payload, f"inclusive equivalent {equivalent}")
    mutated = dict(parts)
    mutated[inclusive_key] = _wrong_boundary(canonical)
    question = fetch_question(client, skill=SKILL_212, component_id="src_11979", seed=inclusive_seed)
    status, payload = submit_answer(client, question, mutated)
    _assert_rejected(status, payload, "inclusive wrong boundary")


def test_quadratic_roots_keep_smaller_larger_order(auth_client):
    client = auth_client["client"]
    question = fetch_question(client, skill=SKILL_222, component_id="src_11997", seed=6)
    parts = _canonical_parts(question)
    assert len(parts) >= 2, parts
    keys = list(parts)
    status, payload = submit_answer(client, question, parts)
    _assert_accepted(status, payload, "roots order")

    swapped = {keys[0]: parts[keys[1]], keys[1]: parts[keys[0]]}
    assert swapped[keys[0]] != parts[keys[0]]
    question = fetch_question(client, skill=SKILL_222, component_id="src_11997", seed=6)
    status, payload = submit_answer(client, question, swapped)
    _assert_rejected(status, payload, "roots swapped")


def _assert_multipart_gate(client, *, skill: str, component_id: str, seed: int, label: str) -> None:
    question = fetch_question(client, skill=skill, component_id=component_id, seed=seed)
    parts = _canonical_parts(question)
    assert len(parts) >= 2, (label, parts)
    status, payload = submit_answer(client, question, parts)
    _assert_accepted(status, payload, f"{label} all correct")

    keys = list(parts)
    for key in keys:
        mutated = dict(parts)
        mutated[key] = _mutate(parts[key])
        question = fetch_question(client, skill=skill, component_id=component_id, seed=seed)
        status, payload = submit_answer(client, question, mutated)
        _assert_rejected(status, payload, f"{label} mutate {key}")

        missing = {item: parts[item] for item in keys if item != key}
        question = fetch_question(client, skill=skill, component_id=component_id, seed=seed)
        status, payload = submit_answer(client, question, missing)
        _assert_rejected(status, payload, f"{label} missing {key}")

    if len(set(parts.values())) >= 2:
        ordered = list(parts.values())
        reversed_values = list(reversed(ordered))
        assert reversed_values != ordered
        question = fetch_question(client, skill=skill, component_id=component_id, seed=seed)
        status, payload = submit_answer(client, question, reversed_values)
        _assert_rejected(status, payload, f"{label} positional mismatch")


def test_multipart_partial_and_missing_are_rejected(auth_client):
    client = auth_client["client"]
    _assert_multipart_gate(
        client, skill=SKILL_211, component_id="src_11990", seed=7, label="multipart_2",
    )
    _assert_multipart_gate(
        client, skill=SKILL_211, component_id="src_11991", seed=8, label="multipart_3",
    )
    _assert_multipart_gate(
        client, skill=SKILL_211, component_id="src_11987", seed=9, label="multipart_4plus",
    )


def _choice_text_matches_semantic(text: str, semantic: str) -> bool:
    compact_text = re.sub(r"\s+", "", text).replace("\\", "")
    compact_semantic = re.sub(r"\s+", "", semantic)
    return compact_semantic in compact_text or compact_text in compact_semantic


def _assert_mcq(client, *, skill: str, component_id: str) -> None:
    letters: dict[str, str] = {}
    for seed in range(1, 16):
        question = fetch_question(client, skill=skill, component_id=component_id, seed=seed)
        choices = question.get("choices") or []
        assert len(choices) >= 2, choices
        label = _mcq_correct_label(question)
        matched = None
        for index, choice in enumerate(choices):
            if _choice_label(choice, index).upper() == label:
                matched = choice
                break
        assert matched is not None, (label, choices)
        text = str(matched.get("text") or matched.get("value") or "")
        semantic = str(question.get("semantic_answer") or question.get("display_answer") or "")
        if semantic and semantic.upper() not in {"A", "B", "C", "D"}:
            assert _choice_text_matches_semantic(text, semantic), (semantic, text, label)
        letters[label] = text
        status, payload = submit_answer(client, question, label)
        _assert_accepted(status, payload, f"{component_id} choice {label}")
        question = fetch_question(client, skill=skill, component_id=component_id, seed=seed)
        label = _mcq_correct_label(question)
        wrong = next(item for item in "ABCD" if item != label)
        status, payload = submit_answer(client, question, wrong)
        _assert_rejected(status, payload, f"{component_id} seed {seed} wrong {wrong}")
        if len(letters) >= 2:
            break
    assert len(letters) >= 2, (component_id, letters)


def test_mcq_choice_mapping_survives_shuffle(auth_client):
    client = auth_client["client"]
    _assert_mcq(client, skill=SKILL_211, component_id="src_12032")
    _assert_mcq(client, skill=SKILL_221, component_id="src_12024")
    _assert_mcq(client, skill=SKILL_224, component_id="src_12011")


def test_src_12013_one_field_rejects_algebraic_pair(auth_client):
    client = auth_client["client"]
    from core.domain.equation_solving_domain import build_equation_solving_matrix

    seed = None
    for candidate in range(1, 80):
        matrix = build_equation_solving_matrix(
            operation="quadratic_right_triangle_side_relation",
            domain_operation="quadratic_right_triangle_side_relation",
            constraints={
                "skill_id": SKILL_222,
                "problem_type_id": "quadratic_right_triangle_side_relation",
                "required_capabilities": ["quadratic_right_triangle_side_relation"],
                "source_example_id": 12013,
            },
            seed=candidate,
            curriculum_profile="vocational_high_b",
            difficulty_profile="easy",
        )
        if int((matrix.get("params") or {}).get("d") or 0) == 5:
            seed = candidate
            break
    assert seed is not None

    question = fetch_question(client, skill=SKILL_222, component_id="src_12013", seed=seed)
    parts = _canonical_parts(question)
    assert len(parts) <= 1
    answer = _scalar_answer(question)
    assert answer == "15"
    assert not isinstance(question.get("answer"), dict) or len(question.get("answer")) == 1
    status, payload = submit_answer(client, question, "15")
    _assert_accepted(status, payload, "12013 canonical")

    algebraic = (question.get("validation_facts") or {}).get("algebraic_roots")
    if not algebraic:
        algebraic = ["15", "-5"]
    assert len(algebraic) >= 2
    assert len(parts) != len(algebraic)

    for wrong in ("-5", "20", "15,-5", "-5,15"):
        question = fetch_question(client, skill=SKILL_222, component_id="src_12013", seed=seed)
        status, payload = submit_answer(client, question, wrong)
        _assert_rejected(status, payload, f"12013 {wrong}")


def test_authenticated_submit_persists_only_fixture_user(auth_client):
    client = auth_client["client"]
    question = fetch_question(client, skill=SKILL_211, component_id="src_11988", seed=3)
    status, payload = submit_answer(client, question, _scalar_answer(question))
    _assert_accepted(status, payload, "persist sample")

    from models import PracticeAttempt, Progress, QuizAttempt, db

    app = auth_client["app"]
    with app.app_context():
        uri = str(db.engine.url)
        assert Path(auth_client["db_path"]).name in uri
        progress = Progress.query.filter_by(user_id=auth_client["user_id"]).all()
        assert progress, "expected a progress row for the fixture user"
        assert all(row.user_id == auth_client["user_id"] for row in progress)
        attempts = PracticeAttempt.query.all()
        quizzes = QuizAttempt.query.all()
        assert attempts, "expected a practice_attempts row for the fixture user"
        assert all(row.student_id == auth_client["user_id"] for row in attempts)
        assert all(row.user_id == auth_client["user_id"] for row in quizzes)
