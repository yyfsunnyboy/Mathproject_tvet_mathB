# -*- coding: utf-8 -*-
"""GenCode V3 healer telemetry: dedup, ledgers, metric recomputation, dashboard / CSV access."""

from __future__ import annotations

import csv
import io
import json
import sqlite3
import threading
import uuid
from datetime import datetime, timedelta

import pytest

import core.gencode.v3_healer_telemetry as telemetry
from core.gencode.schema.gencode_v3_healer_telemetry_inspection import (
    TABLE_NAME,
    ensure_gencode_v3_healer_telemetry_table,
    healer_telemetry_table_exists,
    inspect_gencode_v3_healer_telemetry_schema,
)
from core.gencode.v3_healer_adapter import (
    MODE_REPAIR,
    MODE_SHADOW,
    V3HealerRequest,
    heal_v3_component,
    heal_v3_component_after_exec_failure,
)
from core.gencode.research_healer.eligibility import RULE_ELIGIBILITY
from core.gencode.v3_healer_rules import DISABLED_RULE_IDS

CODE = '''from __future__ import annotations

from typing import Any

TEXTBOOK_EXAMPLE_ID = 5


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    norm_context = {"fixed_domain_key": "algebra.demo"}
    values = [3, 4]
    constraints = {"skill_id": "demo_skill"}
    constraints["label"] = "demo"
    total = sum(values)
    return build_payload(total, domain_operation="demo_op")


def build_payload(total: int, domain_operation: str) -> dict[str, Any]:
    return {"question_text": "3 + 4 = ?", "correct_answer": str(total), "domain_operation": domain_operation}
'''
CONTRACT = {"skill_id": "demo_skill", "fixed_domain_key": "algebra.demo", "domain_operation": "demo_op"}
DELIMITER_BROKEN = CODE.replace('constraints["label"] =', 'constraints["label" =')
TIER_A_B_BROKEN = CODE.replace("    total = sum(values)\n", "    total = sum(values\n    scale = Fraction(1)\n")
AMBIGUOUS_BROKEN = CODE.replace("total = sum(values)", "total = sum(values[0] + values[1]")
SYNTAX_ERROR = "execution_error:SyntaxError:corrupted"


class FakeValidator:
    def __init__(self, fail: bool = False):
        self.fail = fail

    def __call__(self, code: str) -> dict:
        if self.fail:
            return {"passed": False, "blockers": ["forced_gate_failure"]}
        namespace: dict = {}
        try:
            exec(compile(code, "<fake>", "exec"), namespace)  # noqa: S102
            payload = namespace["generate"](seed=42)
        except Exception as exc:  # noqa: BLE001
            return {"passed": False, "blockers": ["exec"], "exception_type": type(exc).__name__, "exception_message": str(exc)}
        return {"passed": bool(payload.get("correct_answer")), "blockers": []}


@pytest.fixture
def conn():
    connection = sqlite3.connect(":memory:")
    yield connection
    connection.close()


def _heal(code: str, mode: str, *, fail: bool = False, allowed=None):
    request = V3HealerRequest(
        component_id="src_5",
        textbook_example_id=5,
        candidate_code=code,
        failure_diagnostics={"exception_type": "SyntaxError", "exception_message": "corrupted"},
        operation_contract=CONTRACT,
        allowed_rules=allowed,
    )
    result = heal_v3_component(request, validator=FakeValidator(fail=fail), mode=mode)
    result.applied_to_pipeline = mode == MODE_REPAIR and result.status == "REPAIRED"
    return result


def _record(conn, result, run_id: str, context=None, started_at=None):
    telemetry.record_attempt_safely(
        conn, result, generation_run_id=run_id, context=context or {"environment": "test", "data_origin": "synthetic"},
        started_at=started_at,
    )
    return result


def _metrics(conn, **filters):
    return telemetry.build_dashboard_payload(conn, **filters)["metrics"]


def _events(conn, event_type=None):
    sql = f"SELECT event_type, outcome, attempt_id, rule_id, tier FROM {TABLE_NAME}"
    rows = conn.execute(sql).fetchall()
    return [r for r in rows if event_type is None or r[0] == event_type]


# --- unique rescue counting -------------------------------------------------


def test_multi_round_tier_a_plus_b_repair_counts_one_combined_rescue(conn):
    result = _record(conn, _heal(TIER_A_B_BROKEN, MODE_REPAIR), "run-1")
    assert result.status == "REPAIRED", result.reason
    assert [r["research_tier"] for r in result.rules_applied] == ["Tier A", "Tier B"]
    assert result.rounds == 3
    telemetry.record_gate_safely(conn, result, passed=True)

    totals = _metrics(conn)["totals"]
    assert totals["invocations"] == 1 and totals["eligible_attempts"] == 1
    assert totals["verified_rescues"] == 1 and totals["multi_tier_verified_rescues"] == 1
    metrics = _metrics(conn)
    assert metrics["chains"] == [{"chain": "Tier A + Tier B", "verified_rescues": 1}]
    tiers = {t["tier"]: t for t in metrics["tiers"]}
    assert tiers["Tier A"]["verified_rescues_sole"] == 0 and tiers["Tier A"]["verified_rescues_contributing"] == 1
    assert tiers["Tier B"]["verified_rescues_sole"] == 0 and tiers["Tier B"]["verified_rescues_contributing"] == 1
    assert sum(t["verified_rescues_sole"] for t in metrics["tiers"]) + totals["multi_tier_verified_rescues"] == 1
    attempt_row = conn.execute(f"SELECT repair_chain, tier FROM {TABLE_NAME} WHERE event_type='attempt'").fetchone()
    assert [c["tier"] for c in json.loads(attempt_row[0])] == ["Tier A", "Tier B"]
    assert attempt_row[1] == "Tier A+Tier B"


def test_shadow_candidate_never_counts_as_verified(conn):
    result = _record(conn, _heal(DELIMITER_BROKEN, MODE_SHADOW), "run-s")
    telemetry.record_gate_safely(conn, result, passed=True)
    totals = _metrics(conn)["totals"]
    assert totals["shadow_candidates"] == 1
    assert totals["verified_rescues"] == 0 and totals["published_rescues"] == 0


def test_gate_failure_after_repair_is_still_failed_not_rescue(conn):
    result = _record(conn, _heal(DELIMITER_BROKEN, MODE_REPAIR), "run-g")
    telemetry.record_gate_safely(conn, result, passed=False, stage="component_payload_validator")
    totals = _metrics(conn)["totals"]
    assert totals["verified_rescues"] == 0 and totals["still_failed"] == 1
    assert totals["post_repair_regression_rate"] == 1.0
    assert _metrics(conn)["recent"][0]["final_gate"] == "failed"


def test_repair_without_gate_event_is_pending_not_rescue(conn):
    _record(conn, _heal(DELIMITER_BROKEN, MODE_REPAIR), "run-p")
    totals = _metrics(conn)["totals"]
    assert totals["verified_rescues"] == 0 and totals["gate_pending"] == 1


def test_published_requires_human_approval_and_event_evidence(conn):
    result = _record(conn, _heal(DELIMITER_BROKEN, MODE_REPAIR), "run-pub")
    result.post_repair_gates = "passed"
    telemetry.record_gate_safely(conn, result, passed=True)
    spec = {"v3_healer": result.summary()}
    component = {"component_id": "src_5", "induced_spec_payload": spec}

    pending = telemetry.record_published_rescues(conn, skill_id="demo_skill", components=[component], publish_status="production_published")
    assert pending["inserted"] == 0 and pending["skipped"] == ["src_5:not_human_approved"]
    assert _metrics(conn)["totals"]["published_rescues"] == 0

    fake = {"v3_healer": {**result.summary(), "telemetry": {"attempt_id": "deadbeef"}}, "v3_healer_human_approved": True}
    no_evidence = telemetry.record_published_rescues(conn, skill_id="demo_skill", components=[{"component_id": "src_5", "induced_spec_payload": fake}], publish_status="production_published")
    assert no_evidence["skipped"] == ["src_5:no_event_evidence"]

    approved = {"component_id": "src_5", "induced_spec_payload": json.dumps({**spec, "v3_healer_human_approved": True})}
    for _ in range(2):
        telemetry.record_published_rescues(conn, skill_id="demo_skill", components=[approved], publish_status="production_published")
    totals = _metrics(conn)["totals"]
    assert totals["published_rescues"] == 1 and len(_events(conn, "publish")) == 1


def test_retry_and_resume_do_not_duplicate_events(conn):
    first = _record(conn, _heal(DELIMITER_BROKEN, MODE_REPAIR), "run-r")
    retry = _record(conn, _heal(DELIMITER_BROKEN, MODE_REPAIR), "run-r")
    assert first.telemetry["status"] == "recorded" and retry.telemetry["status"] == "duplicate"
    for _ in range(3):
        telemetry.record_gate_safely(conn, retry, passed=True)
    assert len(_events(conn, "attempt")) == 1 and len(_events(conn, "gate")) == 1
    assert _metrics(conn)["totals"]["verified_rescues"] == 1

    second_run = _record(conn, _heal(DELIMITER_BROKEN, MODE_REPAIR), "run-r2")
    telemetry.record_gate_safely(conn, second_run, passed=True)
    assert _metrics(conn)["totals"]["verified_rescues"] == 2


def test_rule_events_keep_order_and_disabled_rules_are_not_failures(conn):
    result = _record(conn, _heal(AMBIGUOUS_BROKEN, MODE_REPAIR, allowed=(*DISABLED_RULE_IDS[:2], "TIER_A_UNIQUE_MISSING_DELIMITER_REPAIR_V1")), "run-d")
    assert result.status == "ABSTAINED"
    rows = conn.execute(f"SELECT rule_seq, rule_id, outcome FROM {TABLE_NAME} WHERE event_type='rule' ORDER BY rule_seq").fetchall()
    assert [r[2] for r in rows] == ["DISABLED", "DISABLED", "ABSTAIN"]
    metrics = _metrics(conn)
    rules = {r["rule_id"]: r for r in metrics["rules"]}
    catalog_ids = {m.rule_id for m in RULE_ELIGIBILITY}
    for rule_id in DISABLED_RULE_IDS[:2]:
        expected = telemetry.RULE_STATUS_DISABLED if rule_id in catalog_ids else telemetry.RULE_STATUS_RETIRED
        assert rules[rule_id]["status"] == expected
        assert rules[rule_id]["rejected"] == 0 and rules[rule_id]["abstained"] == 0
    assert rules["TIER_A_UNIQUE_MISSING_DELIMITER_REPAIR_V1"]["status"] == telemetry.RULE_STATUS_RETIRED
    assert rules[DISABLED_RULE_IDS[0]]["disabled_skips"] == 1
    for meta in RULE_ELIGIBILITY:
        expected = telemetry.RULE_STATUS_ACTIVE if meta.v3_status == "ENABLED" else telemetry.RULE_STATUS_DISABLED
        assert rules[meta.rule_id]["status"] == expected
    tiers = {t["tier"]: t for t in metrics["tiers"]}
    assert set(telemetry.TIER_ORDER) <= set(tiers)
    assert tiers["V3 Preflight"]["status"] == telemetry.RULE_STATUS_ACTIVE
    assert tiers["Research L1"]["status"] == tiers["Research L2"]["status"] == telemetry.RULE_STATUS_DISABLED
    assert tiers["Tier A"]["status"] == telemetry.RULE_STATUS_RETIRED
    assert metrics["totals"]["abstained"] == 1 and metrics["totals"]["eligible_attempts"] == 1


# --- off / pass identity / failure isolation --------------------------------


def _wrapper(conn, mode, tmp_path, run_id="run-w", code=DELIMITER_BROKEN):
    return heal_v3_component_after_exec_failure(
        draft={"files": {"generate.py": code}},
        induced_spec=CONTRACT,
        skill_id="demo_skill",
        textbook_example_id=5,
        component_id="src_5",
        execution_error=SYNTAX_ERROR,
        dryrun_path=str(tmp_path),
        mode=mode,
        validator=FakeValidator(),
        conn=conn,
        generation_run_id=run_id,
    )


def test_off_mode_records_nothing_and_creates_no_table(conn, tmp_path, monkeypatch):
    monkeypatch.delenv("GENCODE_V3_HEALER_MODE", raising=False)
    assert _wrapper(conn, None, tmp_path) is None
    assert not healer_telemetry_table_exists(conn)
    assert telemetry.build_dashboard_payload(conn)["metrics"]["totals"]["invocations"] == 0
    assert not healer_telemetry_table_exists(conn)


def test_wrapper_records_attempt_with_evidence_and_no_source_or_answers(conn, tmp_path):
    result = _wrapper(conn, MODE_REPAIR, tmp_path)
    assert result.telemetry["status"] == "recorded"
    assert result.telemetry["environment"] == "test" and result.telemetry["data_origin"] == "synthetic"
    rows = conn.execute(f"SELECT * FROM {TABLE_NAME}").fetchall()
    blob = json.dumps([list(r) for r in rows], ensure_ascii=False)
    for forbidden in ("def generate", "correct_answer", "question_text", "3 + 4"):
        assert forbidden not in blob
    attempt = conn.execute(
        f"SELECT original_sha256, repaired_sha256, evidence_path, certificate_status, source_version FROM {TABLE_NAME} WHERE event_type='attempt'"
    ).fetchone()
    assert attempt[0] == result.original_sha256 and attempt[1] == result.repaired_sha256
    assert attempt[2] == result.evidence_path and attempt[3] == "verified"
    assert telemetry.TELEMETRY_VERSION in attempt[4]


class _BrokenConn:
    in_transaction = False

    def execute(self, *args, **kwargs):
        raise sqlite3.OperationalError("disk I/O error")

    def commit(self):
        raise sqlite3.OperationalError("disk I/O error")

    def rollback(self):
        pass


def test_telemetry_failure_never_changes_healer_result(tmp_path):
    result = _wrapper(_BrokenConn(), MODE_REPAIR, tmp_path)
    assert result.status == "REPAIRED" and result.applied_to_pipeline is True
    assert result.telemetry["status"] == "failed"
    assert result.telemetry["errors"][0].startswith("attempt:OperationalError")
    telemetry.record_gate_safely(_BrokenConn(), result, passed=True)
    assert result.telemetry["gate_status"] == "skipped:no_attempt_event"
    result.telemetry["attempt_id"] = "a" * 32
    telemetry.record_gate_safely(_BrokenConn(), result, passed=True)
    assert result.telemetry["gate_status"] == "failed" and len(result.telemetry["errors"]) == 2


def test_missing_generation_run_id_is_reported_not_raised(conn, tmp_path):
    result = _wrapper(conn, MODE_SHADOW, tmp_path, run_id="")
    assert result.status == "REPAIRED"
    assert result.telemetry["status"] == "failed"
    assert "generation_run_id_required" in result.telemetry["errors"][0]


def test_telemetry_inside_caller_transaction_uses_savepoint(conn):
    conn.execute("CREATE TABLE caller (x INTEGER)")
    conn.commit()
    conn.execute("INSERT INTO caller VALUES (1)")
    assert conn.in_transaction
    _record(conn, _heal(DELIMITER_BROKEN, MODE_SHADOW), "run-tx")
    assert conn.in_transaction
    conn.rollback()
    assert conn.execute("SELECT COUNT(*) FROM caller").fetchone()[0] == 0


# --- concurrency ------------------------------------------------------------


def test_concurrent_writers_do_not_lose_events(tmp_path):
    db_path = tmp_path / "telemetry.db"
    setup = sqlite3.connect(db_path)
    ensure_gencode_v3_healer_telemetry_table(setup)
    setup.close()
    base = _heal(DELIMITER_BROKEN, MODE_REPAIR)
    errors: list[BaseException] = []

    def worker(index: int):
        try:
            local = sqlite3.connect(db_path, timeout=30)
            for run in (f"run-{index}", "run-shared"):
                result = _heal(DELIMITER_BROKEN, MODE_REPAIR)
                _record(local, result, run)
                telemetry.record_gate_safely(local, result, passed=True)
                assert result.telemetry.get("status") in ("recorded", "duplicate"), result.telemetry
            local.close()
        except BaseException as exc:  # noqa: BLE001
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors
    check = sqlite3.connect(db_path)
    attempts = check.execute(f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE event_type='attempt'").fetchone()[0]
    gates = check.execute(f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE event_type='gate'").fetchone()[0]
    rules = check.execute(f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE event_type='rule'").fetchone()[0]
    assert attempts == 9 and gates == 9 and rules == 9 * len(base.attempts)
    assert _metrics(check)["totals"]["verified_rescues"] == 9
    check.close()


# --- ledgers, ranges, recomputation -----------------------------------------


def _populate_mixed(conn):
    old = (datetime.now() - timedelta(days=40)).isoformat(timespec="seconds")
    cases = [
        (DELIMITER_BROKEN, MODE_REPAIR, False, {"environment": "production", "data_origin": "real_world"}, "passed", None),
        (TIER_A_B_BROKEN, MODE_REPAIR, False, {"environment": "production", "data_origin": "real_world"}, "passed", old),
        (DELIMITER_BROKEN, MODE_SHADOW, False, {"environment": "production", "data_origin": "real_world"}, None, None),
        (DELIMITER_BROKEN, MODE_REPAIR, False, {"environment": "test", "data_origin": "synthetic"}, "failed", None),
        (AMBIGUOUS_BROKEN, MODE_REPAIR, False, {"environment": "test", "data_origin": "synthetic"}, None, None),
        (DELIMITER_BROKEN, MODE_REPAIR, True, {"environment": "test", "data_origin": "synthetic"}, None, None),
    ]
    for index, (code, mode, fail, ctx, gate, started) in enumerate(cases):
        result = _record(conn, _heal(code, mode, fail=fail), f"mixed-{index}", ctx, started_at=started)
        if gate:
            telemetry.record_gate_safely(conn, result, passed=gate == "passed", stage=None if gate == "passed" else "multi_seed")


def _independent_totals(conn) -> dict:
    """Plain SQL over the raw events, written independently of compute_healer_metrics."""
    q = lambda sql: conn.execute(sql).fetchone()[0]  # noqa: E731
    unit = "a.generation_run_id || '|' || a.skill_id || '|' || a.component_id"
    t = TABLE_NAME
    return {
        "invocations": q(f"SELECT COUNT(*) FROM {t} WHERE event_type='attempt'"),
        "eligible_attempts": q(f"SELECT COUNT(*) FROM {t} WHERE event_type='attempt' AND eligible=1"),
        "abstained": q(f"SELECT COUNT(*) FROM {t} WHERE event_type='attempt' AND outcome='ABSTAINED'"),
        "rejected": q(f"SELECT COUNT(*) FROM {t} WHERE event_type='attempt' AND outcome='REJECTED'"),
        "shadow_candidates": q(f"SELECT COUNT(DISTINCT {unit}) FROM {t} a WHERE a.event_type='attempt' AND a.mode='shadow' AND a.outcome='REPAIRED'"),
        "verified_rescues": q(
            f"SELECT COUNT(DISTINCT {unit}) FROM {t} a JOIN {t} g ON g.attempt_id=a.attempt_id AND g.event_type='gate' "
            "WHERE a.event_type='attempt' AND a.mode='repair' AND a.outcome='REPAIRED' AND g.outcome='passed'"
        ),
        "still_failed": q(
            f"SELECT COUNT(DISTINCT {unit}) FROM {t} a JOIN {t} g ON g.attempt_id=a.attempt_id AND g.event_type='gate' "
            "WHERE a.event_type='attempt' AND a.mode='repair' AND a.outcome='REPAIRED' AND g.outcome='failed'"
        ),
        "published_rescues": q(
            f"SELECT COUNT(DISTINCT {unit}) FROM {t} a JOIN {t} p ON p.attempt_id=a.attempt_id AND p.event_type='publish' "
            f"JOIN {t} g ON g.attempt_id=a.attempt_id AND g.event_type='gate' AND g.outcome='passed' "
            "WHERE a.event_type='attempt' AND a.mode='repair'"
        ),
    }


def test_all_totals_recompute_from_raw_events(conn):
    _populate_mixed(conn)
    totals = _metrics(conn)["totals"]
    expected = _independent_totals(conn)
    assert {k: totals[k] for k in expected} == expected
    assert expected["verified_rescues"] == 2 and expected["shadow_candidates"] == 1 and expected["still_failed"] == 1
    rule_rows = conn.execute(
        f"SELECT rule_id, outcome, COUNT(*) FROM {TABLE_NAME} WHERE event_type='rule' GROUP BY rule_id, outcome"
    ).fetchall()
    rules = {r["rule_id"]: r for r in _metrics(conn)["rules"]}
    key = {"ACCEPT": "modified", "REJECT": "rejected", "ABSTAIN": "abstained", "DISABLED": "disabled_skips"}
    for rule_id, outcome, count in rule_rows:
        assert rules[rule_id][key[outcome]] == count


def test_ledgers_and_ranges_are_separated(conn):
    _populate_mixed(conn)
    prod = _metrics(conn, environment="production", data_origin="real_world")["totals"]
    test = _metrics(conn, environment="test", data_origin="synthetic")["totals"]
    assert prod["invocations"] == 3 and test["invocations"] == 3
    assert prod["verified_rescues"] == 2 and test["verified_rescues"] == 0 and test["still_failed"] == 1
    assert _metrics(conn, mode="shadow")["totals"]["verified_rescues"] == 0
    assert _metrics(conn, mode="shadow")["totals"]["shadow_candidates"] == 1
    assert _metrics(conn, mode="repair")["totals"]["shadow_candidates"] == 0
    assert _metrics(conn, range_key="7d")["totals"]["invocations"] == 5
    assert _metrics(conn, range_key="30d")["totals"]["invocations"] == 5
    assert _metrics(conn, range_key="all")["totals"]["invocations"] == 6
    assert telemetry.normalize_filters(range_key="bogus", mode="x")["range"] == "all"


def test_context_defaults(monkeypatch):
    assert telemetry.resolve_telemetry_context() == {"environment": "test", "data_origin": "synthetic"}
    assert telemetry.resolve_telemetry_context(env={}) == {"environment": "production", "data_origin": "real_world"}
    assert telemetry.resolve_telemetry_context(env={telemetry.DATA_ORIGIN_ENV: "synthetic"}) == {
        "environment": "production",
        "data_origin": "synthetic",
    }


def test_csv_exports_cover_tiers_rules_and_origins(conn):
    _populate_mixed(conn)
    events = telemetry.load_events(conn)
    summary = list(csv.DictReader(io.StringIO(telemetry.export_summary_csv(events))))
    assert set(telemetry.SUMMARY_COLUMNS) == set(summary[0])
    assert {r["data_origin"] for r in summary} == {"real_world", "synthetic"}
    all_rows = [r for r in summary if r["rule_id"] == "__ALL__"]
    assert sum(int(r["verified_rescues"]) for r in all_rows) == 2
    assert sum(int(r["invocations"]) for r in all_rows) == 6
    rule_rows = [r for r in summary if r["rule_id"] != "__ALL__"]
    assert {"Tier A", "Tier B"} <= {r["tier"] for r in rule_rows}
    raw = telemetry.export_events_csv(events)
    assert "def generate" not in raw and raw.splitlines()[0].startswith("event_key,event_type,attempt_id")


# --- schema -----------------------------------------------------------------


def test_schema_init_is_idempotent_and_append_only(conn):
    assert ensure_gencode_v3_healer_telemetry_table(conn) is True
    assert ensure_gencode_v3_healer_telemetry_table(conn) is False
    report = inspect_gencode_v3_healer_telemetry_schema(conn)
    assert report["ok"] and report["append_only_trigger"]
    _record(conn, _heal(DELIMITER_BROKEN, MODE_REPAIR), "run-ao")
    with pytest.raises(sqlite3.DatabaseError, match="append-only"):
        conn.execute(f"UPDATE {TABLE_NAME} SET outcome='REPAIRED'")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(f"INSERT INTO {TABLE_NAME} (event_key, event_type, attempt_id, generation_run_id, component_id, skill_id, mode, environment, data_origin, outcome, created_at, source_version) VALUES ('x','attempt','a','r','c','s','off','test','synthetic','X','t','v')")


# --- dashboard / CSV routes -------------------------------------------------


@pytest.fixture
def flask_client():
    from app import app
    from models import User, db

    app.config["TESTING"] = True
    with app.app_context():
        users = {}
        for role in ("teacher", "student"):
            name = f"healer_tel_{role}_{uuid.uuid4().hex[:8]}"
            user = User(username=name, password_hash="x", role=role)
            db.session.add(user)
            db.session.commit()
            users[role] = user.id
        raw = db.engine.raw_connection()
        try:
            ensure_gencode_v3_healer_telemetry_table(raw)
            _populate_mixed(raw)
        finally:
            raw.close()
    client = app.test_client()
    yield app, client, users
    with app.app_context():
        for uid in users.values():
            user = db.session.get(User, uid)
            if user is not None:
                db.session.delete(user)
        db.session.commit()


def _login(client, user_id: int):
    with client.session_transaction() as session:
        session["_user_id"] = str(user_id)
        session["_fresh"] = True


def test_dashboard_route_matches_raw_events_and_enforces_roles(flask_client):
    app, client, users = flask_client
    _login(client, users["student"])
    assert client.get("/admin/gencode/healer-telemetry").status_code == 403
    assert client.get("/admin/gencode/healer-telemetry/export.csv").status_code == 403

    _login(client, users["teacher"])
    response = client.get("/admin/gencode/healer-telemetry?range=all")
    assert response.status_code == 200
    totals = response.get_json()["metrics"]["totals"]
    from models import db

    with app.app_context():
        raw = db.engine.raw_connection()
        try:
            expected = _independent_totals(raw)
        finally:
            raw.close()
    assert {k: totals[k] for k in expected} == expected
    assert client.get("/admin/gencode/healer-telemetry/export.csv").status_code == 403
    page = client.get("/skills").get_data(as_text=True)
    assert 'id="healer-telemetry-card"' in page and "Healer 修復統計" in page
    assert "exportHealerTelemetry('events')" not in page

    _login(client, 1)
    csv_response = client.get("/admin/gencode/healer-telemetry/export.csv?kind=summary&origin=real_world")
    assert csv_response.status_code == 200 and csv_response.mimetype == "text/csv"
    rows = list(csv.DictReader(io.StringIO(csv_response.get_data(as_text=True).lstrip("\ufeff"))))
    assert rows and {r["data_origin"] for r in rows} == {"real_world"}
    events_response = client.get("/admin/gencode/healer-telemetry/export.csv?kind=events")
    assert events_response.status_code == 200
    assert "def generate" not in events_response.get_data(as_text=True)
