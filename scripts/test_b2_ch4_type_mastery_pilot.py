# -*- coding: utf-8 -*-
"""B2 chapter-4 type-mastery opt-in: 6 practice SubSections with usable Y."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

STAMP = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
ISO_DIR = ROOT / "tmp" / f"b2_ch4_mastery_{STAMP}"
ISO_DIR.mkdir(parents=True, exist_ok=True)
ISO_DB = ISO_DIR / "kumon_math.db"
_src = __import__("sqlite3").connect(str(ROOT / "instance" / "kumon_math.db"))
try:
    _src.execute(f"VACUUM INTO '{ISO_DB.as_posix()}'")
finally:
    _src.close()
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
from models import Progress, User, db
from werkzeug.security import generate_password_hash

CH4_PILOT = (
    "vh_數學B2_SubSection_4_1_1",
    "vh_數學B2_SubSection_4_1_2",
    "vh_數學B2_SubSection_4_2_1",
    "vh_數學B2_SubSection_4_2_2",
    "vh_數學B2_SubSection_4_2_3",
    "vh_數學B2_SubSection_4_2_4",
)
NOT_GATED = (
    "vh_數學B2_SubSection_2_2_1",  # inactive ch2 org
)


def _ok(label: str, cond: bool, detail: str = "") -> dict:
    print(("PASS" if cond else "FAIL"), label, detail)
    return {"label": label, "pass": bool(cond), "detail": detail}


def main() -> int:
    results: list[dict] = []
    usable_map: dict[str, list[str]] = {}
    with flask_app.app_context():
        results.append(_ok("ch4_count_6", len(CH4_PILOT) == 6))
        for sid in CH4_PILOT:
            results.append(_ok(f"gated:{sid}", sid in B2_TYPE_MASTERY_PILOT_SKILL_IDS))
            results.append(_ok(f"enabled:{sid}", is_b1_type_mastery_skill(sid)))
            types = list_required_problem_types(sid)
            usable_map[sid] = types
            results.append(_ok(f"usable_Y:{sid}", len(types) >= 1, str(len(types))))

        for sid in NOT_GATED:
            results.append(_ok(f"not_gated:{sid}", not is_b1_type_mastery_skill(sid)))

        results.append(
            _ok("ch3_still_gated", is_b1_type_mastery_skill("vh_數學B2_SubSection_3_1_1"))
        )
        results.append(
            _ok(
                "ch1_named_still_gated",
                is_b1_type_mastery_skill("vh_數學B2_TrigonometricFunctionsOfAcuteAngles"),
            )
        )

        user = User(
            username=f"b2ch4_{STAMP}",
            password_hash=generate_password_hash("x", method="pbkdf2:sha256"),
            role="student",
            email=f"b2ch4_{STAMP}@audit.local",
        )
        db.session.add(user)
        db.session.commit()
        uid = int(user.id)

        sample = "vh_數學B2_SubSection_4_1_1"
        db.session.add(
            Progress(user_id=uid, skill_id=sample, consecutive_correct=50, consecutive_wrong=0)
        )
        db.session.commit()
        before = get_skill_type_progress(uid, sample)
        results.append(
            _ok(
                "legacy_streak_not_mastery",
                int(before.get("mastered_count") or 0) == 0,
                str(before.get("display_label")),
            )
        )

        types = list_required_problem_types(sample)
        t0 = types[0]
        record_type_attempt(
            user_id=uid, skill_id=sample, problem_type_id=t0, is_correct=True, commit=True
        )
        record_type_attempt(
            user_id=uid, skill_id=sample, problem_type_id=t0, is_correct=True, commit=True
        )
        p1 = get_skill_type_progress(uid, sample)
        results.append(_ok("same_type_once", int(p1.get("mastered_count") or 0) == 1))

        record_type_attempt(
            user_id=uid, skill_id=sample, problem_type_id=t0, is_correct=False, commit=True
        )
        p2 = get_skill_type_progress(uid, sample)
        results.append(_ok("wrong_keeps", int(p2.get("mastered_count") or 0) == 1))

        if len(types) >= 2:
            record_type_attempt(
                user_id=uid,
                skill_id=sample,
                problem_type_id=types[1],
                is_correct=True,
                assisted=True,
                commit=True,
            )
            p3 = get_skill_type_progress(uid, sample)
            results.append(_ok("assisted_blocked", int(p3.get("mastered_count") or 0) == 1))
            record_type_attempt(
                user_id=uid,
                skill_id=sample,
                problem_type_id=types[1],
                is_correct=True,
                assisted=False,
                commit=True,
            )
            p4 = get_skill_type_progress(uid, sample)
            results.append(_ok("independent_ok", int(p4.get("mastered_count") or 0) == 2))

        for i, pt in enumerate(types):
            record_type_attempt(
                user_id=uid,
                skill_id=sample,
                problem_type_id=pt,
                is_correct=True,
                question_uid=f"ch4-fin-{i}",
                assisted=False,
                commit=True,
            )
        done = get_skill_type_progress(uid, sample)
        results.append(
            _ok("skill_complete", bool(done.get("complete")), str(done.get("display_label")))
        )
        nav = resolve_next_b1_practice_skill(sample, user_id=uid)
        results.append(
            _ok(
                "nav_same_chapter_or_complete",
                nav.get("nav_kind")
                in {"same_chapter", "same_chapter_backfill", "chapter_complete", "volume_complete"},
                json.dumps(nav, ensure_ascii=False),
            )
        )
        if nav.get("skill_id"):
            results.append(
                _ok(
                    "nav_target_in_ch4_or_gated",
                    nav["skill_id"] in CH4_PILOT
                    or is_b1_type_mastery_skill(str(nav["skill_id"])),
                    str(nav.get("skill_id")),
                )
            )

        # MCQ type mastery for same-center scaled area
        mcq_type = "circle_same_center_scaled_area"
        if mcq_type in types:
            other_user = User(
                username=f"b2ch4b_{STAMP}",
                password_hash=generate_password_hash("x", method="pbkdf2:sha256"),
                role="student",
                email=f"b2ch4b_{STAMP}@audit.local",
            )
            db.session.add(other_user)
            db.session.commit()
            uid2 = int(other_user.id)
            record_type_attempt(
                user_id=uid2,
                skill_id=sample,
                problem_type_id=mcq_type,
                is_correct=True,
                commit=True,
            )
            iso = get_skill_type_progress(uid2, sample)
            results.append(
                _ok(
                    "mcq_type_mastery_isolated",
                    int(iso.get("mastered_count") or 0) == 1
                    and int(done.get("mastered_count") or 0) == len(types),
                    str(iso.get("display_label")),
                )
            )

    summary = {
        "stamp": STAMP,
        "pass": sum(1 for r in results if r["pass"]),
        "total": len(results),
        "results": results,
        "ch4_pilot": list(CH4_PILOT),
        "usable_Y": {k: len(v) for k, v in usable_map.items()},
        "usable_ids": usable_map,
    }
    out_dir = ROOT / "reports" / "b2_ch4_intro"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"b2_ch4_type_mastery_pilot_{STAMP}.json"
    latest = out_dir / "b2_ch4_type_mastery_pilot_latest.json"
    closed = ROOT / "reports" / "gencode_closed_loop" / f"b2_ch4_type_mastery_pilot_{STAMP}.json"
    text = json.dumps(summary, ensure_ascii=False, indent=2)
    out.write_text(text, encoding="utf-8")
    latest.write_text(text, encoding="utf-8")
    closed.parent.mkdir(parents=True, exist_ok=True)
    closed.write_text(text, encoding="utf-8")
    print("SUMMARY", summary["pass"], "/", summary["total"], "wrote", out)
    return 0 if summary["pass"] == summary["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
