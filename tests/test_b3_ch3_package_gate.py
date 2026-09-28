# -*- coding: utf-8 -*-
"""B3 Chapter 3 package gate: coverage, samples, checkers, and practice contracts."""
from __future__ import annotations

import importlib.util
import json
import os
import sqlite3
from pathlib import Path

import pytest

os.environ.setdefault("ADV_RAG_EAGER_INIT", "0")

from core.domain.linear_inequality_planning_domain import (  # noqa: E402
    OPS,
    SOURCE_SPECS,
    build_linear_inequality_planning_matrix,
    validate_linear_inequality_planning_matrix,
)
from core.gencode.linear_inequality_planning_capability_adapter import (  # noqa: E402
    adapt_linear_inequality_planning_matrix,
)
from core.gencode.runtime_skill_wrapper import check_answer  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
BANNED_STEM = ("隨堂", "基礎題", "進階題", "自我評量", "習題")
CHAPTER_IDS = list(range(12042, 12127))


def _representative_ids():
    seen = set()
    for example_id, spec in sorted(SOURCE_SPECS.items()):
        key = (spec["op"], spec["presentation"])
        if key in seen:
            continue
        seen.add(key)
        yield example_id, spec


def _load_generator(example_id: int, skill_id: str):
    path = ROOT / "agent_skills_v3" / skill_id / "components" / f"src_{example_id}" / "generate.py"
    spec = importlib.util.spec_from_file_location(f"b3ch3_src_{example_id}", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def _student_answer(payload: dict):
    contract = payload.get("answer_contract") or {}
    parts = contract.get("parts") or []
    if len(parts) >= 2:
        return {str(part.get("key")): part.get("expected_answer") for part in parts}
    if payload.get("answer_type") == "single_choice" or payload.get("presentation_mode") == "single_choice":
        return payload.get("correct_answer")
    return payload.get("semantic_answer")


def test_source_coverage_is_complete():
    assert set(SOURCE_SPECS) == set(CHAPTER_IDS)
    assert len(SOURCE_SPECS) == 85
    skills = {spec["skill_id"] for spec in SOURCE_SPECS.values()}
    assert "vh_數學B3_SubSection_3_2_1" not in skills
    assert all(not skill.endswith("_3_2_1") or "PlainHeading" in skill for skill in skills)
    assert not any("SubSection_3_2_" in skill for skill in skills)


def test_zero_example_skills_are_not_fabricated():
    fabricated = [
        "vh_數學B3_SubSection_3_1_1",
        "vh_數學B3_PlainHeading_3_2_1",
        "vh_數學B3_SubSection_3_3_2",
    ]
    for skill_id in fabricated:
        assert not (ROOT / "skills" / f"{skill_id}.py").exists()
        assert not (ROOT / "agent_skills_v3" / skill_id).exists()


def test_family_samples_and_source_label_gate():
    """SOURCE_LABEL_NOT_IN_STUDENT_STEM and generator sample gate."""
    reps = {}
    for example_id, spec in SOURCE_SPECS.items():
        reps.setdefault(spec["op"], example_id)
    assert len(reps) == len(OPS)
    failures = []
    for op, example_id in reps.items():
        for offset in range(60):
            matrix = build_linear_inequality_planning_matrix(
                example_id * 100 + offset,
                {"textbook_example_id": example_id},
            )
            if not validate_linear_inequality_planning_matrix(matrix):
                failures.append((op, offset, "invalid"))
                continue
            stem = matrix["question_text"]
            if any(token in stem for token in BANNED_STEM):
                failures.append((op, offset, "label"))
            if not stem.strip():
                failures.append((op, offset, "empty"))
    assert failures == []


def test_mcq_identity_and_multipart_arity():
    """PRACTICE_MCQ_CHOICE_IDENTITY_GATE and MULTIPART_ANSWER_ARITY_GATE."""
    for example_id, spec in _representative_ids():
        matrix = build_linear_inequality_planning_matrix(example_id, {"textbook_example_id": example_id})
        payload = adapt_linear_inequality_planning_matrix(
            matrix,
            domain_operation=spec["op"],
            presentation_mode=spec["presentation"],
            answer_type=matrix["answer_type"],
            textbook_example_id=example_id,
            component_id=f"src_{example_id}",
        )
        if matrix["presentation_mode"] == "single_choice":
            choices = payload["choices"]
            values = [row["value"] for row in choices]
            assert len(values) == 4
            assert len(set(values)) == 4
            assert matrix["semantic_answer"] in values
            label = matrix["correct_label"]
            matched = next(row for row in choices if row["label"] == label)
            assert matched["value"] == matrix["semantic_answer"]
            from core.gencode.choice_contract_validator import validate_vocational_multiple_choice

            payload["skill_id"] = spec["skill_id"]
            payload["curriculum_profile"] = "vocational_high_b"
            assert validate_vocational_multiple_choice(payload, spec["skill_id"]) == []
        if matrix["answer_type"] == "multi_part":
            parts = payload["answer_contract"]["parts"]
            assert len(parts) == matrix["validation_facts"]["multipart_count"]
            assert len(parts) >= 2


def test_checker_accepts_semantic_answer_and_equivalent_fraction():
    module = _load_generator(12092, "vh_數學B3_SubSection_3_3_4")
    payload = module.generate(seed=7)
    assert check_answer(_student_answer(payload), payload.get("correct_answer"), payload=payload)
    assert check_answer("28/2", payload.get("correct_answer"), payload=payload) or payload.get("semantic_answer") != "14"
    unique = _load_generator(12052, "vh_數學B3_SubSection_3_1_3")
    unique_payload = unique.generate(seed=3)
    assert check_answer(
        unique_payload.get("semantic_answer"),
        unique_payload.get("correct_answer"),
        payload=unique_payload,
    )


def test_diagram_payload_matches_halfplane_semantics():
    matrix = build_linear_inequality_planning_matrix(4, {"textbook_example_id": 12066})
    visual = matrix["visual_spec"]
    line = visual["lines"][0]
    assert line["a"] == matrix["givens"]["a"]
    assert line["b"] == matrix["givens"]["b"]
    assert line["c"] == matrix["givens"]["c"]
    included = matrix["givens"]["op"] in {"<=", ">="}
    assert line["style"] == ("solid" if included else "dashed")
    assert visual["shade"]["boundary_included"] is included
    lp = build_linear_inequality_planning_matrix(5, {"textbook_example_id": 12090})
    xs = [float(point[0]) for point in lp["visual_spec"]["vertices"]]
    ys = [float(point[1]) for point in lp["visual_spec"]["vertices"]]
    lo_x, hi_x = lp["visual_spec"]["x_range"]
    lo_y, hi_y = lp["visual_spec"]["y_range"]
    assert min(xs) >= lo_x and max(xs) <= hi_x
    assert min(ys) >= lo_y and max(ys) <= hi_y


def test_deeplink_is_consumed_once():
    """PRACTICE_TEXTBOOK_EXAMPLE_DEEPLINK_GATE"""
    text = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    assert "__textbookExampleIdConsumed" in text
    assert "textbook_example_id" in text


def test_answer_layout_does_not_stretch_labels():
    css = (ROOT / "static" / "css" / "practice_answer_layout.css").read_text(encoding="utf-8")
    assert "flex: 1 1 auto" not in css


def test_practice_bootstrap_script_has_get_next_question():
    """GLOBAL_PRACTICE_BOOTSTRAP_GATE: the practice page still requests questions."""
    text = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    assert "/get_next_question" in text
    assert "function loadQuestion" in text or "loadQuestion" in text


def test_production_corpus_readonly():
    db_path = ROOT / "instance" / "kumon_math.db"
    if not db_path.exists():
        pytest.skip("production db absent")
    uri = "file:" + str(db_path.resolve()).replace("\\", "/") + "?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    try:
        rows = conn.execute(
            """
            SELECT id, skill_id, source_chapter
            FROM textbook_examples
            WHERE id BETWEEN 12042 AND 12126
            """
        ).fetchall()
    except sqlite3.OperationalError:
        pytest.skip("textbook table unavailable")
    finally:
        conn.close()
    assert len(rows) == 85
    assert all(row[1] for row in rows)
    assert all(row[2] and "3" in str(row[2]) for row in rows)


@pytest.fixture(scope="module")
def auth_client(tmp_path_factory):
    import config
    from werkzeug.security import generate_password_hash

    db_path = tmp_path_factory.mktemp("b3ch3") / "gate.db"
    db_uri = "sqlite:///" + str(db_path.resolve()).replace("\\", "/")
    patch = pytest.MonkeyPatch()
    patch.setattr(config.Config, "SQLALCHEMY_DATABASE_URI", db_uri)
    from app import create_app
    from models import User, db

    app = create_app()
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    with app.app_context():
        user = User(
            username="b3_ch3_gate",
            password_hash=generate_password_hash("pass1234"),
            role="student",
        )
        db.session.add(user)
        db.session.commit()
    client = app.test_client()
    login = client.post("/login", data={"username": "b3_ch3_gate", "password": "pass1234"})
    assert login.status_code in {302, 303}
    try:
        yield client
    finally:
        with app.app_context():
            db.session.remove()
            db.engine.dispose()
        patch.undo()


@pytest.mark.parametrize(
    "skill_id,component_id",
    [
        ("vh_數學B3_SubSection_3_1_2", "src_12042"),
        ("vh_數學B3_SubSection_3_1_2", "src_12046"),
        ("vh_數學B3_SubSection_3_1_3", "src_12050"),
        ("vh_數學B3_PlainHeading_3_2_3", "src_12069"),
        ("vh_數學B3_SubSection_3_3_3", "src_12090"),
        ("vh_數學B3_SubSection_3_3_1", "src_12113"),
    ],
)
def test_runtime_get_next_and_check(auth_client, skill_id, component_id):
    response = auth_client.get(
        "/get_next_question",
        query_string={"skill": skill_id, "level": 1, "component_id": component_id, "gen_seed": 4},
    )
    assert response.status_code == 200, response.get_data(as_text=True)[:500]
    question = response.get_json()
    assert question.get("component_id") == component_id
    stem = question.get("question_text") or ""
    assert not any(token in stem for token in BANNED_STEM)
    answer = _student_answer(question)
    body = {
        "skill_id": question.get("skill_id"),
        "question_uid": question.get("question_uid"),
        "problem_type_id": question.get("problem_type_id") or "",
        "answer": answer,
    }
    if isinstance(answer, dict):
        body["answers"] = answer
        body["user_answer"] = answer
    checked = auth_client.post("/check_answer", data=json.dumps(body), content_type="application/json")
    payload = checked.get_json(silent=True) or {}
    assert checked.status_code == 200
    assert payload.get("correct") is True, payload
