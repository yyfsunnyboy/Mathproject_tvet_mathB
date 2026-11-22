# -*- coding: utf-8 -*-
"""Regression for PointSlopeForm perpendicular-bisector fidelity fix."""
from __future__ import annotations

import importlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "gencode_closed_loop"
STAMP = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
SKILL = "vh_數學B1_PointSlopeForm"


def _ok(r) -> bool:
    return bool(r.get("correct") if isinstance(r, dict) else r)


def offline() -> dict:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    for n in list(sys.modules):
        if SKILL in n or n in {"core.gencode.slot_generators", "core.practice_type_rotation"}:
            del sys.modules[n]
    mod = importlib.import_module(f"skills.{SKILL}")
    from core.practice_type_rotation import resolve_type_key

    types: dict[str, list[str]] = {}
    for s in mod.GENERATOR_SPECS:
        k, _ = resolve_type_key(s)
        types.setdefault(k, []).append(str(s.get("component_id")))

    rows = []
    # basic point-slope still works
    p0 = mod.generate(level=1, seed=3, component_id="src_4540")
    a0 = p0.get("correct_answer") or p0.get("answer")
    rows.append(
        {
            "case": "basic_point_slope",
            "component_id": "src_4540",
            "problem_type_id": p0.get("problem_type_id"),
            "self_check": _ok(mod.check(a0, a0, p0)),
            "wrong_rejected": not _ok(mod.check("x=0", a0, p0)),
            "has_bisector_token": "垂直平分" in str(p0.get("question") or p0.get("question_text") or ""),
        }
    )
    for cid, seed in (("src_4542", 14), ("src_4557", 2), ("src_4550", 9)):
        p = mod.generate(level=1, seed=seed, component_id=cid)
        q = str(p.get("question") or p.get("question_text") or "")
        ans = p.get("correct_answer") or p.get("answer")
        # equivalent scaled form
        equiv_ok = False
        if isinstance(ans, str) and "x" in ans and "= 0" in ans:
            # try doubling if integer coeffs present
            try:
                from sympy import Eq, simplify
                from sympy.parsing.sympy_parser import parse_expr

                left = ans.replace("= 0", "").replace("=", "-(") + ")" if False else None
            except Exception:
                left = None
            # simple: multiply by 2 when all terms look integer-ish
            doubled = None
            if ans.endswith("= 0"):
                body = ans[:-4].strip()
                # crude: prepend 2*(...) not reliable; use known checker with alternate general form
                doubled = None
            # Use checker with flipped sign form -A -B -C = 0
            if ans.endswith("= 0"):
                body = ans[:-4].strip()
                # replace leading terms by negating via multiplying -1: swap signs manually for common patterns
                alt = f"-({body}) = 0"
                equiv_ok = _ok(mod.check(alt, ans, p))
        rows.append(
            {
                "case": "bisector",
                "component_id": cid,
                "problem_type_id": p.get("problem_type_id"),
                "question_preview": q[:100],
                "answer": ans,
                "self_check": _ok(mod.check(ans, ans, p)),
                "wrong_rejected": not _ok(mod.check("y=0", ans, p)),
                "negated_form_accepted": equiv_ok,
                "has_bisector_token": ("垂直平分" in q) or ("距離相等" in q),
            }
        )
    # textbook oracle A(-1,1), B(3,-1) → 2x - y - 2 = 0
    from core.gencode.slot_generators import _canonical_perpendicular_bisector_from_two_points

    _, _, _, canon = _canonical_perpendicular_bisector_from_two_points(-1, 1, 3, -1)
    return {
        "type_keys": {k: v for k, v in sorted(types.items())},
        "type_count": len(types),
        "textbook_4542_canonical": canon,
        "rows": rows,
    }


def student_route() -> dict:
    prod = ROOT / "instance" / "kumon_math.db"
    iso = ROOT / "tmp" / f"pointslope_bisector_{STAMP}" / "db.db"
    iso.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(prod, iso)
    os.environ["MATHPROJECT_DATABASE_URI"] = f"sqlite:///{iso.as_posix()}"
    sys.path.insert(0, str(ROOT))
    import config as app_config
    from werkzeug.security import generate_password_hash

    app_config.Config.SQLALCHEMY_DATABASE_URI = os.environ["MATHPROJECT_DATABASE_URI"]
    from app import create_app
    from models import User, db

    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["MATHPROJECT_DATABASE_URI"]
    with app.app_context():
        u = User(username=f"psf_bis_{STAMP}", password_hash=generate_password_hash("x"), role="student")
        db.session.add(u)
        db.session.commit()
        uid = str(u.id)

    results = []
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["_user_id"] = uid
            sess["_fresh"] = True
        # Force bisector component
        for cid in ("src_4542", "src_4550", "src_4540"):
            res = client.get(
                "/get_next_question",
                query_string={"skill": SKILL, "level": 1, "component_id": cid, "seed": 14},
            )
            data = res.get_json(silent=True) or {}
            q = str(data.get("question") or data.get("question_text") or "")
            row = {
                "component_id": cid,
                "generate": "PASS" if res.status_code == 200 and q and data.get("question_uid") else "FAIL",
                "problem_type_id": data.get("problem_type_id"),
                "question_preview": q[:110],
                "checker": "SKIP",
            }
            if row["generate"] != "PASS":
                results.append(row)
                continue
            from core.practice_question_store import _STORE

            stored = None
            for bucket in _STORE.values():
                if data["question_uid"] in bucket:
                    stored = bucket[data["question_uid"]]
                    break
            ans = None
            if isinstance(stored, dict):
                ans = stored.get("semantic_answer") or stored.get("correct_answer") or stored.get("answer")
            chk = client.post(
                "/check_answer",
                json={"skill_id": SKILL, "question_uid": data["question_uid"], "answer": ans},
            )
            body = chk.get_json(silent=True) or {}
            row["checker"] = "PASS" if chk.status_code == 200 and (body.get("correct") or body.get("all_correct")) else "FAIL"
            results.append(row)

        # type rotation should eventually pick bisector type without forcing component
        seen_types = set()
        for i in range(12):
            res = client.get("/get_next_question", query_string={"skill": SKILL, "level": 1, "seed": 100 + i})
            data = res.get_json(silent=True) or {}
            pt = data.get("problem_type_id") or ((data.get("metadata") or {}).get("problem_type_id"))
            if pt:
                seen_types.add(str(pt))
    return {"forced_components": results, "rotation_seen_types": sorted(seen_types)}


def main() -> int:
    off = offline()
    route = student_route()
    payload = {"generated_at": STAMP, "offline": off, "student_route": route}
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"pointslope_bisector_fix_{STAMP}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "pointslope_bisector_fix_latest.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({"wrote": str(path), "type_count": off["type_count"], "types": list(off["type_keys"].keys()), "canon": off["textbook_4542_canonical"], "rotation": route["rotation_seen_types"]}, ensure_ascii=False, indent=2))
    for r in off["rows"]:
        print(r)
    for r in route["forced_components"]:
        print(r["generate"], r["checker"], r["component_id"], r.get("problem_type_id"), r["question_preview"][:70])
    fails = [r for r in off["rows"] if not r.get("self_check") or not r.get("wrong_rejected") or (r.get("case") == "bisector" and not r.get("has_bisector_token"))]
    fails += [r for r in route["forced_components"] if r["generate"] != "PASS" or r["checker"] != "PASS"]
    if "write_perpendicular_bisector_from_two_points" not in route["rotation_seen_types"]:
        print("WARN rotation did not observe bisector type in 12 draws")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
