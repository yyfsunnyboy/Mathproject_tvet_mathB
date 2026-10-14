# -*- coding: utf-8 -*-
"""Exhaustive B3 Ch1 answer-arity audit (generator → wrapper → API → render → checker).

Writes:
  reports/b3_ch1_answer_arity_audit.json
  reports/b3_ch1_answer_arity_audit.md

Does not modify mathematical coverage reports.
"""

from __future__ import annotations

import importlib
import json
import uuid
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
COVERAGE_PATH = ROOT / "reports" / "b3_ch1_family_coverage.json"
OUT_JSON = ROOT / "reports" / "b3_ch1_answer_arity_audit.json"
OUT_MD = ROOT / "reports" / "b3_ch1_answer_arity_audit.md"

from core.gencode.multipart_answer_arity import (  # noqa: E402
    arity_status,
    checker_answer_count,
    expected_answer_field_count,
    generator_answer_count_from_matrix,
    is_mcq_payload,
    rendered_answer_field_count,
    resolve_multipart_fields,
)


def _import_skill(skill_id: str):
    return importlib.import_module(f"skills.{skill_id}")


def _question_type(payload: dict[str, Any]) -> str:
    return str(
        payload.get("question_type")
        or payload.get("problem_type_id")
        or payload.get("domain_operation")
        or ""
    )


def _answer_type(payload: dict[str, Any]) -> str:
    ac = payload.get("answer_contract") if isinstance(payload.get("answer_contract"), dict) else {}
    return str(payload.get("answer_type") or ac.get("answer_type") or "").strip()


def _bucket(expected: int, *, mcq: bool) -> str:
    if mcq:
        return "mcq"
    if expected <= 1:
        return "single"
    if expected == 2:
        return "multipart_2"
    if expected == 3:
        return "multipart_3"
    return "multipart_4plus"


def _mutate_part(answer: Any, part_index: int) -> Any:
    if isinstance(answer, dict):
        keys = list(answer.keys())
        if not keys:
            return answer
        idx = min(max(part_index, 0), len(keys) - 1)
        bad = dict(answer)
        bad[keys[idx]] = "__WRONG__"
        return bad
    return "__WRONG__"


def audit_row(row: dict[str, Any], client) -> dict[str, Any]:
    skill_id = str(row["skill_id"])
    generator_key = str(row["generator_key"])
    source_id = row.get("source_id")
    family = str(row.get("family_id") or row.get("domain_op") or "")
    mod = _import_skill(skill_id)

    payload = mod.generate(seed=7, component_id=generator_key)
    wrapper_count = expected_answer_field_count(payload)
    generator_count = wrapper_count
    # Prefer matrix arity when generate exposes embedded matrix metadata.
    meta = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    matrix = meta.get("domain_matrix") if isinstance(meta.get("domain_matrix"), dict) else None
    if matrix is None and isinstance(payload.get("domain_matrix"), dict):
        matrix = payload.get("domain_matrix")
    if matrix is not None:
        generator_count = generator_answer_count_from_matrix(matrix)
    else:
        # Domain answer.parts may still be on payload answer / contract.
        generator_count = checker_answer_count(payload)

    # Formal practice API path.
    client.get(f"/practice/{quote(skill_id)}")
    resp = client.get(
        f"/get_next_question?skill={quote(skill_id)}"
        f"&level=1&gen_seed=7&component_id={quote(generator_key)}"
    )
    api_payload = resp.get_json(silent=True) or {}
    api_ok = resp.status_code == 200 and not api_payload.get("error")
    if not api_ok:
        # Fall back to generate payload for arity measurement but flag failure.
        api_payload = payload

    expected = expected_answer_field_count(api_payload if api_ok else payload)
    # Prefer generate-side expected when API accidentally collapses — still report API.
    gen_expected = expected_answer_field_count(payload)
    if gen_expected > expected:
        expected = gen_expected

    api_count = expected_answer_field_count(api_payload) if api_ok else 0
    rendered = rendered_answer_field_count(api_payload if api_ok else payload)
    checker_n = checker_answer_count(api_payload if api_ok else payload)
    mcq = is_mcq_payload(api_payload if api_ok else payload)
    fields = resolve_multipart_fields(api_payload if api_ok else payload)
    labels = [f.get("label") for f in fields]

    # Submit / checker glue on generate payload (same contract as API).
    check_payload = payload
    ans = check_payload.get("answer")
    if ans in (None, "", [], {}):
        ans = check_payload.get("correct_answer")
    submit_ok = True
    submit_reason = "ok"
    try:
        if not mod.check(ans, ans, question_payload=check_payload):
            submit_ok = False
            submit_reason = "correct_rejected"
        elif expected > 1 and isinstance(ans, dict):
            for i in range(expected):
                bad = _mutate_part(ans, i)
                if mod.check(bad, ans, question_payload=check_payload):
                    submit_ok = False
                    submit_reason = f"part_{i}_wrong_accepted"
                    break
            # Missing one key must reject.
            if submit_ok and len(ans) > 1:
                incomplete = dict(ans)
                incomplete.pop(next(iter(incomplete)))
                if mod.check(incomplete, ans, question_payload=check_payload):
                    submit_ok = False
                    submit_reason = "missing_part_accepted"
        elif expected == 1 and not mcq:
            if mod.check("__WRONG__", ans, question_payload=check_payload):
                submit_ok = False
                submit_reason = "wrong_single_accepted"
    except Exception as exc:  # noqa: BLE001
        submit_ok = False
        submit_reason = f"check_error:{type(exc).__name__}"

    status, reason = arity_status(
        expected=expected,
        generator=generator_count,
        wrapper=wrapper_count,
        api=api_count if api_ok else -1,
        rendered=rendered,
        checker=checker_n,
        is_mcq=mcq,
    )
    if not api_ok and status == "PASS":
        status = "SCHEMA_MISMATCH"
        reason = f"api_fetch_failed:{api_payload.get('error') or resp.status_code}"
    if not submit_ok and status == "PASS":
        status = "CHECKER_MISMATCH"
        reason = submit_reason

    return {
        "source_id": source_id,
        "skill_id": skill_id,
        "generator_key": generator_key,
        "family": family,
        "question_type": _question_type(payload),
        "answer_type": _answer_type(api_payload if api_ok else payload),
        "expected_answer_count": expected,
        "generator_answer_count": generator_count,
        "wrapper_answer_count": wrapper_count,
        "api_answer_count": api_count if api_ok else None,
        "rendered_input_count": rendered,
        "checker_answer_count": checker_n,
        "field_labels": labels,
        "is_mcq": mcq,
        "bucket": _bucket(expected, mcq=mcq),
        "api_ok": api_ok,
        "submit_checker_ok": submit_ok,
        "submit_checker_reason": submit_reason,
        "status": status,
        "reason": reason,
        "coverage_status": row.get("status"),
    }


def main() -> dict[str, Any]:
    coverage = json.loads(COVERAGE_PATH.read_text(encoding="utf-8"))
    rows = list(coverage.get("rows") or [])
    assert len(rows) == 74, f"expected 74 coverage rows, got {len(rows)}"

    from app import create_app
    from models import User, db

    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User(username=f"arity_{uuid.uuid4().hex[:8]}", password_hash="x", role="student")
        db.session.add(user)
        db.session.commit()
        uid = user.id

    client = app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(uid)
        sess["_fresh"] = True

    audit_rows: list[dict[str, Any]] = []
    for row in rows:
        audit_rows.append(audit_row(row, client))

    buckets = Counter(r["bucket"] for r in audit_rows)
    status_counts = Counter(r["status"] for r in audit_rows)
    by_skill: dict[str, Any] = {}
    for r in audit_rows:
        skill = r["skill_id"]
        if skill not in by_skill:
            by_skill[skill] = {
                "single": 0,
                "multipart_2": 0,
                "multipart_3": 0,
                "multipart_4plus": 0,
                "mcq": 0,
                "other": 0,
                "pass": 0,
                "fail": 0,
            }
        b = r["bucket"]
        if b in by_skill[skill]:
            by_skill[skill][b] += 1
        else:
            by_skill[skill]["other"] += 1
        if r["status"] == "PASS":
            by_skill[skill]["pass"] += 1
        else:
            by_skill[skill]["fail"] += 1

    multi = [r for r in audit_rows if r["expected_answer_count"] > 1 and not r["is_mcq"]]
    fails = [r for r in audit_rows if r["status"] != "PASS"]
    arity_pass = sum(1 for r in audit_rows if r["status"] == "PASS")
    render_pass = sum(
        1
        for r in audit_rows
        if r["expected_answer_count"] == r["rendered_input_count"]
    )
    submit_pass = sum(1 for r in audit_rows if r["submit_checker_ok"])

    report = {
        "total_examples": len(audit_rows),
        "inventory": {
            "single_answer": buckets.get("single", 0),
            "multi_answer_2": buckets.get("multipart_2", 0),
            "multi_answer_3": buckets.get("multipart_3", 0),
            "multi_answer_4plus": buckets.get("multipart_4plus", 0),
            "mcq": buckets.get("mcq", 0),
        },
        "acceptance": {
            "arity_pass": arity_pass,
            "arity_fail": len(audit_rows) - arity_pass,
            "render_pass": render_pass,
            "render_fail": len(audit_rows) - render_pass,
            "submit_checker_pass": submit_pass,
            "submit_checker_fail": len(audit_rows) - submit_pass,
        },
        "status_counts": dict(status_counts),
        "by_skill": by_skill,
        "multi_answer_generators": [
            {
                "source_id": r["source_id"],
                "skill_id": r["skill_id"],
                "generator_key": r["generator_key"],
                "expected": r["expected_answer_count"],
                "labels": r["field_labels"],
                "status": r["status"],
            }
            for r in multi
        ],
        "mismatched": [
            {
                "source_id": r["source_id"],
                "skill_id": r["skill_id"],
                "generator_key": r["generator_key"],
                "expected": r["expected_answer_count"],
                "api": r["api_answer_count"],
                "rendered": r["rendered_input_count"],
                "status": r["status"],
                "reason": r["reason"],
            }
            for r in fails
        ],
        "rows": audit_rows,
        "math_coverage_unchanged": "74/74 SUPPORTED (see b3_ch1_family_coverage.json)",
        "practice_runtime_field_contract": (
            "PASS" if not fails else "REOPENED_FAIL"
        ),
    }

    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# B3 Ch1 Answer-Arity Runtime Audit",
        "",
        f"total_examples = {report['total_examples']}",
        "",
        "## Inventory",
        f"- single_answer = {report['inventory']['single_answer']}",
        f"- multi_answer_2 = {report['inventory']['multi_answer_2']}",
        f"- multi_answer_3 = {report['inventory']['multi_answer_3']}",
        f"- multi_answer_4plus = {report['inventory']['multi_answer_4plus']}",
        f"- mcq = {report['inventory']['mcq']}",
        "",
        "## Acceptance",
        f"- arity_pass = {report['acceptance']['arity_pass']}",
        f"- arity_fail = {report['acceptance']['arity_fail']}",
        f"- render_pass = {report['acceptance']['render_pass']}",
        f"- render_fail = {report['acceptance']['render_fail']}",
        f"- submit_checker_pass = {report['acceptance']['submit_checker_pass']}",
        f"- submit_checker_fail = {report['acceptance']['submit_checker_fail']}",
        "",
        "## By Skill",
    ]
    for skill, stats in by_skill.items():
        short = skill.replace("vh_數學B3_SubSection_", "")
        lines.append(
            f"- `{short}`: single={stats['single']} m2={stats['multipart_2']} "
            f"m3={stats['multipart_3']} m4+={stats['multipart_4plus']} "
            f"mcq={stats['mcq']} PASS={stats['pass']} FAIL={stats['fail']}"
        )

    lines.extend(["", "## Multi-answer generators", ""])
    for r in multi:
        lines.append(
            f"- {r['source_id']} `{r['generator_key']}` expected={r['expected_answer_count']} "
            f"labels={r['field_labels']} status={r['status']}"
        )

    lines.extend(["", "## Mismatched", ""])
    if not fails:
        lines.append("(none)")
    else:
        lines.append("| source_id | skill | expected | api | rendered | status | reason |")
        lines.append("|---|---|---:|---:|---:|---|---|")
        for r in fails:
            short = r["skill_id"].replace("vh_數學B3_SubSection_", "")
            lines.append(
                f"| {r['source_id']} | {short} | {r['expected_answer_count']} | "
                f"{r['api_answer_count']} | {r['rendered_input_count']} | "
                f"{r['status']} | {r['reason']} |"
            )

    lines.extend(
        [
            "",
            "## Notes",
            "- Mathematical coverage remains 74/74 SUPPORTED.",
            "- This audit measures practice runtime field contract only.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("total_examples", "inventory", "acceptance", "practice_runtime_field_contract")}, ensure_ascii=False, indent=2))
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    return report


if __name__ == "__main__":
    main()
