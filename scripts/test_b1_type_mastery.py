# -*- coding: utf-8 -*-
"""Focused B1 problem-type mastery tests (no full B1 sweep)."""
from __future__ import annotations

import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

STAMP = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
ISO_DIR = ROOT / "tmp" / f"b1_type_mastery_{STAMP}"
ISO_DIR.mkdir(parents=True, exist_ok=True)
ISO_DB = ISO_DIR / "kumon_math.db"
shutil.copy2(ROOT / "instance" / "kumon_math.db", ISO_DB)
os.environ["MATHPROJECT_DATABASE_URI"] = f"sqlite:///{ISO_DB.as_posix()}"

import config as app_config

app_config.Config.SQLALCHEMY_DATABASE_URI = os.environ["MATHPROJECT_DATABASE_URI"]

from app import app as flask_app
from models import StudentProblemTypeMastery, User, db
from core.practice_type_mastery import (
    STATUS_MASTERED,
    get_skill_type_progress,
    is_b1_type_mastery_skill,
    list_required_problem_types,
    record_type_attempt,
)
from werkzeug.security import generate_password_hash


def _ok(label: str, cond: bool, detail: str = "") -> dict:
    print(("PASS" if cond else "FAIL"), label, detail)
    return {"label": label, "pass": bool(cond), "detail": detail}


def main() -> int:
    results = []
    with flask_app.app_context():
        # Ensure table exists on isolated DB copy.
        from scripts.migrate_b1_problem_type_mastery import DDL
        import sqlite3

        con = sqlite3.connect(str(ISO_DB))
        con.execute(DDL)
        con.commit()
        con.close()

        skill = "vh_數學B1_PointSlopeForm"
        results.append(_ok("is_b1_true", is_b1_type_mastery_skill(skill)))
        results.append(_ok("is_b1_false_b2", not is_b1_type_mastery_skill("vh_數學B2_Foo")))
        results.append(_ok("is_b1_false_subsection", not is_b1_type_mastery_skill("vh_數學B1_SubSection332")))

        types = list_required_problem_types(skill)
        results.append(_ok("point_slope_has_types", len(types) >= 2, f"n={len(types)} types={types}"))

        # Prefer a B1 skill with >=4 runtime types for multi-type scenarios.
        multi_skill = skill
        multi_types = types
        import sqlite3 as _sqlite3

        _con = _sqlite3.connect(str(ISO_DB))
        _sids = [
            r[0]
            for r in _con.execute(
                "SELECT skill_id FROM skills_info WHERE skill_id LIKE 'vh_數學B1_%'"
            ).fetchall()
        ]
        _con.close()
        for sid in _sids:
            cand = list_required_problem_types(sid)
            if len(cand) >= 4:
                multi_skill, multi_types = sid, cand
                break
        results.append(
            _ok(
                "found_multi_type_skill",
                len(multi_types) >= 2,
                f"skill={multi_skill} n={len(multi_types)}",
            )
        )

        user = User(
            username=f"b1_mastery_{STAMP}",
            password_hash=generate_password_hash("x", method="pbkdf2:sha256"),
            role="student",
            email=f"b1_mastery_{STAMP}@audit.local",
        )
        db.session.add(user)
        db.session.commit()
        uid = int(user.id)

        # Same type correct four times → still 1/N
        t0 = multi_types[0]
        for i in range(4):
            record_type_attempt(
                user_id=uid,
                skill_id=multi_skill,
                problem_type_id=t0,
                is_correct=True,
                question_uid=f"q-same-{i}",
                assisted=False,
                commit=True,
            )
        p = get_skill_type_progress(uid, multi_skill)
        results.append(
            _ok(
                "same_type_four_correct_is_1",
                p["mastered_count"] == 1 and p["total_types"] == len(multi_types),
                f"{p['mastered_count']}/{p['total_types']}",
            )
        )

        # Master A then B; wrong on C keeps 2; assisted correct does not advance;
        # independent correct advances.
        if len(multi_types) >= 3:
            t1, t2 = multi_types[1], multi_types[2]
            record_type_attempt(
                user_id=uid, skill_id=multi_skill, problem_type_id=t1, is_correct=True, commit=True
            )
            p = get_skill_type_progress(uid, multi_skill)
            results.append(_ok("after_second_type", p["mastered_count"] == 2, str(p["mastered_count"])))
            record_type_attempt(
                user_id=uid, skill_id=multi_skill, problem_type_id=t2, is_correct=False, commit=True
            )
            p = get_skill_type_progress(uid, multi_skill)
            results.append(_ok("wrong_keeps_mastered", p["mastered_count"] == 2, str(p["mastered_count"])))
            record_type_attempt(
                user_id=uid,
                skill_id=multi_skill,
                problem_type_id=t2,
                is_correct=True,
                assisted=True,
                commit=True,
            )
            p = get_skill_type_progress(uid, multi_skill)
            results.append(_ok("assisted_not_mastered", p["mastered_count"] == 2, str(p["mastered_count"])))
            record_type_attempt(
                user_id=uid,
                skill_id=multi_skill,
                problem_type_id=t2,
                is_correct=True,
                assisted=False,
                commit=True,
            )
            p = get_skill_type_progress(uid, multi_skill)
            results.append(_ok("independent_after_assist", p["mastered_count"] == 3, str(p["mastered_count"])))

        # Complete remaining types → N/N
        for pt in multi_types:
            record_type_attempt(
                user_id=uid,
                skill_id=multi_skill,
                problem_type_id=pt,
                is_correct=True,
                assisted=False,
                commit=True,
            )
        p = get_skill_type_progress(uid, multi_skill)
        results.append(
            _ok(
                "all_types_complete",
                p["complete"] and p["mastered_count"] == p["total_types"] > 0,
                f"{p['mastered_count']}/{p['total_types']} complete={p['complete']}",
            )
        )

        # Persistence across new query
        p2 = get_skill_type_progress(uid, multi_skill)
        results.append(
            _ok("persisted_reload", p2["mastered_count"] == len(multi_types), str(p2["mastered_count"]))
        )

        # Zero-type skill must not complete
        zero = get_skill_type_progress(uid, "vh_數學B1_SubSection332")
        results.append(
            _ok(
                "zero_types_not_complete",
                zero["total_types"] == 0 and not zero["complete"],
                zero.get("display_label"),
            )
        )

        rows = (
            db.session.query(StudentProblemTypeMastery)
            .filter_by(user_id=uid, skill_id=multi_skill, status=STATUS_MASTERED)
            .count()
        )
        results.append(_ok("db_mastered_rows", rows == len(multi_types), f"rows={rows}"))

        # B2 skill must not write mastery rows even if called.
        b2 = "vh_數學B2_Synthetic"
        out = record_type_attempt(
            user_id=uid,
            skill_id=b2,
            problem_type_id="any_type",
            is_correct=True,
            commit=True,
        )
        b2_rows = (
            db.session.query(StudentProblemTypeMastery).filter_by(user_id=uid, skill_id=b2).count()
        )
        results.append(
            _ok("b2_skipped", bool(out.get("skipped")) and b2_rows == 0, str(out))
        )

    failed = [r for r in results if not r["pass"]]
    out = {
        "passed": len(results) - len(failed),
        "total": len(results),
        "failed": failed,
        "results": results,
        "iso_db": str(ISO_DB),
    }
    path = ROOT / "reports/gencode_closed_loop" / f"b1_type_mastery_test_{STAMP}.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "reports/gencode_closed_loop/b1_type_mastery_test_latest.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("SUMMARY", out["passed"], "/", out["total"], "wrote", path)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
