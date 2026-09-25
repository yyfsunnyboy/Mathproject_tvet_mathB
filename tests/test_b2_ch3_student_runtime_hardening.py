# -*- coding: utf-8 -*-
"""Focused B2 Ch3 student-runtime hardening regressions."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote

import pytest

from core.domain.vector_plane_domain import build_vector_plane_matrix
from core.gencode.domain_matrix_adapter import (
    _format_latex_display_answer,
    _student_facing_part_label,
    convert_domain_matrix_to_question_payload,
)


def test_same_seed_reproducible_scalar_fill():
    a = build_vector_plane_matrix(domain_operation="solve_scalar_multiple_relation_fill", seed=42)
    b = build_vector_plane_matrix(domain_operation="solve_scalar_multiple_relation_fill", seed=42)
    assert a["answer"]["value"] == b["answer"]["value"]
    assert a["question_text"] == b["question_text"]


def test_different_seeds_scalar_fill_diversity():
    answers = {
        json.dumps(
            build_vector_plane_matrix(domain_operation="solve_scalar_multiple_relation_fill", seed=s)["answer"]["value"],
            sort_keys=True,
            default=str,
        )
        for s in range(12)
    }
    assert len(answers) >= 4


def test_section_coeff_minimum_diagram_and_geometry():
    matrix = build_vector_plane_matrix(domain_operation="solve_section_coefficient_pair", seed=11)
    vs = matrix["visual_spec"]
    labels = {p["label"] for p in vs["points"]}
    assert labels == {"A", "E", "F", "M"}
    pts = {p["label"]: (p["x"], p["y"]) for p in vs["points"]}
    alpha = float(eval(str(matrix["answer"]["parts"]["alpha"]).replace("/", "/")))  # noqa: S307 — controlled
    # Use sympy-free parse for rationals like 2/3
    from fractions import Fraction

    alpha = float(Fraction(str(matrix["answer"]["parts"]["alpha"])))
    beta = float(Fraction(str(matrix["answer"]["parts"]["beta"])))
    ax, ay = pts["A"]
    ex, ey = pts["E"]
    fx, fy = pts["F"]
    mx, my = pts["M"]
    assert abs((mx - ax) - (alpha * (ex - ax) + beta * (fx - ax))) < 1e-6
    assert abs((my - ay) - (alpha * (ey - ay) + beta * (fy - ay))) < 1e-6


def test_internal_multipart_keys_get_student_labels():
    from core.gencode.domain_matrix_adapter import _student_facing_part_label, _looks_like_internal_part_key

    assert _student_facing_part_label("a_dot_a") == r"$\vec{a}\cdot\vec{a}$"
    assert _student_facing_part_label("a_dot_b") == r"$\vec{a}\cdot\vec{b}$"
    assert _student_facing_part_label("mag_2a_3b") == r"$\left|2\vec{a}-3\vec{b}\right|$"
    assert "周長" == _student_facing_part_label("perimeter")
    assert _student_facing_part_label("dot1").startswith("第")
    assert "$k_{1}$" in _student_facing_part_label("k1")
    assert r"$\alpha$" == _student_facing_part_label("alpha")
    assert not _looks_like_internal_part_key("perimeter", "周長")
    assert _looks_like_internal_part_key("a_dot_a", "a_dot_a")

    matrix = build_vector_plane_matrix(domain_operation="compute_dot_identity_multipart", seed=5)
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="short_answer",
        answer_type="multi_part",
        problem_type_id="compute_dot_identity_multipart",
        domain_operation="compute_dot_identity_multipart",
    )
    parts = (payload.get("answer_contract") or {}).get("parts") or []
    assert parts
    for part in parts:
        assert part["label"] != part["key"]
        assert part.get("display_label") == part["label"]
        assert not _looks_like_internal_part_key(part["key"], part["label"])


def test_explicit_display_label_survives_serialization():
    matrix = build_vector_plane_matrix(domain_operation="compute_regular_polygon_edge_dot", seed=2)
    assert (matrix.get("answer") or {}).get("part_labels")
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="short_answer",
        answer_type="multi_part",
        problem_type_id="compute_regular_polygon_edge_dot",
        domain_operation="compute_regular_polygon_edge_dot",
    )
    labels = {
        p["key"]: p.get("display_label") or p.get("label")
        for p in ((payload.get("answer_contract") or {}).get("parts") or [])
    }
    assert labels["dot1"] != "dot1"
    assert labels["dot2"] != "dot2"


def test_chain_closure_mcq_runtime_schema():
    matrix = build_vector_plane_matrix(domain_operation="compute_chain_closure_vector_mcq", seed=7)
    assert matrix.get("choices") and matrix.get("correct_label")
    from skills.vh_數學B2_SubSection_3_2_2 import generate

    payload = generate(seed=7, component_id="src_11821")
    assert payload.get("answer_type") in {"single_choice", "choice"}
    assert len(payload.get("choices") or []) == 4
    assert payload.get("presentation_mode") == "single_choice"


def test_angle_from_mag_avoids_parallel_degeneracy_by_default():
    angles = []
    for seed in range(20):
        matrix = build_vector_plane_matrix(domain_operation="solve_angle_from_magnitude_identity", seed=seed)
        ang = str((matrix.get("answer") or {}).get("parts", {}).get("angle_degrees") or "")
        angles.append(ang)
        # Default sampler must not emit parallel 0°/180° traps.
        assert ang not in {"0", "180"}
    assert len(set(angles)) >= 2


def test_mcq_cannot_pass_audit_with_missing_choices():
    from scripts.audit_b2_ch3_student_runtime import _runtime_is_mcq

    assert _runtime_is_mcq({"answer_type": "single_choice", "choices": []}) is True
    assert _runtime_is_mcq({"answer_type": "expression", "choices": []}) is False
    assert _runtime_is_mcq({
        "answer_type": "single_choice",
        "choices": [{"label": "A", "text": "$1$"}] * 4,
    }) is True


def test_mcq_choices_keep_math_delimiters():
    wrapped = _format_latex_display_answer(r"\overrightarrow{AB}")
    assert wrapped.startswith("$") and wrapped.endswith("$")
    matrix = build_vector_plane_matrix(domain_operation="identify_equal_vector_mcq", seed=7)
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="single_choice",
        answer_type="single_choice",
        problem_type_id="identify_equal_vector_mcq",
        domain_operation="identify_equal_vector_mcq",
    )
    choices = payload.get("choices") or []
    assert len(choices) == 4
    assert all(str(c.get("text") or "").startswith("$") for c in choices)
    assert payload.get("answer") in {"A", "B", "C", "D"}


def test_choice_math_js_wraps_overrightarrow():
    source = Path("static/js/choice_math.js").read_text(encoding="utf-8")
    assert r"\\[a-zA-Z]+" in source or "overrightarrow" in source.lower() or "Bare TeX" in source


def test_visual_spec_label_formatter_preserved():
    source = Path("static/js/visual_spec.js").read_text(encoding="utf-8")
    assert "formatDiagramLabel" in source
    assert "diagramLabelExposesRawLatex" in source


def test_practice_next_question_no_payload_reuse(logged_client=None):
    pytest.importorskip("flask")
    from app import create_app
    from models import User, db
    import uuid

    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User(username=f"rt_{uuid.uuid4().hex[:8]}", password_hash="x", role="student")
        db.session.add(user)
        db.session.commit()
        uid = user.id
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(uid)
        sess["_fresh"] = True
    skill = "vh_數學B2_SubSection_3_1_4"
    uids = []
    fps = []
    for _ in range(6):
        data = client.get(f"/get_next_question?skill={quote(skill)}&level=1").get_json() or {}
        assert not data.get("error"), data
        uids.append(data.get("question_uid"))
        fps.append(json.dumps({
            "c": data.get("component_id"),
            "a": data.get("correct_answer") or data.get("answer"),
            "q": (data.get("question_text") or "")[:120],
        }, ensure_ascii=False, sort_keys=True, default=str))
    assert len(set(uids)) == len(uids)
    assert len(set(fps)) >= 3


def test_triangle_sections_geometry_midpoint_trisection():
    from core.domain.vector_plane_gap_coverage import _figure_points

    pts = _figure_points("triangle_sections")
    a, b, c = pts["A"], pts["B"], pts["C"]
    d, e, f = pts["D"], pts["E"], pts["F"]
    # Exact construction: D,E trisect AB; F midpoint AC.
    assert d == [2, 0] and e == [4, 0]
    assert abs(d[0] - (2 * a[0] + 1 * b[0]) / 3) < 1e-9
    assert abs(e[0] - (1 * a[0] + 2 * b[0]) / 3) < 1e-9
    assert f == [(a[0] + c[0]) / 2, (a[1] + c[1]) / 2]
