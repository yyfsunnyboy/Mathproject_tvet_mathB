# -*- coding: utf-8 -*-
"""B2 ch1 pilot runtime acceptance on isolated DB (3 representative skills)."""
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
ISO_DIR = ROOT / "tmp" / f"b2_phase2_ch1_accept_{STAMP}"
ISO_DIR.mkdir(parents=True, exist_ok=True)
ISO_DB = ISO_DIR / "kumon_math.db"
shutil.copy2(ROOT / "instance" / "kumon_math.db", ISO_DB)
os.environ["MATHPROJECT_DATABASE_URI"] = f"sqlite:///{ISO_DB.as_posix()}"

import config as app_config

app_config.Config.SQLALCHEMY_DATABASE_URI = os.environ["MATHPROJECT_DATABASE_URI"]

from app import app as flask_app
from core.practice_type_mastery import (
    B2_TYPE_MASTERY_PILOT_SKILL_IDS,
    get_skill_type_progress,
    is_b1_type_mastery_skill,
    list_required_problem_types,
    record_type_attempt,
    resolve_next_b1_practice_skill,
)
from models import StudentProblemTypeMastery, User, db
from werkzeug.security import generate_password_hash

REPS = [
    "vh_數學B2_RatioAndRatioValue",
    "vh_數學B2_TrigonometricFunctionsOfAcuteAngles",
    "vh_數學B2_FundamentalTrigonometricIdentities",
    "vh_數學B2_SubSection_1_3_2",
]


def _ok(label: str, cond: bool, detail: str = "") -> dict:
    print(("PASS" if cond else "FAIL"), label, detail)
    return {"label": label, "pass": bool(cond), "detail": detail}


def _accept_one(uid: int, skill_id: str, results: list[dict]) -> None:
    assert is_b1_type_mastery_skill(skill_id)
    types = list_required_problem_types(skill_id)
    results.append(_ok(f"{skill_id}:Y_gt0", len(types) >= 1, str(len(types))))
    p0 = get_skill_type_progress(uid, skill_id)
    results.append(
        _ok(
            f"{skill_id}:Y_matches_progress",
            int(p0.get("total_types") or 0) == len(types),
            f"progress={p0.get('total_types')} inv={len(types)}",
        )
    )
    t0 = types[0]
    for i in range(3):
        record_type_attempt(
            user_id=uid,
            skill_id=skill_id,
            problem_type_id=t0,
            is_correct=True,
            question_uid=f"{skill_id}-same-{i}",
            assisted=False,
            commit=True,
        )
    p1 = get_skill_type_progress(uid, skill_id)
    results.append(
        _ok(
            f"{skill_id}:same_type_no_double_count",
            int(p1.get("mastered_count") or 0) == 1,
            str(p1.get("mastered_count")),
        )
    )
    record_type_attempt(
        user_id=uid,
        skill_id=skill_id,
        problem_type_id=t0,
        is_correct=False,
        question_uid=f"{skill_id}-wrong",
        assisted=False,
        commit=True,
    )
    p2 = get_skill_type_progress(uid, skill_id)
    results.append(
        _ok(
            f"{skill_id}:wrong_keeps_mastered",
            int(p2.get("mastered_count") or 0) == 1,
            str(p2.get("mastered_count")),
        )
    )
    if len(types) >= 2:
        t1 = types[1]
        record_type_attempt(
            user_id=uid,
            skill_id=skill_id,
            problem_type_id=t1,
            is_correct=True,
            question_uid=f"{skill_id}-assist",
            assisted=True,
            commit=True,
        )
        p3 = get_skill_type_progress(uid, skill_id)
        results.append(
            _ok(
                f"{skill_id}:assisted_not_mastered",
                int(p3.get("mastered_count") or 0) == 1,
                str(p3.get("mastered_count")),
            )
        )
        record_type_attempt(
            user_id=uid,
            skill_id=skill_id,
            problem_type_id=t1,
            is_correct=True,
            question_uid=f"{skill_id}-indep",
            assisted=False,
            commit=True,
        )
        p4 = get_skill_type_progress(uid, skill_id)
        results.append(
            _ok(
                f"{skill_id}:independent_after_assist",
                int(p4.get("mastered_count") or 0) == 2,
                str(p4.get("mastered_count")),
            )
        )


def main() -> int:
    results: list[dict] = []
    with flask_app.app_context():
        for sid in REPS:
            results.append(_ok(f"gated:{sid}", sid in B2_TYPE_MASTERY_PILOT_SKILL_IDS and is_b1_type_mastery_skill(sid)))

        u1 = User(
            username=f"b2p2_a_{STAMP}",
            password_hash=generate_password_hash("x", method="pbkdf2:sha256"),
            role="student",
            email=f"b2p2_a_{STAMP}@audit.local",
        )
        u2 = User(
            username=f"b2p2_b_{STAMP}",
            password_hash=generate_password_hash("x", method="pbkdf2:sha256"),
            role="student",
            email=f"b2p2_b_{STAMP}@audit.local",
        )
        db.session.add_all([u1, u2])
        db.session.commit()
        uid1, uid2 = int(u1.id), int(u2.id)

        for sid in REPS:
            _accept_one(uid1, sid, results)

        # Complete multi-type skill for MsgBox / nav checks
        multi = "vh_數學B2_TrigonometricFunctionsOfAcuteAngles"
        for i, pt in enumerate(list_required_problem_types(multi)):
            record_type_attempt(
                user_id=uid1,
                skill_id=multi,
                problem_type_id=pt,
                is_correct=True,
                question_uid=f"multi-finish-{i}",
                assisted=False,
                commit=True,
            )
        done = get_skill_type_progress(uid1, multi)
        results.append(_ok("multi_complete", bool(done.get("complete")), str(done.get("display_label"))))

        # First completion nav uses curriculum order among pilot skills
        nav = resolve_next_b1_practice_skill(multi, user_id=uid1)
        results.append(
            _ok(
                "nav_curriculum_same_chapter",
                nav.get("nav_kind") in {"same_chapter", "same_chapter_backfill", "chapter_complete"},
                json.dumps(nav, ensure_ascii=False),
            )
        )
        if nav.get("skill_id"):
            results.append(
                _ok(
                    "nav_target_still_pilot",
                    nav["skill_id"] in B2_TYPE_MASTERY_PILOT_SKILL_IDS,
                    str(nav.get("skill_id")),
                )
            )

        # Free review: already complete skill remains reviewable; no revoke on wrong
        record_type_attempt(
            user_id=uid1,
            skill_id=multi,
            problem_type_id=list_required_problem_types(multi)[0],
            is_correct=False,
            question_uid="review-wrong",
            assisted=False,
            commit=True,
        )
        after_review = get_skill_type_progress(uid1, multi)
        results.append(
            _ok(
                "free_review_wrong_keeps_complete",
                bool(after_review.get("complete")),
                str(after_review.get("mastered_count")),
            )
        )

        # Student isolation
        other = get_skill_type_progress(uid2, multi)
        results.append(
            _ok(
                "student_isolation",
                int(other.get("mastered_count") or 0) == 0,
                str(other.get("mastered_count")),
            )
        )
        rows_u2 = StudentProblemTypeMastery.query.filter_by(user_id=uid2).count()
        results.append(_ok("student_isolation_rows", rows_u2 == 0, str(rows_u2)))

        # MsgBox markup still present (UI contract)
        html = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
        results.append(_ok("msgbox_markup", "skillCompletionModal" in html))
        results.append(_ok("msgbox_just_completed_gate", "skill_just_completed" in html or "just_completed" in html))

    summary = {
        "stamp": STAMP,
        "pass": sum(1 for r in results if r["pass"]),
        "total": len(results),
        "results": results,
        "representatives": REPS,
        "browser_ui": "NOT_TESTED",
        "multipart_live_submit": "NOT_TESTED",
    }
    out = ROOT / "reports/gencode_closed_loop" / f"b2_phase2_ch1_runtime_accept_{STAMP}.json"
    latest = ROOT / "reports/gencode_closed_loop/b2_phase2_ch1_runtime_accept_latest.json"
    text = json.dumps(summary, ensure_ascii=False, indent=2)
    out.write_text(text, encoding="utf-8")
    latest.write_text(text, encoding="utf-8")
    print("SUMMARY", summary["pass"], "/", summary["total"], "wrote", out)
    return 0 if summary["pass"] == summary["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
