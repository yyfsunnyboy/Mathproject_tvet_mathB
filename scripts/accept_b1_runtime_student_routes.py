# -*- coding: utf-8 -*-
"""B1 student-route Runtime acceptance on an isolated DB copy.

Does NOT write the formal kumon_math.db. Copies formal DB → tmp, then drives
/get_next_question + /check_answer via Flask test_client.
"""
from __future__ import annotations

import json
import os
import shutil
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROD_DB = ROOT / "instance" / "kumon_math.db"
OUT_DIR = ROOT / "reports" / "gencode_closed_loop"
STAMP = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
ISO_DIR = ROOT / "tmp" / f"b1_runtime_accept_{STAMP}"
ISO_DB = ISO_DIR / "kumon_math_accept.db"

# Priority + representative skills for full answer-check; others generate-only sample.
PRIORITY_CHECK = {
    "vh_數學B1_QuadraticInequalitySolution",
    "vh_數學B1_DistanceBetweenPointAndLine",
    "vh_數學B1_DistanceBetweenTwoParallelLines",
    "vh_數學B1_SlopeOfALine",
    "vh_數學B1_SlopeInterceptForm",
}
FORCE_COMPONENT = {
    "vh_數學B1_DistanceBetweenPointAndLine": "src_4584",
    "vh_數學B1_QuadraticInequalitySolution": "src_4474",
    "vh_數學B1_SlopeOfALine": "src_4519",
    "vh_數學B1_SlopeInterceptForm": "src_4603",
}


def _is_correct(body: dict | None) -> bool:
    if not isinstance(body, dict):
        return False
    return bool(body.get("correct") or body.get("all_correct") or body.get("is_correct"))


def _load_b1_skills(db: Path) -> list[dict]:
    con = sqlite3.connect(str(db))
    con.row_factory = sqlite3.Row
    rows = con.execute(
        """
        SELECT skill_id, skill_ch_name, is_active, category
        FROM skills_info
        WHERE skill_id LIKE 'vh_數學B1_%' OR skill_id LIKE 'outline_vocational_數學B1_%'
        ORDER BY skill_id
        """
    ).fetchall()
    con.close()
    out = []
    for r in rows:
        item = dict(r)
        item["is_outline"] = str(item.get("skill_id") or "").startswith("outline_")
        out.append(item)
    return out


def main() -> int:
    if not PROD_DB.exists():
        print("FAIL: formal DB missing")
        return 2
    ISO_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PROD_DB, ISO_DB)
    uri = f"sqlite:///{ISO_DB.as_posix()}"
    os.environ["MATHPROJECT_DATABASE_URI"] = uri

    # Import app only after URI override.
    sys.path.insert(0, str(ROOT))
    import config as app_config

    app_config.Config.SQLALCHEMY_DATABASE_URI = uri
    from app import create_app
    from models import User, db
    from werkzeug.security import generate_password_hash

    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = uri

    username = f"b1_audit_probe_{STAMP}"
    with app.app_context():
        user = User(
            username=username,
            password_hash=generate_password_hash("audit-only-not-for-login"),
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        user_id = str(user.id)

    skills = _load_b1_skills(ISO_DB)
    results: list[dict] = []
    summary = {
        "skills_total": len(skills),
        "executable_attempted": 0,
        "generate_pass": 0,
        "generate_fail": 0,
        "checker_pass": 0,
        "checker_fail": 0,
        "checker_skipped": 0,
        "outline_skipped": 0,
        "zero_generator_skipped": 0,
    }

    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["_user_id"] = user_id
            sess["_fresh"] = True

        for sk in skills:
            sid = sk["skill_id"]
            row: dict = {
                "skill_id": sid,
                "skill_ch_name": sk.get("skill_ch_name"),
                "is_outline": bool(sk.get("is_outline")),
                "is_active": bool(sk.get("is_active")),
                "generate": "SKIP",
                "checker": "SKIP",
                "component_id": None,
                "problem_type_id": None,
                "route_source": None,
                "notes": [],
            }
            if sk.get("is_outline"):
                summary["outline_skipped"] += 1
                row["notes"].append("outline")
                results.append(row)
                continue

            # Probe module for keys
            try:
                mod = __import__(f"skills.{sid}", fromlist=["*"])
            except Exception as exc:  # noqa: BLE001
                row["generate"] = "FAIL"
                row["notes"].append(f"import_error:{exc}")
                summary["generate_fail"] += 1
                summary["executable_attempted"] += 1
                results.append(row)
                continue

            keys = list(getattr(mod, "GENERATOR_KEYS", []) or [])
            specs = list(getattr(mod, "GENERATOR_SPECS", []) or [])
            if not keys and specs:
                keys = [str(s.get("component_id") or s.get("generator_key") or "") for s in specs]
                keys = [k for k in keys if k]
            if not keys:
                summary["zero_generator_skipped"] += 1
                row["notes"].append("no_generator_keys")
                results.append(row)
                continue

            summary["executable_attempted"] += 1
            component_id = FORCE_COMPONENT.get(sid) or keys[0]
            if FORCE_COMPONENT.get(sid) and FORCE_COMPONENT[sid] not in keys:
                row["notes"].append(f"forced_component_missing:{FORCE_COMPONENT[sid]}")
                component_id = keys[0]
            row["component_id"] = component_id

            res = client.get(
                "/get_next_question",
                query_string={
                    "skill": sid,
                    "level": 1,
                    "component_id": component_id,
                    "seed": 42,
                },
            )
            data = res.get_json(silent=True) or {}
            if res.status_code != 200 or not data:
                row["generate"] = "FAIL"
                row["notes"].append(f"http_{res.status_code}")
                summary["generate_fail"] += 1
                results.append(row)
                continue

            q = str(data.get("question") or data.get("question_text") or "").strip()
            uid = data.get("question_uid")
            pt = data.get("problem_type_id")
            got_comp = (data.get("metadata") or {}).get("component_id") or data.get("component_id")
            route = (
                (data.get("metadata") or {}).get("resolved_route_source")
                or (data.get("metadata") or {}).get("route_source")
                or data.get("route_source")
            )
            row["problem_type_id"] = pt
            row["route_source"] = route
            if got_comp:
                row["component_id"] = got_comp
            if not q or not uid:
                row["generate"] = "FAIL"
                row["notes"].append("empty_question_or_uid")
                summary["generate_fail"] += 1
                results.append(row)
                continue

            # Refuse accidental ParallelLines binding for src_4584
            if component_id == "src_4584" and "Parallel" in sid:
                row["generate"] = "FAIL"
                row["notes"].append("src_4584_on_parallel")
                summary["generate_fail"] += 1
                results.append(row)
                continue

            row["generate"] = "PASS"
            summary["generate_pass"] += 1

            # Student JSON intentionally strips answers; oracle lives in practice_question_store.
            from core.practice_question_store import _STORE

            stored = None
            for rows in _STORE.values():
                if uid in rows:
                    stored = rows[uid]
                    break
            answer = None
            if isinstance(stored, dict):
                answer = stored.get("semantic_answer")
                if answer is None:
                    answer = stored.get("correct_answer")
                if answer is None:
                    answer = stored.get("answer")
                meta = stored.get("metadata") or {}
                if answer is None:
                    answer = meta.get("semantic_answer")
            if answer is None or (isinstance(answer, str) and not str(answer).strip()):
                # Fallback: session cookie current_answer (server-side only).
                with client.session_transaction() as sess:
                    answer = sess.get("current_answer")
            if answer is None or (isinstance(answer, str) and not str(answer).strip()):
                row["checker"] = "FAIL"
                row["notes"].append("no_server_side_oracle")
                summary["checker_fail"] += 1
                results.append(row)
                continue
            row["notes"].append("oracle_from_store" if stored else "oracle_from_session")

            check_payload: dict = {
                "skill_id": sid,
                "question_uid": uid,
                "answer": answer,
            }
            # Only send plural ``answers`` for structured multi-part payloads.
            # A present ``answers: null`` key would shadow ``answer`` in the route.
            if isinstance(answer, dict):
                check_payload["answers"] = answer
            check = client.post("/check_answer", json=check_payload)
            body = check.get_json(silent=True) or {}
            if check.status_code == 200 and _is_correct(body):
                row["checker"] = "PASS"
                summary["checker_pass"] += 1
            else:
                row["checker"] = "FAIL"
                row["notes"].append(f"check_status={check.status_code} body_keys={list(body.keys())[:8]}")
                summary["checker_fail"] += 1

            # Wrong-answer probe for priority skills only (avoid long runs).
            if sid in PRIORITY_CHECK and row["checker"] == "PASS":
                wrong = "__definitely_wrong__"
                if isinstance(answer, (int, float)) or (isinstance(answer, str) and str(answer).lstrip("-").isdigit()):
                    try:
                        wrong = str(int(str(answer).strip()) + 99)
                    except Exception:  # noqa: BLE001
                        wrong = "__definitely_wrong__"
                elif isinstance(answer, dict):
                    wrong = {k: "__wrong__" for k in answer}
                # Need a fresh question_uid for second check (session stores one).
                res2 = client.get(
                    "/get_next_question",
                    query_string={
                        "skill": sid,
                        "level": 1,
                        "component_id": component_id,
                        "seed": 99,
                    },
                )
                data2 = res2.get_json(silent=True) or {}
                uid2 = data2.get("question_uid")
                if uid2:
                    bad_payload: dict = {"skill_id": sid, "question_uid": uid2, "answer": wrong}
                    if isinstance(wrong, dict):
                        bad_payload["answers"] = wrong
                    bad = client.post("/check_answer", json=bad_payload)
                    bad_body = bad.get_json(silent=True) or {}
                    if _is_correct(bad_body):
                        row["notes"].append("wrong_answer_accepted")
                        row["checker"] = "FAIL"
                        summary["checker_pass"] -= 1
                        summary["checker_fail"] += 1
                    else:
                        row["notes"].append("wrong_answer_rejected")

            results.append(row)

    payload = {
        "generated_at": STAMP,
        "isolated_db": str(ISO_DB),
        "test_username": username,
        "summary": summary,
        "results": results,
        "priority": sorted(PRIORITY_CHECK),
        "src_4584": next((r for r in results if r.get("component_id") == "src_4584"), None),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"b1_runtime_student_route_accept_{STAMP}.json"
    latest = OUT_DIR / "b1_runtime_student_route_accept_latest.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    latest.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", out)
    print("summary", json.dumps(summary, ensure_ascii=False))
    fails = [r for r in results if r.get("generate") == "FAIL" or r.get("checker") == "FAIL"]
    print("fails", len(fails))
    for r in fails[:20]:
        print(r["skill_id"], r.get("generate"), r.get("checker"), r.get("notes"))
    return 0 if summary["generate_fail"] == 0 and summary["checker_fail"] == 0 else 1


if __name__ == "__main__":
    t0 = time.time()
    code = main()
    print(f"elapsed_s={time.time() - t0:.1f}")
    raise SystemExit(code)
