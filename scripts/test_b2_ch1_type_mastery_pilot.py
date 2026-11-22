# -*- coding: utf-8 -*-
"""B2 chapter-1 type-mastery pilot: gate, inventory Y, nav among pilot skills."""
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
ISO_DIR = ROOT / "tmp" / f"b2_type_mastery_pilot_{STAMP}"
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
from models import Progress, StudentProblemTypeMastery, User, db
from werkzeug.security import generate_password_hash


def _ok(label: str, cond: bool, detail: str = "") -> dict:
    print(("PASS" if cond else "FAIL"), label, detail)
    return {"label": label, "pass": bool(cond), "detail": detail}


def main() -> int:
    results: list[dict] = []
    ch1_named = sorted(
        sid
        for sid in B2_TYPE_MASTERY_PILOT_SKILL_IDS
        if sid.startswith("vh_數學B2_") and "SubSection" not in sid
    )
    ch1_a_subs = sorted(
        sid
        for sid in B2_TYPE_MASTERY_PILOT_SKILL_IDS
        if sid.startswith("vh_數學B2_SubSection_1_")
    )
    expected_a_subs = {
        "vh_數學B2_SubSection_1_3_1",
        "vh_數學B2_SubSection_1_3_2",
        "vh_數學B2_SubSection_1_3_4",
        "vh_數學B2_SubSection_1_3_5",
        "vh_數學B2_SubSection_1_3_6",
        "vh_數學B2_SubSection_1_3_7",
        "vh_數學B2_SubSection_1_4_3",
        "vh_數學B2_SubSection_1_4_4",
    }
    with flask_app.app_context():
        results.append(_ok("ch1_named_count_8", len(ch1_named) == 8, str(len(ch1_named))))
        results.append(
            _ok(
                "all_ch1_named_gated",
                all(is_b1_type_mastery_skill(sid) for sid in ch1_named),
            )
        )
        results.append(
            _ok(
                "ch1_a_subsection_count_8",
                set(ch1_a_subs) == expected_a_subs,
                json.dumps(ch1_a_subs, ensure_ascii=False),
            )
        )
        results.append(
            _ok(
                "all_ch1_a_subsection_gated",
                all(is_b1_type_mastery_skill(sid) for sid in expected_a_subs),
            )
        )
        results.append(
            _ok(
                "ch1_empty_shells_not_gated",
                not is_b1_type_mastery_skill("vh_數學B2_SubSection_1_4_1")
                and not is_b1_type_mastery_skill("vh_數學B2_SubSection_1_4_2"),
            )
        )
        results.append(
            _ok(
                "b2_ch2_practice_subsection_gated",
                is_b1_type_mastery_skill("vh_數學B2_SubSection_2_1_1"),
            )
        )

        usable = {sid: list_required_problem_types(sid) for sid in ch1_named}
        usable_subs = {sid: list_required_problem_types(sid) for sid in sorted(expected_a_subs)}
        results.append(
            _ok(
                "all_ch1_named_have_usable_types",
                all(len(v) >= 1 for v in usable.values()),
                json.dumps({k: len(v) for k, v in usable.items()}, ensure_ascii=False),
            )
        )
        results.append(
            _ok(
                "all_ch1_a_subsection_have_usable_types",
                all(len(v) >= 1 for v in usable_subs.values()),
                json.dumps({k: len(v) for k, v in usable_subs.items()}, ensure_ascii=False),
            )
        )

        user = User(
            username=f"b2_pilot_{STAMP}",
            password_hash=generate_password_hash("x", method="pbkdf2:sha256"),
            role="student",
            email=f"b2_pilot_{STAMP}@audit.local",
        )
        db.session.add(user)
        db.session.commit()
        uid = int(user.id)

        # Ensure no consecutive_correct is treated as mastery evidence.
        sample = "vh_數學B2_TrigonometricFunctionsOfAcuteAngles"
        if sample not in usable or not usable[sample]:
            sample = next(sid for sid, types in usable.items() if types)
        db.session.add(
            Progress(
                user_id=uid,
                skill_id=sample,
                consecutive_correct=99,
                consecutive_wrong=0,
            )
        )
        db.session.commit()
        before = get_skill_type_progress(uid, sample)
        results.append(
            _ok(
                "legacy_streak_not_mastery",
                int(before.get("mastered_count") or 0) == 0,
                str(before),
            )
        )

        types = usable[sample]
        for i, pt in enumerate(types):
            record_type_attempt(
                user_id=uid,
                skill_id=sample,
                problem_type_id=pt,
                is_correct=True,
                question_uid=f"b2-pilot-{i}",
                assisted=False,
                commit=True,
            )
        after = get_skill_type_progress(uid, sample)
        results.append(
            _ok(
                "independent_mastery_works",
                bool(after.get("complete")),
                f"{after.get('mastered_count')}/{after.get('total_types')}",
            )
        )
        rows = StudentProblemTypeMastery.query.filter_by(
            user_id=uid, skill_id=sample
        ).count()
        results.append(_ok("mastery_rows_persisted", rows == len(types), str(rows)))

        # Nav among pilot skills: after completing first, should stay in ch1 pilot set.
        nav = resolve_next_b1_practice_skill(sample, user_id=uid)
        nxt = nav.get("skill_id")
        results.append(
            _ok(
                "nav_next_is_pilot_or_chapter",
                (
                    (nxt in ch1_named)
                    or nav.get("nav_kind")
                    in {
                        "chapter_complete",
                        "volume_complete",
                        "same_chapter",
                        "same_chapter_backfill",
                    }
                ),
                json.dumps(nav, ensure_ascii=False),
            )
        )
        if nxt:
            results.append(
                _ok(
                    "nav_target_gated",
                    is_b1_type_mastery_skill(str(nxt)),
                    str(nxt),
                )
            )

    summary = {
        "stamp": STAMP,
        "pass": sum(1 for r in results if r["pass"]),
        "total": len(results),
        "results": results,
        "ch1_named_skills": ch1_named,
    }
    out = ROOT / "reports/gencode_closed_loop" / f"b2_ch1_type_mastery_pilot_{STAMP}.json"
    latest = ROOT / "reports/gencode_closed_loop/b2_ch1_type_mastery_pilot_latest.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    latest.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print("SUMMARY", summary["pass"], "/", summary["total"], "wrote", out)
    return 0 if summary["pass"] == summary["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
