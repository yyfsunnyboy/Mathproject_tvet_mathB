# -*- coding: utf-8 -*-
"""B2 1-1 live / test-client runtime smoke. Does not rebuild components."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SKILLS = {
    "vh_數學B2_AngleMeasurementAndConversion": [
        "src_11606",
        "src_11607",
        "src_11616",
        "src_11617",
        "src_11618",
    ],
    "vh_數學B2_ArcLengthAndAreaOfSector": [
        "src_11608",
        "src_11609",
        "src_11610",
        "src_11619",
        "src_11620",
        "src_11624",
        "src_11625",
    ],
    "vh_數學B2_CoterminalAngles": [
        "src_11611",
        "src_11612",
        "src_11613",
        "src_11614",
        "src_11615",
        "src_11621",
        "src_11622",
        "src_11623",
    ],
}
LIVE = "http://127.0.0.1:5000"
FALLBACK = {"legacy", "legacy_skill", "db_fallback", "db_textbook_example"}


def _canonical(payload: dict):
    ac = payload.get("answer_contract") if isinstance(payload.get("answer_contract"), dict) else {}
    parts = ac.get("parts") if isinstance(ac.get("parts"), list) else []
    if parts:
        return {str(p.get("key") or p.get("field_key")): p.get("expected_answer") for p in parts}
    blanks = ((payload.get("table_question") or payload.get("table_data") or {}).get("blank_cells") or [])
    if isinstance(blanks, list) and blanks:
        return {str(b.get("field_key")): b.get("expected_answer") for b in blanks if isinstance(b, dict)}
    if isinstance(payload.get("answer"), dict):
        return payload["answer"]
    return payload.get("answer") or payload.get("canonical_answer") or payload.get("correct_answer")


def _wrong(canonical):
    if isinstance(canonical, dict):
        return {k: ("pi/999" if "pi" in str(v or "").lower() else "999") for k, v in canonical.items()}
    s = str(canonical or "")
    return "pi/999" if "pi" in s.lower() else "999"


def live_practice_status(skill_id: str) -> int:
    url = f"{LIVE}/practice/{quote(skill_id)}"
    req = Request(url, method="GET")
    with urlopen(req, timeout=20) as resp:
        return int(resp.status)


def main() -> None:
    from app import create_app
    from models import User

    errors: list[str] = []
    live_http = {}
    for skill_id in SKILLS:
        try:
            live_http[skill_id] = live_practice_status(skill_id)
            if live_http[skill_id] != 200:
                errors.append(f"{skill_id}:live_http_{live_http[skill_id]}")
        except Exception as exc:
            live_http[skill_id] = f"EXC:{exc}"
            errors.append(f"{skill_id}:live_exc:{exc}")

    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User.query.order_by(User.id.asc()).first()
        user_id = str(user.id) if user else ""
    if not user_id:
        errors.append("no_user_for_login")

    hits: dict[str, dict[str, int]] = {sid: {cid: 0 for cid in cids} for sid, cids in SKILLS.items()}
    route_sources: dict[str, int] = {}
    http_500 = 0
    fallback = 0
    table_ok = False

    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["_user_id"] = user_id
            sess["_fresh"] = True
        for skill_id, cids in SKILLS.items():
            page = client.get(f"/practice/{quote(skill_id)}")
            if page.status_code != 200:
                errors.append(f"{skill_id}:client_practice_{page.status_code}")
            if page.status_code >= 500:
                http_500 += 1
            for extra in range(12):
                resp = client.get(
                    f"/get_next_question?skill={quote(skill_id)}&level=1&gen_seed={200 + extra}"
                )
                if resp.status_code >= 500:
                    http_500 += 1
                    errors.append(f"{skill_id}:random_http_{resp.status_code}")
                    continue
                if resp.status_code != 200:
                    errors.append(f"{skill_id}:random_http_{resp.status_code}")
                    continue
                data = resp.get_json(silent=True) or {}
                src = str(data.get("route_source") or data.get("source") or data.get("question_source") or "")
                route_sources[src] = route_sources.get(src, 0) + 1
                if src in FALLBACK:
                    fallback += 1
                    errors.append(f"{skill_id}:random_fallback:{src}")
                got = str(data.get("component_id") or "")
                if got in hits[skill_id]:
                    hits[skill_id][got] += 1

            for seed, cid in enumerate(cids, start=1):
                url = (
                    f"/get_next_question?skill={quote(skill_id)}"
                    f"&level=1&gen_seed={seed}&component_id={cid}"
                )
                resp = client.get(url)
                if resp.status_code >= 500:
                    http_500 += 1
                    errors.append(f"{cid}:get_http_{resp.status_code}")
                    continue
                if resp.status_code != 200:
                    errors.append(f"{cid}:get_http_{resp.status_code}")
                    continue
                data = resp.get_json(silent=True) or {}
                src = str(data.get("route_source") or data.get("source") or data.get("question_source") or "")
                route_sources[src] = route_sources.get(src, 0) + 1
                if src in FALLBACK:
                    fallback += 1
                    errors.append(f"{cid}:fallback:{src}")
                got = str(data.get("component_id") or "")
                if got == cid:
                    hits[skill_id][cid] += 1
                else:
                    errors.append(f"{cid}:got_{got}")
                if cid == "src_11616":
                    tq = data.get("table_question") if isinstance(data.get("table_question"), dict) else {}
                    td = data.get("table_data") if isinstance(data.get("table_data"), dict) else {}
                    blanks = tq.get("blank_cells") or td.get("blank_cells") or []
                    ac = data.get("answer_contract") if isinstance(data.get("answer_contract"), dict) else {}
                    cells_ok = bool(blanks) and all(
                        {"row", "col", "field_key"} <= set(b) for b in blanks if isinstance(b, dict)
                    )
                    table_ok = (
                        str(data.get("presentation_mode") or "") == "inline_table_input"
                        and str(ac.get("answer_type") or data.get("answer_type") or "") == "table_fill"
                        and str(data.get("checker") or data.get("checker_key") or ac.get("checker") or "")
                        == "table_fill_checker"
                        and cells_ok
                    )
                    if not table_ok:
                        errors.append("11616_table_fill_http_contract_fail")
                canon = _canonical(data)
                body_ok = {
                    "skill_id": skill_id,
                    "question_uid": data.get("question_uid"),
                    "problem_type_id": data.get("problem_type_id") or data.get("problem_type"),
                    "answer": canon,
                }
                chk = client.post("/check_answer", json=body_ok)
                if chk.status_code >= 500:
                    http_500 += 1
                    errors.append(f"{cid}:check_ok_http_{chk.status_code}")
                else:
                    payload = chk.get_json(silent=True) or {}
                    if not payload.get("correct"):
                        errors.append(f"{cid}:canonical_http_fail")
                # Fresh question so the second POST is not a duplicate_submission cache hit.
                resp_bad = client.get(
                    f"/get_next_question?skill={quote(skill_id)}"
                    f"&level=1&gen_seed={seed + 100}&component_id={cid}"
                )
                if resp_bad.status_code >= 500:
                    http_500 += 1
                    errors.append(f"{cid}:get_wrong_http_{resp_bad.status_code}")
                    continue
                data_bad = resp_bad.get_json(silent=True) or {}
                src_bad = str(
                    data_bad.get("route_source")
                    or data_bad.get("source")
                    or data_bad.get("question_source")
                    or ""
                )
                route_sources[src_bad] = route_sources.get(src_bad, 0) + 1
                if src_bad in FALLBACK:
                    fallback += 1
                    errors.append(f"{cid}:fallback_wrong:{src_bad}")
                chk_bad = client.post(
                    "/check_answer",
                    json={
                        "skill_id": skill_id,
                        "question_uid": data_bad.get("question_uid"),
                        "problem_type_id": data_bad.get("problem_type_id") or data_bad.get("problem_type"),
                        "answer": _wrong(_canonical(data_bad)),
                    },
                )
                if chk_bad.status_code >= 500:
                    http_500 += 1
                    errors.append(f"{cid}:check_bad_http_{chk_bad.status_code}")
                else:
                    payload = chk_bad.get_json(silent=True) or {}
                    if payload.get("correct"):
                        errors.append(f"{cid}:wrong_http_accepted")
                    elif payload.get("duplicate_submission"):
                        errors.append(f"{cid}:wrong_duplicate_cache")

    missing = [cid for sid, cmap in hits.items() for cid, n in cmap.items() if n == 0]
    if missing:
        errors.append(f"unsampled_http:{missing}")

    out = {
        "live_http": live_http,
        "route_sources": route_sources,
        "hits": hits,
        "http_500": http_500,
        "fallback": fallback,
        "table_fill_11616": table_ok,
        "errors": errors[:40],
        "ok": not errors and http_500 == 0 and fallback == 0,
        "runtime_http_200": all(v == 200 for v in live_http.values()),
        "old_generator_fallback": fallback > 0 or any(
            s in FALLBACK for s in route_sources
        ),
    }
    path = ROOT / "scratch" / "_b2_1_1_runtime_http_smoke.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2, default=str)[:8000])


if __name__ == "__main__":
    main()
