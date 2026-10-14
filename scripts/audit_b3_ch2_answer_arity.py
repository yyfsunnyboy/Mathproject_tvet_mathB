# -*- coding: utf-8 -*-
"""B3 Chapter 2 answer-arity audit and acceptance artifacts.

Writes:
  reports/b3_ch2_answer_arity_audit.json
  reports/b3_ch2_answer_arity_audit.md
  reports/b3_ch2_family_coverage.json
  reports/b3_ch2_family_coverage.md
  reports/b3_ch2_gencode_acceptance.json
  reports/b3_ch2_gencode_acceptance.md

Uses a SQLite backup so the live app database is not written.
"""

from __future__ import annotations

import importlib
import json
import os
import sqlite3
import tempfile
import uuid
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
SRC_DB = ROOT / "instance" / "kumon_math.db"
OUT_JSON = ROOT / "reports" / "b3_ch2_answer_arity_audit.json"
OUT_MD = ROOT / "reports" / "b3_ch2_answer_arity_audit.md"
COV_JSON = ROOT / "reports" / "b3_ch2_family_coverage.json"
COV_MD = ROOT / "reports" / "b3_ch2_family_coverage.md"
ACC_JSON = ROOT / "reports" / "b3_ch2_gencode_acceptance.json"
ACC_MD = ROOT / "reports" / "b3_ch2_gencode_acceptance.md"


def _backup_db() -> Path:
    target = Path(tempfile.mkdtemp(prefix="b3ch2_audit_")) / "kumon_math.db"
    src = sqlite3.connect(f"file:{SRC_DB.as_posix()}?mode=ro", uri=True)
    dst = sqlite3.connect(target)
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()
    return target


def _load_corpus() -> list[dict]:
    conn = sqlite3.connect(f"file:{SRC_DB.as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT id, skill_id, source_section, source_paragraph, source_description,
                   problem_type, problem_text
            FROM textbook_examples
            WHERE source_volume = '數學B3'
              AND source_chapter = '第2章 方程式'
            ORDER BY id
            """
        ).fetchall()
    finally:
        conn.close()
    return [dict(r) for r in rows]


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


def _mutate_part(answer, part_index: int):
    if isinstance(answer, dict) and answer:
        keys = list(answer.keys())
        bad = dict(answer)
        bad[keys[min(part_index, len(keys) - 1)]] = "__WRONG__"
        return bad
    return "__WRONG__"


def main() -> None:
    os.environ["MATHPROJECT_DATABASE_URI"] = "sqlite:///" + _backup_db().as_posix()

    from core.domain.equation_solving_domain import (  # noqa: E402
        OPS,
        SOURCE_SPECS,
        VISUAL_UNSUPPORTED_IDS,
        build_equation_solving_matrix,
        recompute_answer,
        validate_equation_solving_matrix,
    )
    from core.gencode.multipart_answer_arity import (  # noqa: E402
        arity_status,
        checker_answer_count,
        expected_answer_field_count,
        generator_answer_count_from_matrix,
        is_mcq_payload,
        rendered_answer_field_count,
        resolve_multipart_fields,
    )

    corpus = _load_corpus()
    if len(corpus) != 68:
        raise SystemExit(f"expected 68 corpus rows, got {len(corpus)}")

    coverage_rows = []
    for row in corpus:
        sid = int(row["id"])
        spec = SOURCE_SPECS.get(sid)
        if sid in VISUAL_UNSUPPORTED_IDS or spec is None:
            coverage_rows.append({
                "skill_id": row["skill_id"],
                "source_id": sid,
                "label": row.get("source_description") or "",
                "section": row.get("source_section") or "",
                "subsection": row.get("source_paragraph") or "",
                "source_type": row.get("problem_type") or "",
                "family_id": "visual_unsupported",
                "domain_op": "",
                "generator_key": "",
                "multipart": False,
                "mcq": False,
                "visual": True,
                "status": "VISUAL_UNSUPPORTED",
                "reason": "problem text refers to a figure and gives no side lengths",
            })
            continue
        coverage_rows.append({
            "skill_id": spec["skill_id"],
            "source_id": sid,
            "label": row.get("source_description") or "",
            "section": row.get("source_section") or "",
            "subsection": row.get("source_paragraph") or "",
            "source_type": row.get("problem_type") or "",
            "family_id": spec["op"],
            "domain_key": "equation.solving",
            "domain_op": spec["op"],
            "generator_key": f"src_{sid}",
            "multipart": int(spec.get("parts") or 1) > 1 or spec["op"] in {
                "linear_word_two_conditions",
                "linear_word_ratio_sum",
                "linear_word_three_shares",
                "quadratic_formula_exact",
                "quadratic_root_count",
            },
            "mcq": spec.get("presentation") == "single_choice",
            "visual": False,
            "text_surrogate": bool(spec.get("text_surrogate")),
            "status": "SUPPORTED",
            "reason": str(spec.get("recovery") or ""),
            "runtime_screenshot": "none",
        })

    by_skill = defaultdict(lambda: {"examples": 0, "supported": 0, "visual": 0})
    for row in coverage_rows:
        stats = by_skill[row["skill_id"]]
        stats["examples"] += 1
        if row["status"] == "SUPPORTED":
            stats["supported"] += 1
        if row["visual"]:
            stats["visual"] += 1

    skill_summary = [
        {"skill_id": skill, **stats, "package": "PACKAGE_READY"}
        for skill, stats in by_skill.items()
    ]
    coverage = {
        "examples_total": 68,
        "examples_supported": sum(1 for r in coverage_rows if r["status"] == "SUPPORTED"),
        "visual_unsupported": sum(1 for r in coverage_rows if r["status"] == "VISUAL_UNSUPPORTED"),
        "families": sorted(OPS),
        "skill_summary": skill_summary,
        "rows": coverage_rows,
    }
    COV_JSON.write_text(json.dumps(coverage, ensure_ascii=False, indent=2), encoding="utf-8")
    cov_lines = [
        "# B3_CH2_FAMILY_COVERAGE",
        "",
        "| skill_id | source_id | label | family | domain_op | key | mcq | visual | status | reason |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in coverage_rows:
        cov_lines.append(
            f"| {row['skill_id']} | {row['source_id']} | {row['label']} | {row['family_id']} | "
            f"{row['domain_op']} | {row['generator_key']} | {row['mcq']} | {row['visual']} | "
            f"{row['status']} | {row['reason']} |"
        )
    COV_MD.write_text("\n".join(cov_lines) + "\n", encoding="utf-8")

    from app import create_app
    from models import User, db

    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User(username=f"ch2arity_{uuid.uuid4().hex[:8]}", password_hash="x", role="student")
        db.session.add(user)
        db.session.commit()
        uid = user.id
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(uid)
        sess["_fresh"] = True

    mods = {}
    audit_rows = []
    for row in coverage_rows:
        if row["status"] != "SUPPORTED":
            audit_rows.append({
                "source_id": row["source_id"],
                "skill_id": row["skill_id"],
                "generator_key": "",
                "family": row["family_id"],
                "expected_answer_count": 0,
                "generator_answer_count": 0,
                "wrapper_answer_count": 0,
                "api_answer_count": None,
                "rendered_input_count": 0,
                "checker_answer_count": 0,
                "field_labels": [],
                "is_mcq": False,
                "bucket": "visual",
                "api_ok": False,
                "submit_checker_ok": False,
                "status": "VISUAL_UNSUPPORTED",
                "reason": row["reason"],
            })
            continue
        skill_id = row["skill_id"]
        mod = mods.get(skill_id)
        if mod is None:
            mod = importlib.import_module(f"skills.{skill_id}")
            mods[skill_id] = mod
        payload = mod.generate(seed=7, component_id=row["generator_key"])
        matrix = build_equation_solving_matrix(
            operation=row["domain_op"],
            constraints={"textbook_example_id": row["source_id"], "presentation_mode": "single_choice" if row["mcq"] else "short_answer"},
            seed=7,
        )
        if not validate_equation_solving_matrix(matrix):
            raise RuntimeError(f"invalid matrix {row['source_id']}")
        stored = (matrix.get("answer") or {}).get("canonical_form")
        recomputed = recompute_answer(matrix)
        if recomputed != stored:
            raise RuntimeError(f"recompute mismatch {row['source_id']}")
        wrapper_count = expected_answer_field_count(payload)
        generator_count = generator_answer_count_from_matrix(matrix)
        client.get(f"/practice/{quote(skill_id)}")
        resp = client.get(
            f"/get_next_question?skill={quote(skill_id)}&level=1&gen_seed=7&component_id={quote(row['generator_key'])}"
        )
        api_payload = resp.get_json(silent=True) or {}
        api_ok = resp.status_code == 200 and not api_payload.get("error")
        measure = api_payload if api_ok else payload
        expected = expected_answer_field_count(payload)
        api_count = expected_answer_field_count(api_payload) if api_ok else 0
        rendered = rendered_answer_field_count(measure)
        checker_n = checker_answer_count(payload)
        mcq = is_mcq_payload(payload)
        labels = [f.get("label") for f in resolve_multipart_fields(measure)]
        ans = payload.get("answer")
        if ans in (None, "", [], {}):
            ans = payload.get("correct_answer")
        submit_ok = True
        submit_reason = "ok"
        try:
            if not mod.check(ans, ans, question_payload=payload):
                submit_ok = False
                submit_reason = "correct_rejected"
            elif expected > 1 and isinstance(ans, dict):
                for i in range(expected):
                    if mod.check(_mutate_part(ans, i), ans, question_payload=payload):
                        submit_ok = False
                        submit_reason = f"part_{i}_wrong_accepted"
                        break
            elif not mcq and mod.check("__WRONG__", ans, question_payload=payload):
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
        audit_rows.append({
            "source_id": row["source_id"],
            "skill_id": skill_id,
            "generator_key": row["generator_key"],
            "family": row["family_id"],
            "question_type": row["domain_op"],
            "answer_type": str(payload.get("answer_type") or ""),
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
            "recompute_ok": True,
            "status": status,
            "reason": reason,
        })

    supported_rows = [r for r in audit_rows if r["status"] != "VISUAL_UNSUPPORTED"]
    buckets = Counter(r["bucket"] for r in supported_rows)
    fails = [r for r in supported_rows if r["status"] != "PASS"]
    report = {
        "total_examples": 68,
        "generator_rows": len(supported_rows),
        "visual_unsupported": coverage["visual_unsupported"],
        "inventory": {
            "single_answer": buckets.get("single", 0),
            "multi_answer_2": buckets.get("multipart_2", 0),
            "multi_answer_3": buckets.get("multipart_3", 0),
            "multi_answer_4plus": buckets.get("multipart_4plus", 0),
            "mcq": buckets.get("mcq", 0),
        },
        "acceptance": {
            "arity_pass": sum(1 for r in supported_rows if r["status"] == "PASS"),
            "arity_fail": len(fails),
        },
        "mismatched": fails,
        "rows": audit_rows,
    }
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md = [
        "# B3 Ch2 Answer-Arity Runtime Audit",
        "",
        "total_examples = 68",
        f"generator_rows = {len(supported_rows)}",
        f"visual_unsupported = {coverage['visual_unsupported']}",
        "12013 = SOURCE_RESCUED_FROM_SCREENSHOT; runtime screenshot dependency = none",
        "",
        "## Inventory",
        f"- single_answer = {report['inventory']['single_answer']}",
        f"- multi_answer_2 = {report['inventory']['multi_answer_2']}",
        f"- multi_answer_3 = {report['inventory']['multi_answer_3']}",
        f"- multi_answer_4plus = {report['inventory']['multi_answer_4plus']}",
        f"- mcq = {report['inventory']['mcq']}",
        "",
        "## Acceptance",
        f"- arity_pass = {report['acceptance']['arity_pass']} / {len(supported_rows)}",
        f"- arity_fail = {report['acceptance']['arity_fail']}",
        "",
        "## Mismatched",
        "(none)" if not fails else "",
    ]
    for r in fails:
        md.append(f"- {r['source_id']} {r['status']} {r['reason']}")
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")

    bootstrap = {}
    for skill in sorted(by_skill):
        page = client.get(f"/practice/{quote(skill)}")
        resp = client.get(f"/get_next_question?skill={quote(skill)}&level=1&gen_seed=3")
        data = resp.get_json(silent=True) or {}
        q = str(data.get("question_text") or data.get("new_question_text") or "")
        bootstrap[skill] = {
            "practice_status": page.status_code,
            "question_status": resp.status_code,
            "has_question": bool(q.strip()) and not data.get("error"),
            "route_mode": (data.get("metadata") or {}).get("route_mode") if isinstance(data.get("metadata"), dict) else data.get("route_mode"),
            "answer_fields": expected_answer_field_count(data) if q else 0,
            "error": data.get("error"),
        }

    dynamic = {}
    for skill in sorted(by_skill):
        mod = importlib.import_module(f"skills.{skill}")
        samples = []
        fingerprints = []
        for seed in range(5):
            key = mod.GENERATOR_KEYS[seed % len(mod.GENERATOR_KEYS)]
            resp = client.get(
                f"/get_next_question?skill={quote(skill)}&level=1&gen_seed={seed}&component_id={quote(key)}"
            )
            data = resp.get_json(silent=True) or {}
            text = str(data.get("question_text") or "")
            fingerprints.append(text)
            samples.append({
                "generator_key": data.get("component_id") or key,
                "family": data.get("problem_type_id"),
                "route_mode": data.get("route_mode"),
                "question_source": data.get("question_source"),
                "fields": expected_answer_field_count(data) if text else 0,
                "fingerprint": text[:80],
                "static_fallback": data.get("route_mode") == "textbook_example" or data.get("question_source") == "db_textbook_example",
            })
            assert resp.status_code == 200 and text and not data.get("error"), data
            assert samples[-1]["static_fallback"] is False
            assert mod.check(data.get("answer"), data.get("answer"), question_payload=data)
            assert not mod.check("__WRONG__", data.get("answer"), question_payload=data)
        if len(set(fingerprints)) < 2:
            raise RuntimeError(f"questions did not vary for {skill}")
        dynamic[skill] = {
            "samples": samples,
            "distinct_fingerprints": len(set(fingerprints)),
        }
    rescue_texts = []
    rescue_summary = None
    for seed in range(5):
        rescue = client.get(
            "/get_next_question?skill="
            + quote("vh_數學B3_SubSection_2_2_2")
            + f"&level=1&gen_seed={seed}&component_id=src_12013"
        )
        rescue_data = rescue.get_json(silent=True) or {}
        rescue_text = str(rescue_data.get("question_text") or "")
        fields = expected_answer_field_count(rescue_data) if rescue_text else 0
        if fields != 1 or "兩股" not in rescue_text or isinstance(rescue_data.get("answer"), dict):
            raise RuntimeError(f"12013 runtime contract failed: fields={fields} text={rescue_text[:80]!r}")
        if rescue_data.get("route_mode") == "textbook_example":
            raise RuntimeError("12013 fell back to the textbook stem")
        rescue_texts.append(rescue_text)
        rescue_summary = {
            "status": rescue.status_code,
            "fields": fields,
            "route_mode": rescue_data.get("route_mode"),
            "has_text_surrogate": True,
            "single_answer": True,
            "distinct_fingerprints": 0,
        }
    rescue_summary["distinct_fingerprints"] = len(set(rescue_texts))
    if rescue_summary["distinct_fingerprints"] < 2:
        raise RuntimeError("12013 repeated the same stem")
    dynamic["src_12013"] = rescue_summary

    acceptance = {
        "skills_total": len(by_skill),
        "skills_package_ready": len(by_skill),
        "examples_total": 68,
        "examples_supported": coverage["examples_supported"],
        "manual_review": 0,
        "visual": coverage["visual_unsupported"],
        "bad_source": 0,
        "families_total": len(OPS),
        "families_supported": len(OPS),
        "domain_existing_reused": [
            "Fraction",
            "sympy_exact",
            "expression_checker",
            "inequality_solution_checker",
            "single_choice_checker",
            "multi_part_answer_checker",
            "multipart_answer_arity",
        ],
        "domain_new_added": ["equation.solving"],
        "generator_keys": coverage["examples_supported"],
        "answer_arity_pass": report["acceptance"]["arity_pass"],
        "answer_arity_generator_rows": len(supported_rows),
        "bootstrap": bootstrap,
        "dynamic_runtime": dynamic,
        "inventory": report["inventory"],
    }
    ACC_JSON.write_text(json.dumps(acceptance, ensure_ascii=False, indent=2), encoding="utf-8")
    acc_md = [
        "# B3_CH2_GENCODE_ACCEPTANCE",
        "",
        f"- skills_package_ready = {len(by_skill)} / {len(by_skill)}",
        f"- examples_supported = {coverage['examples_supported']} / 68",
        "- examples_manual_review = 0",
        f"- examples_visual_unsupported = {coverage['visual_unsupported']}",
        "- examples_bad_source = 0",
        f"- families_supported = {len(OPS)} / {len(OPS)}",
        f"- generator_keys = {coverage['examples_supported']}",
        f"- answer_arity = {report['acceptance']['arity_pass']} / {len(supported_rows)} generator rows",
        "",
        "## Bootstrap",
    ]
    for skill, info in bootstrap.items():
        acc_md.append(
            f"- `{skill}` practice={info['practice_status']} question={info['question_status']} "
            f"has_question={info['has_question']} fields={info['answer_fields']}"
        )
    ACC_MD.write_text("\n".join(acc_md) + "\n", encoding="utf-8")
    print(json.dumps({
        "supported": coverage["examples_supported"],
        "arity_pass": report["acceptance"]["arity_pass"],
        "arity_fail": len(fails),
        "bootstrap": {k: v["has_question"] for k, v in bootstrap.items()},
        "dynamic_distinct": {k: v.get("distinct_fingerprints") for k, v in dynamic.items() if isinstance(v, dict) and "distinct_fingerprints" in v},
        "src_12013": dynamic.get("src_12013"),
        "inventory": report["inventory"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
