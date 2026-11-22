# -*- coding: utf-8 -*-
"""B1 final live HTTP acceptance against Flask 5001 after controlled restart.

Focuses on closeout-fixed components. Creates a traceable audit student.
Does not delete history. Does not modify B2–B4.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import requests
from werkzeug.security import generate_password_hash

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "instance" / "kumon_math.db"
OUT = ROOT / "reports" / "gencode_closed_loop"
BASE = "http://127.0.0.1:5001"
STAMP = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
USER = f"b1_final_accept_{STAMP}"
PASS = f"accept-{STAMP}-x"

# Closeout + regression targets only (no full B1 sweep).
TARGETS = [
    ("vh_數學B1_RemainderTheorem", "src_4638", 101, "remainder_symbolic"),
    ("vh_數學B1_RemainderTheorem", "src_4640", 103, "remainder_symbolic"),
    ("vh_數學B1_RemainderTheorem", "src_4664", 105, "remainder_symbolic"),
    ("vh_數學B1_RemainderTheorem", "src_4666", 107, "remainder_symbolic"),
    ("vh_數學B1_QuadraticFunctionExtremum", "src_4457", 111, "farmer_fence"),
    ("vh_數學B1_QuadraticFunctionExtremum", "src_4465", 113, "group_buy_multi"),
    ("vh_數學B1_QuadraticFunctionExtremum", "src_4471", 115, "tour_multi"),
    ("vh_數學B1_QuadraticInequalitySolution", "src_4517", 117, "triangle_mcq"),
    ("vh_數學B1_QuadraticInequalitySolution", "src_4474", 119, "qis_reverse"),
    ("vh_數學B1_QuadraticInequalitySolution", "src_4476", 121, "qis_min_integer"),
    ("vh_數學B1_PointSlopeForm", "src_4542", 123, "perpendicular_bisector"),
    ("vh_數學B1_DistanceBetweenPointAndLine", "src_4584", 125, "point_line_regress"),
]


def _ensure_user() -> int:
    con = sqlite3.connect(str(DB))
    try:
        con.execute(
            "INSERT INTO users (username, password_hash, role, email) VALUES (?, ?, 'student', ?)",
            (USER, generate_password_hash(PASS, method="pbkdf2:sha256"), f"{USER}@audit.local"),
        )
        con.commit()
        return int(con.execute("SELECT id FROM users WHERE username=?", (USER,)).fetchone()[0])
    finally:
        con.close()


def _login(session: requests.Session) -> bool:
    session.get(f"{BASE}/login", timeout=20)
    session.post(f"{BASE}/login", data={"username": USER, "password": PASS}, timeout=20, allow_redirects=True)
    probe = session.get(
        f"{BASE}/get_next_question",
        params={"skill": "vh_數學B1_SlopeOfALine", "level": 1, "component_id": "src_4519", "seed": 3},
        timeout=30,
    )
    if probe.status_code != 200:
        return False
    body = probe.json() if probe.headers.get("content-type", "").startswith("application/json") else {}
    return bool(isinstance(body, dict) and body.get("question_uid"))


def _session_current_answer(session: requests.Session):
    import sys

    sys.path.insert(0, str(ROOT))
    from flask.sessions import SecureCookieSessionInterface
    from app import app as flask_app

    cookie_name = flask_app.config.get("SESSION_COOKIE_NAME", "session")
    raw = session.cookies.get(cookie_name)
    if not raw:
        return None
    interface = SecureCookieSessionInterface()
    serializer = interface.get_signing_serializer(flask_app)
    if serializer is None:
        return None
    try:
        data = serializer.loads(raw)
    except Exception:  # noqa: BLE001
        return None
    return data.get("current_answer")


def _structure_ok(tag: str, data: dict) -> tuple[bool, str]:
    q = str(data.get("question") or data.get("question_text") or "")
    pt = str(data.get("problem_type_id") or "")
    at = str(data.get("answer_type") or "")
    choices = data.get("choices") or []
    if tag == "remainder_symbolic":
        ok = "餘式" in q and "f(x)" in q.replace(" ", "") and (
            "remainder_theorem_state_symbolic" in pt or "f(" in str(data.get("correct_answer") or data.get("answer") or "")
        )
        return ok, f"pt={pt}"
    if tag == "farmer_fence":
        return ("農夫" in q or "籬笆" in q) and "面積" in q, f"pt={pt}"
    if tag == "group_buy_multi":
        return ("團購" in q or "手機" in q) and at in {"multi_part", "multipart"}, f"at={at}"
    if tag == "tour_multi":
        return ("旅行社" in q or "出團" in q) and at in {"multi_part", "multipart"}, f"at={at}"
    if tag == "triangle_mcq":
        return (
            ("直角三角形" in q or "三角形" in q)
            and (at == "choice_label" or str(data.get("presentation_mode") or "") == "single_choice")
            and isinstance(choices, list)
            and len(choices) >= 4
        ), f"at={at} choices={len(choices) if isinstance(choices, list) else 0}"
    if tag == "perpendicular_bisector":
        return "垂直平分" in q or "perpendicular" in pt or "bisector" in pt, f"pt={pt}"
    if tag == "qis_min_integer":
        return ("最少" in q or "開始賺" in q) and at in {"integer", "int"}, f"at={at}"
    return bool(q), f"pt={pt}"


def _check_skill(session: requests.Session, skill_id: str, component_id: str, seed: int, tag: str) -> dict:
    res = session.get(
        f"{BASE}/get_next_question",
        params={"skill": skill_id, "level": 1, "component_id": component_id, "seed": seed},
        timeout=45,
    )
    data = res.json() if res.headers.get("content-type", "").startswith("application/json") else {}
    q = str(data.get("question") or data.get("question_text") or "").strip()
    out = {
        "tag": tag,
        "skill_id": skill_id,
        "component_id": component_id,
        "http_generate": res.status_code,
        "generate": "FAIL",
        "structure": "FAIL",
        "checker_correct": "SKIP",
        "checker_wrong": "SKIP",
        "problem_type_id": data.get("problem_type_id"),
        "answer_type": data.get("answer_type"),
        "presentation_mode": data.get("presentation_mode"),
        "question_uid": data.get("question_uid"),
        "question_preview": q[:120],
        "notes": [],
    }
    if res.status_code != 200 or not q or not data.get("question_uid"):
        out["notes"].append(f"generate_keys={list(data.keys())[:12]}")
        return out
    out["generate"] = "PASS"
    ok_struct, detail = _structure_ok(tag, data)
    out["structure"] = "PASS" if ok_struct else "FAIL"
    out["notes"].append(detail)

    answer = data.get("semantic_answer") or data.get("correct_answer") or data.get("answer")
    if answer is None or (isinstance(answer, str) and not str(answer).strip()):
        answer = _session_current_answer(session)
        out["notes"].append("oracle_from_flask_session_cookie")
    if answer is None or (isinstance(answer, str) and not str(answer).strip()):
        out["checker_correct"] = "FAIL"
        out["notes"].append("no_oracle")
        return out

    check_payload = {"skill_id": skill_id, "question_uid": data["question_uid"], "answer": answer}
    if isinstance(answer, dict):
        check_payload["answers"] = answer
    chk = session.post(f"{BASE}/check_answer", json=check_payload, timeout=45)
    body = chk.json() if chk.headers.get("content-type", "").startswith("application/json") else {}
    ok = bool(body.get("correct") or body.get("all_correct") or body.get("is_correct"))
    out["checker_correct"] = "PASS" if chk.status_code == 200 and ok else "FAIL"
    if out["checker_correct"] != "PASS":
        out["notes"].append(
            f"check_status={chk.status_code} correct={body.get('correct')} body_keys={list(body.keys())[:10]}"
        )

    res2 = session.get(
        f"{BASE}/get_next_question",
        params={"skill": skill_id, "level": 1, "component_id": component_id, "seed": seed + 17},
        timeout=45,
    )
    data2 = res2.json() if res2.ok else {}
    uid2 = data2.get("question_uid")
    if uid2:
        bad = session.post(
            f"{BASE}/check_answer",
            json={"skill_id": skill_id, "question_uid": uid2, "answer": "__definitely_wrong__"},
            timeout=45,
        )
        bad_body = bad.json() if bad.ok else {}
        if bad_body.get("correct") or bad_body.get("all_correct"):
            out["checker_wrong"] = "FAIL"
            out["notes"].append("wrong_answer_accepted")
        else:
            out["checker_wrong"] = "PASS"
            out["notes"].append("wrong_answer_rejected")
    return out


def main() -> int:
    health = requests.get(f"{BASE}/healthz", timeout=10).json()
    uid = _ensure_user()
    session = requests.Session()
    logged_in = _login(session)
    results = []
    if logged_in:
        for skill, comp, seed, tag in TARGETS:
            results.append(_check_skill(session, skill, comp, seed, tag))

    def row_pass(r: dict) -> bool:
        return (
            r.get("generate") == "PASS"
            and r.get("structure") == "PASS"
            and r.get("checker_correct") == "PASS"
            and r.get("checker_wrong") == "PASS"
        )

    summary = {
        "PASS": sum(1 for r in results if row_pass(r)),
        "FAIL": sum(1 for r in results if not row_pass(r)),
        "total": len(results),
    }
    payload = {
        "generated_at": STAMP,
        "healthz": health,
        "test_username": USER,
        "test_user_id": uid,
        "logged_in": logged_in,
        "summary": summary,
        "results": results,
        "note": "Traceable audit student left on formal DB; practice attempts may exist for this username only.",
    }
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"b1_final_live_http_{STAMP}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "b1_final_live_http_latest.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({"wrote": str(path), "logged_in": logged_in, "healthz": health, "summary": summary}, ensure_ascii=False, indent=2))
    for r in results:
        mark = "PASS" if row_pass(r) else "FAIL"
        print(f"[{mark}] {r['tag']} {r['component_id']} gen={r['generate']} struct={r['structure']} ok={r['checker_correct']} bad={r['checker_wrong']} | {r.get('question_preview','')[:70]}")
    return 0 if logged_in and summary["FAIL"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
