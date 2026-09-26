# -*- coding: utf-8 -*-
"""MULTI_ANSWER_RENDER_CONTRACT_GATE

Global gate: expected answer arity == runtime field arity for practice payloads.
Applies to B1 / B2 / B3 / future B4 packages that emit multipart or MCQ contracts.
"""

from __future__ import annotations

import importlib
import json
import uuid
from pathlib import Path
from urllib.parse import quote

import pytest

from core.gencode.multipart_answer_arity import (
    checker_answer_count,
    expected_answer_field_count,
    is_mcq_payload,
    rendered_answer_field_count,
    resolve_multipart_fields,
)

TEMPLATE = Path("templates/index.html")
B3_COVERAGE = Path("reports/b3_ch1_family_coverage.json")

# Fixed B3 regressions (known live failures).
B3_FIXED_MULTIPART = [
    ("vh_數學B3_SubSection_1_1_4", "src_11922", 3),  # bw_tile_white_count
    ("vh_數學B3_SubSection_1_1_4", "src_11906", 2),  # recurrence general+target
    ("vh_數學B3_SubSection_1_2_2", "src_11932", 2),  # geometric mean +/-
    ("vh_數學B3_SubSection_1_2_1", "src_11950", 3),  # compound growth table cells
]

# B2 known-good baselines: 2-field, 3-field-ish, legacy single.
B2_BASELINES = [
    # multipart structured (circle plane)
    ("vh_數學B2_SubSection_4_1_1", None, "multipart_or_single"),
    # another Ch4 multipart skill
    ("vh_數學B2_SubSection_4_2_1", None, "any"),
    # legacy single equation surface
    ("vh_數學B2_SubSection_4_2_3", None, "single_ok"),
]


def _import_skill(skill_id: str):
    return importlib.import_module(f"skills.{skill_id}")


@pytest.fixture(scope="module")
def auth_client():
    from app import create_app
    from models import User, db

    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User(
            username=f"marcg_{uuid.uuid4().hex[:8]}",
            password_hash="x",
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        uid = user.id

    client = app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(uid)
        sess["_fresh"] = True
    return client


def _api_payload(client, skill_id: str, *, component_id: str | None = None, seed: int = 3):
    client.get(f"/practice/{quote(skill_id)}")
    q = f"/get_next_question?skill={quote(skill_id)}&level=1&gen_seed={seed}"
    if component_id:
        q += f"&component_id={quote(component_id)}"
    resp = client.get(q)
    data = resp.get_json(silent=True) or {}
    assert resp.status_code == 200, data
    assert not data.get("error"), data.get("error")
    return data


def test_shared_renderer_uses_answer_contract_parts_not_stem_regex() -> None:
    source = TEMPLATE.read_text(encoding="utf-8")
    assert "function resolveMultiPartFields(payload)" in source
    assert "function buildMultiPartFieldGroups(payload, subqs)" in source
    assert "function collectMultiPartAnswers()" in source
    # Must not invent arity from "(1)" / "1." stem regex as primary path.
    resolve_start = source.index("function resolveMultiPartFields(payload)")
    resolve_snip = source[resolve_start : resolve_start + 1200]
    assert "answer_contract" in resolve_snip
    assert "contract.parts" in resolve_snip
    assert "match(/\\(1\\)/" not in resolve_snip


@pytest.mark.parametrize("skill_id,component_id,expected", B3_FIXED_MULTIPART)
def test_b3_fixed_multipart_arity_via_api(auth_client, skill_id, component_id, expected):
    payload = _api_payload(auth_client, skill_id, component_id=component_id, seed=9)
    assert expected_answer_field_count(payload) == expected
    assert rendered_answer_field_count(payload) == expected
    assert checker_answer_count(payload) == expected
    fields = resolve_multipart_fields(payload)
    assert len(fields) == expected
    keys = [f["key"] for f in fields]
    assert len(keys) == len(set(keys))
    # Labels must be student-facing (not collapsed to bare "parts").
    assert "parts" not in keys
    labels = [f["label"] for f in fields]
    assert all(labels), labels
    if component_id == "src_11922":
        joined = " ".join(labels)
        assert "a_1" in joined or "首項" in joined
        assert "白色" in joined or "地磚" in joined
    if component_id == "src_11932":
        joined = " ".join(labels)
        assert "正" in joined and "負" in joined
    if component_id == "src_11950":
        joined = " ".join(labels)
        assert "年底" in joined or "年初" in joined


@pytest.mark.parametrize("skill_id,component_id,expected", B3_FIXED_MULTIPART)
def test_b3_fixed_multipart_submit_per_part_reject(skill_id, component_id, expected):
    mod = _import_skill(skill_id)
    payload = mod.generate(seed=9, component_id=component_id)
    ans = payload.get("answer")
    assert isinstance(ans, dict)
    assert len(ans) == expected
    assert mod.check(ans, ans, question_payload=payload)
    keys = list(ans.keys())
    for i, key in enumerate(keys):
        bad = dict(ans)
        bad[key] = "__WRONG__"
        assert not mod.check(bad, ans, question_payload=payload), f"part {i} wrong accepted"
    incomplete = dict(ans)
    incomplete.pop(keys[0])
    assert not mod.check(incomplete, ans, question_payload=payload)


def test_b3_ch1_full_74_arity_contract(auth_client):
    coverage = json.loads(B3_COVERAGE.read_text(encoding="utf-8"))
    rows = coverage["rows"]
    assert len(rows) == 74
    fails: list[str] = []
    mcq_ok = 0
    single_ok = 0
    multi_ok = 0
    for row in rows:
        skill_id = row["skill_id"]
        gk = row["generator_key"]
        payload = _api_payload(auth_client, skill_id, component_id=gk, seed=7)
        expected = expected_answer_field_count(payload)
        rendered = rendered_answer_field_count(payload)
        checker = checker_answer_count(payload)
        if expected != rendered or expected != checker:
            fails.append(
                f"{gk}: expected={expected} rendered={rendered} checker={checker} "
                f"type={payload.get('answer_type')}"
            )
            continue
        if is_mcq_payload(payload):
            mcq_ok += 1
            # MCQ must not be turned into multipart text inputs.
            assert not resolve_multipart_fields(payload) or expected == 1
        elif expected > 1:
            multi_ok += 1
            assert "parts" not in [f["key"] for f in resolve_multipart_fields(payload)]
        else:
            single_ok += 1
            assert rendered == 1
    assert fails == [], "arity mismatches:\n" + "\n".join(fails)
    assert mcq_ok + single_ok + multi_ok == 74


def test_b2_baseline_payloads_still_render(auth_client):
    """B2 regression: multipart and single must keep working after shared adapter fix."""
    for skill_id, component_id, kind in B2_BASELINES:
        payload = _api_payload(auth_client, skill_id, component_id=component_id, seed=5)
        expected = expected_answer_field_count(payload)
        rendered = rendered_answer_field_count(payload)
        assert expected == rendered >= 1, (skill_id, expected, rendered)
        if kind == "single_ok":
            # Prefer single, but allow multipart if skill emits structured parts.
            assert rendered >= 1
        if is_mcq_payload(payload):
            assert rendered == 1


def test_b3_mcq_not_converted_to_text_multipart(auth_client):
    coverage = json.loads(B3_COVERAGE.read_text(encoding="utf-8"))
    # Prefer coverage answer_type, then confirm at runtime (coverage.mcq can be stale).
    candidates = [
        r
        for r in coverage["rows"]
        if str(r.get("answer_type") or "") in {"single_choice", "multiple_choice", "mcq"}
        or r.get("mcq")
    ]
    assert candidates, "coverage should include at least one MCQ candidate"
    confirmed = 0
    for row in candidates:
        payload = _api_payload(
            auth_client, row["skill_id"], component_id=row["generator_key"], seed=2
        )
        if not is_mcq_payload(payload):
            continue
        assert expected_answer_field_count(payload) == 1
        assert rendered_answer_field_count(payload) == 1
        choices = payload.get("choices") or []
        assert choices, row["generator_key"]
        # Must not invent multipart text fields for a true MCQ.
        assert resolve_multipart_fields(payload) == []
        confirmed += 1
        if confirmed >= 5:
            break
    assert confirmed >= 3, f"expected runtime MCQ samples, got {confirmed}"
