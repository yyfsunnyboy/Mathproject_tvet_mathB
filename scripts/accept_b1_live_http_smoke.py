# -*- coding: utf-8 -*-
"""Live HTTP smoke against Flask 5001 after controlled restart.

Creates a traceable audit student on the formal DB, exercises student routes,
and records evidence. Does not delete history.
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
USER = f"b1_live_audit_{STAMP}"
PASS = f"audit-{STAMP}-x"


def _ensure_user() -> int:
    con = sqlite3.connect(str(DB))
    try:
        con.execute(
            "INSERT INTO users (username, password_hash, role, email) VALUES (?, ?, 'student', ?)",
            (
                USER,
                generate_password_hash(PASS, method="pbkdf2:sha256"),
                f"{USER}@audit.local",
            ),
        )
        con.commit()
        uid = con.execute("SELECT id FROM users WHERE username=?", (USER,)).fetchone()[0]
        return int(uid)
    finally:
        con.close()


def _login(session: requests.Session) -> bool:
    # Fetch login page for CSRF cookie if any
    session.get(f"{BASE}/login", timeout=20)
    # Try common form fields
    for payload in (
        {"username": USER, "password": PASS},
        {"username": USER, "password": PASS, "submit": "Login"},
    ):
        r = session.post(f"{BASE}/login", data=payload, timeout=20, allow_redirects=True)
        # Authenticated practice returns JSON 200 rather than login HTML
        probe = session.get(
            f"{BASE}/get_next_question",
            params={"skill": "vh_數學B1_SlopeOfALine", "level": 1, "component_id": "src_4519", "seed": 3},
            timeout=30,
        )
        if probe.status_code == 200 and isinstance(probe.json(), dict) and probe.json().get("question_uid"):
            return True
        if r.status_code >= 500:
            break
    return False


def _session_current_answer(session: requests.Session):
    """Read server-side oracle from signed Flask session cookie (not from student JSON)."""
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


def _check_skill(session: requests.Session, skill_id: str, component_id: str, seed: int) -> dict:
    res = session.get(
        f"{BASE}/get_next_question",
        params={"skill": skill_id, "level": 1, "component_id": component_id, "seed": seed},
        timeout=40,
    )
    data = res.json() if res.headers.get("content-type", "").startswith("application/json") else {}
    out = {
        "skill_id": skill_id,
        "component_id": component_id,
        "http_generate": res.status_code,
        "generate": "FAIL",
        "checker": "SKIP",
        "problem_type_id": data.get("problem_type_id"),
        "question_uid": data.get("question_uid"),
        "notes": [],
    }
    q = str(data.get("question") or data.get("question_text") or "").strip()
    if res.status_code != 200 or not q or not data.get("question_uid"):
        out["notes"].append(f"generate_body_keys={list(data.keys())[:12]}")
        return out
    out["generate"] = "PASS"

    answer = data.get("semantic_answer") or data.get("correct_answer") or data.get("answer")
    if answer is None or (isinstance(answer, str) and not str(answer).strip()):
        answer = _session_current_answer(session)
        out["notes"].append("oracle_from_flask_session_cookie")
    if answer is None or (isinstance(answer, str) and not str(answer).strip()):
        out["checker"] = "FAIL"
        out["notes"].append("no_oracle")
        return out

    check_payload = {"skill_id": skill_id, "question_uid": data["question_uid"], "answer": answer}
    if isinstance(answer, dict):
        check_payload["answers"] = answer
    chk = session.post(f"{BASE}/check_answer", json=check_payload, timeout=40)
    body = chk.json() if chk.headers.get("content-type", "").startswith("application/json") else {}
    ok = bool(body.get("correct") or body.get("all_correct") or body.get("is_correct"))
    if chk.status_code == 200 and ok:
        out["checker"] = "PASS"
        out["notes"].append("correct_accepted")
    else:
        out["checker"] = "FAIL"
        out["notes"].append(
            f"check_status={chk.status_code} correct={body.get('correct')} invalid={body.get('invalid_input')}"
        )

    # Wrong answer must be rejected on a fresh question.
    res2 = session.get(
        f"{BASE}/get_next_question",
        params={"skill": skill_id, "level": 1, "component_id": component_id, "seed": seed + 11},
        timeout=40,
    )
    data2 = res2.json() if res2.ok else {}
    uid2 = data2.get("question_uid")
    if uid2:
        bad = session.post(
            f"{BASE}/check_answer",
            json={"skill_id": skill_id, "question_uid": uid2, "answer": "__definitely_wrong__"},
            timeout=40,
        )
        bad_body = bad.json() if bad.ok else {}
        if bad_body.get("correct") or bad_body.get("all_correct"):
            out["notes"].append("wrong_answer_accepted")
            out["checker"] = "FAIL"
        else:
            out["notes"].append("wrong_answer_rejected")
    return out


def main() -> int:
    health = requests.get(f"{BASE}/healthz", timeout=10).json()
    uid = _ensure_user()
    session = requests.Session()
    logged_in = _login(session)
    results = []
    if logged_in:
        for skill, comp, seed in (
            ("vh_數學B1_QuadraticInequalitySolution", "src_4474", 17),
            ("vh_數學B1_DistanceBetweenPointAndLine", "src_4584", 19),
            ("vh_數學B1_DistanceBetweenTwoParallelLines", "src_4570", 21),
            ("vh_數學B1_SlopeOfALine", "src_4519", 23),
        ):
            results.append(_check_skill(session, skill, comp, seed))
    payload = {
        "generated_at": STAMP,
        "healthz": health,
        "test_username": USER,
        "test_user_id": uid,
        "logged_in": logged_in,
        "results": results,
        "note": "Traceable audit student left on formal DB; practice attempts may exist for this username only.",
    }
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"b1_live_http_smoke_{STAMP}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "b1_live_http_smoke_latest.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({"wrote": str(path), "logged_in": logged_in, "healthz": health, "results": results}, ensure_ascii=False, indent=2))
    return 0 if logged_in and all(r.get("generate") == "PASS" for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
