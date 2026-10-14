"""Permanent B1 question delivery gate.

Every runtime-active B1 skill module (``skills/vh_數學B1_*.py``) is covered, not only skills
whose manifest is ``production_manifest_compiled``: seed-dispatched draft wrappers are
served by ``/get_next_question`` too, and a single malformed component or problem type must
fail the whole skill.
"""
from __future__ import annotations

import importlib
import inspect
import uuid
from pathlib import Path
from urllib.parse import quote

import pytest
from werkzeug.security import generate_password_hash

ROOT = Path(__file__).resolve().parents[1]
B1_SKILLS = sorted(p.stem for p in (ROOT / "skills").glob("vh_數學B1_*.py"))
GATE_SEEDS = (11, 1000)
ROUTE_SKILL = "vh_數學B1_QuadraticFunctionGraph"

VALID_PAYLOAD = {
    "question_text": "求 $y=(x-1)^2+2$ 的頂點。",
    "correct_answer": "(1,2)",
    "answer": "(1,2)",
    "answer_type": "text_short",
    "checker": "text_short_checker",
    "problem_type_id": "gate_valid",
}


# ---------------------------------------------------------------------------
# Shared gate helpers
# ---------------------------------------------------------------------------


def _runtime_units(skill_id: str, mod) -> list[tuple[str, dict]]:
    """(unit_id, generate kwargs) for every unit reachable at runtime."""
    specs = list(getattr(mod, "GENERATOR_SPECS", []) or [])
    if "generate_for_skill" in inspect.getsource(mod.generate):
        from core.gencode.runtime_skill_wrapper import dispatch_problem_type

        buckets: dict[str, list[int]] = {}
        for seed in range(300):
            pt, _strategy, _ids = dispatch_problem_type(skill_id, specs, level=1, seed=seed)
            seeds = buckets.setdefault(pt, [])
            if len(seeds) < len(GATE_SEEDS):
                seeds.append(seed)
        return [(pt, {"seeds": seeds}) for pt, seeds in buckets.items()]
    cids = [str(r.get("component_id") or "").strip() for r in specs if isinstance(r, dict)]
    return [(cid, {"component_id": cid}) for cid in cids if cid] or [("<default>", {})]


def _deliver(skill_id: str, raw: dict) -> dict:
    """Same normalization chain as /get_next_question before the delivery gate."""
    import core.routes.practice as practice
    from core.legacy_generator_adapter import normalize_runtime_value

    data = practice._canonicalize_route_payload(normalize_runtime_value(raw))
    return practice._normalize_gencode_runtime_payload(dict(data), skill_id=skill_id)


def _payload_failures(payload: dict) -> list[str]:
    from core.gencode.choice_contract_validator import _answer_matches_choice, normalize_canonical_choices
    from core.gencode.question_delivery_contract import question_delivery_errors

    failures = list(question_delivery_errors(payload))
    answer = payload.get("correct_answer", payload.get("answer"))
    if answer is None or (isinstance(answer, str) and not answer.strip()):
        failures.append("answer_missing")
    mode = str(payload.get("presentation_mode") or (payload.get("metadata") or {}).get("presentation_mode") or "")
    if payload.get("choices") or "choice" in mode:
        choices = normalize_canonical_choices(payload.get("choices"))
        if len(choices) != 4:
            failures.append(f"choice_count:{len(choices)}")
        elif not any(_answer_matches_choice(answer, c) for c in choices):
            failures.append("answer_not_in_choices")
    return failures


def audit_skill_delivery(skill_id: str, generate, units, seeds=GATE_SEEDS) -> list[str]:
    """Return failures across all units; any failing unit fails the skill."""
    failures: list[str] = []
    for unit_id, kwargs in units:
        kwargs = dict(kwargs)
        unit_seeds = kwargs.pop("seeds", None) or seeds
        for seed in unit_seeds:
            try:
                payload = _deliver(skill_id, generate(seed=seed, **kwargs))
            except Exception as exc:  # noqa: BLE001
                failures.append(f"{unit_id}@{seed}: EXCEPTION {type(exc).__name__}: {exc}")
                continue
            problems = _payload_failures(payload)
            if problems:
                failures.append(f"{unit_id}@{seed}: {','.join(problems)}")
    return failures


# ---------------------------------------------------------------------------
# Delivery contract unit tests
# ---------------------------------------------------------------------------


def test_normal_question_text_passes() -> None:
    from core.gencode.question_delivery_contract import question_delivery_errors

    assert question_delivery_errors(_deliver(ROUTE_SKILL, dict(VALID_PAYLOAD))) == []


@pytest.mark.parametrize("alias", ["question", "new_question_text", "problem_text", "prompt"])
def test_supported_legacy_alias_is_canonicalized(alias: str) -> None:
    from core.gencode.question_delivery_contract import question_delivery_errors

    raw = {k: v for k, v in VALID_PAYLOAD.items() if k != "question_text"}
    raw[alias] = "化簡 $2x+3x$。"
    delivered = _deliver(ROUTE_SKILL, raw)
    assert delivered["question_text"] == "化簡 $2x+3x$。"
    assert question_delivery_errors(delivered) == []


def test_blank_question_text_falls_back_to_alias() -> None:
    from core.gencode.question_delivery_contract import canonicalize_question_text

    out = canonicalize_question_text({"question_text": "   ", "question": "求 $x$。"})
    assert out["question_text"] == "求 $x$。"


def test_multipart_stem_structure_canonicalizes_question_text() -> None:
    from core.gencode.question_delivery_contract import canonicalize_question_text

    out = canonicalize_question_text({
        "stem_structure": {"prompt": "已知 $f(x)=x^2$：", "items": [
            {"group_label": "(1)", "text": "求 $f(2)$"}, {"group_label": "(2)", "text": "求 $f(-1)$"}]},
    })
    assert out["question_text"] == "已知 $f(x)=x^2$：\n(1) 求 $f(2)$\n(2) 求 $f(-1)$"


@pytest.mark.parametrize(
    ("payload", "reason"),
    [
        ({"correct_answer": "1"}, "question_text_missing"),
        ({"question_text": None, "correct_answer": "1"}, "question_text_not_str"),
        ({"question_text": "", "correct_answer": "1"}, "question_text_blank"),
        ({"question_text": " \n\t ", "correct_answer": "1"}, "question_text_blank"),
        ({"question_text": 42, "correct_answer": "1"}, "question_text_not_str"),
    ],
)
def test_missing_or_blank_question_text_is_rejected(payload: dict, reason: str) -> None:
    from core.gencode.question_delivery_contract import canonicalize_question_text, question_delivery_errors

    assert question_delivery_errors(canonicalize_question_text(payload)) == [reason]


def test_presentation_answer_shape_does_not_break_consistent_choices() -> None:
    """answer_shape='single_choice' is a presentation label, not a semantic choice shape."""
    from core.gencode.choice_contract_validator import validate_choice_answer_shapes

    payload = {
        "answer_contract": {"answer_shape": "single_choice"},
        "correct_answer": "B",
        "choices": [
            {"label": "A", "text": "頂點 $(2,4)$，對稱軸 $x=2$"},
            {"label": "B", "text": "頂點 $(2,-4)$，對稱軸 $x=2$"},
            {"label": "C", "text": "頂點 $(-2,-4)$，對稱軸 $x=-2$"},
            {"label": "D", "text": "頂點 $(3,-4)$，對稱軸 $x=3$"},
        ],
    }
    assert validate_choice_answer_shapes(payload) == []
    numbers = dict(payload, choices=[{"label": lab, "text": t} for lab, t in zip("ABCD", ["7", "4", "5", "3"])])
    assert validate_choice_answer_shapes(numbers) == []


def test_mixed_choice_shapes_still_rejected() -> None:
    from core.gencode.choice_contract_validator import validate_choice_answer_shapes

    payload = {
        "answer_contract": {"answer_shape": "single_choice"},
        "correct_answer": "A",
        "choices": [
            {"label": "A", "text": "$y=2x+1$"},
            {"label": "B", "text": "3"},
            {"label": "C", "text": "$y=x-1$"},
            {"label": "D", "text": "$y=-x$"},
        ],
    }
    assert validate_choice_answer_shapes(payload) == ["vocational_choice_shape_mismatch"]


def test_skill_gate_fails_when_one_component_is_malformed() -> None:
    def generate(seed=None, component_id=None):
        if component_id == "bad":
            return {"question": "", "question_text": "  ", "correct_answer": "1"}
        return dict(VALID_PAYLOAD)

    good_only = audit_skill_delivery(ROUTE_SKILL, generate, [("good", {"component_id": "good"})])
    mixed = audit_skill_delivery(
        ROUTE_SKILL, generate, [("good", {"component_id": "good"}), ("bad", {"component_id": "bad"})]
    )
    assert good_only == []
    assert mixed and all(f.startswith("bad@") for f in mixed)


# ---------------------------------------------------------------------------
# Real B1 coverage: every runtime-active component / problem type
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("skill_id", B1_SKILLS)
def test_b1_skill_every_runtime_unit_delivers_question_text(skill_id: str) -> None:
    from core.legacy_generator_adapter import invoke_skill_generate

    mod = importlib.import_module(f"skills.{skill_id}")

    def generate(seed=None, component_id=None):
        return invoke_skill_generate(mod, level=1, seed=seed, component_id=component_id,
                                     problem_type_id=None, skill_id=skill_id)

    failures = audit_skill_delivery(skill_id, generate, _runtime_units(skill_id, mod))
    assert failures == [], f"{skill_id} delivery gate FAIL: {failures[:10]}"


# ---------------------------------------------------------------------------
# Real /get_next_question route: skip malformed, bounded retry, structured error
# ---------------------------------------------------------------------------


@pytest.fixture()
def route_client():
    import config as _cfg

    db_path = ROOT / "reports" / f"pytest_b1_delivery_gate_{uuid.uuid4().hex[:8]}.db"
    previous_uri = _cfg.Config.SQLALCHEMY_DATABASE_URI
    _cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + db_path.resolve().as_posix()
    try:
        from app import create_app
        from models import SkillCurriculum, SkillInfo, User, db

        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            db.session.add(SkillInfo(skill_id=ROUTE_SKILL, skill_en_name="QuadraticFunctionGraph",
                                     skill_ch_name="B1", description="delivery gate",
                                     gemini_prompt="gate", is_active=True))
            db.session.add(SkillCurriculum(skill_id=ROUTE_SKILL, curriculum="vocational", grade=10,
                                           volume="數學B1", chapter="B1", section="gate", display_order=1))
            username = f"b1_gate_{uuid.uuid4().hex[:8]}"
            db.session.add(User(username=username, role="student", curriculum_code="vocational",
                                password_hash=generate_password_hash("pw", method="pbkdf2:sha256")))
            db.session.commit()
        client = app.test_client()
        login = client.post("/login", data={"username": username, "password": "pw", "role": "student"})
        assert login.status_code == 302
        yield client
    finally:
        _cfg.Config.SQLALCHEMY_DATABASE_URI = previous_uri
        for candidate in (db_path, Path(str(db_path) + "-wal"), Path(str(db_path) + "-shm")):
            try:
                candidate.unlink(missing_ok=True)
            except OSError:
                pass


def _scripted_generator(monkeypatch, outputs: list):
    import core.legacy_generator_adapter as lga

    calls: list[dict] = []

    def fake_invoke(mod, **kwargs):
        calls.append(kwargs)
        item = outputs[min(len(calls) - 1, len(outputs) - 1)]
        if isinstance(item, Exception):
            raise item
        return dict(item)

    monkeypatch.setattr(lga, "invoke_skill_generate", fake_invoke)
    return calls


def _get(client, seed: int | None = 7):
    url = f"/get_next_question?skill={quote(ROUTE_SKILL)}&level=1" + (f"&gen_seed={seed}" if seed is not None else "")
    resp = client.get(url)
    return resp.status_code, resp.get_json()


def test_route_skips_malformed_payload_and_delivers_next_valid(route_client, monkeypatch) -> None:
    calls = _scripted_generator(monkeypatch, [
        {"question_text": "", "correct_answer": "1"},
        RuntimeError("vocational_choice_repair_failed:simulated"),
        dict(VALID_PAYLOAD),
    ])
    status, body = _get(route_client)
    assert status == 200
    assert body["question_text"] == VALID_PAYLOAD["question_text"]
    assert body["question_uid"]
    assert len(calls) == 3
    assert len({c["seed"] for c in calls}) == 3


def test_route_rejects_choice_repair_failure_then_delivers_valid(route_client, monkeypatch) -> None:
    broken_choice = {
        "question_text": "選出正確者",
        "correct_answer": "Z",
        "answer_type": "single_choice",
        "presentation_mode": "single_choice",
        "choices": [{"label": "A", "text": "$y=x$"}, {"label": "B", "text": "3"}],
    }
    calls = _scripted_generator(monkeypatch, [broken_choice, dict(VALID_PAYLOAD)])
    status, body = _get(route_client)
    assert status == 200 and body["question_text"] == VALID_PAYLOAD["question_text"]
    assert len(calls) == 2


def test_route_retry_is_bounded_and_returns_structured_error(route_client, monkeypatch) -> None:
    calls = _scripted_generator(monkeypatch, [{"question_text": "   ", "correct_answer": "1"}])
    status, body = _get(route_client, seed=None)
    assert status == 503
    assert len(calls) == 5
    assert body["success"] is False
    assert body["error_code"] == "QUESTION_DELIVERY_FAILED"
    assert body["error"] and body["skill_id"] == ROUTE_SKILL
    assert "question_text" not in body


def test_route_preserves_question_text_for_visual_and_multipart(route_client, monkeypatch) -> None:
    visual = dict(VALID_PAYLOAD, question_text="依圖判斷拋物線的頂點。",
                  diagram_spec={"type": "function_graph", "functions": ["x^2"]})
    multipart = {
        "stem_structure": {"prompt": "已知 $f(x)=x^2$：", "items": [
            {"group_label": "(1)", "text": "求 $f(2)$"}, {"group_label": "(2)", "text": "求 $f(-1)$"}]},
        "correct_answer": "4;1",
        "answer": "4;1",
    }
    _scripted_generator(monkeypatch, [visual])
    status, body = _get(route_client)
    assert status == 200 and body["question_text"] == "依圖判斷拋物線的頂點。"

    _scripted_generator(monkeypatch, [multipart])
    status, body = _get(route_client, seed=8)
    assert status == 200
    assert body["question_text"].startswith("已知 $f(x)=x^2$：")
    assert "(2) 求 $f(-1)$" in body["question_text"]
