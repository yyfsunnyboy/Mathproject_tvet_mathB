# -*- coding: utf-8 -*-
"""B1 navigation: skip completed skills, same-chapter backfill, chapter/volume complete."""
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
ISO_DIR = ROOT / "tmp" / f"b1_nav_skip_{STAMP}"
ISO_DIR.mkdir(parents=True, exist_ok=True)
ISO_DB = ISO_DIR / "kumon_math.db"
shutil.copy2(ROOT / "instance" / "kumon_math.db", ISO_DB)
os.environ["MATHPROJECT_DATABASE_URI"] = f"sqlite:///{ISO_DB.as_posix()}"

import config as app_config

app_config.Config.SQLALCHEMY_DATABASE_URI = os.environ["MATHPROJECT_DATABASE_URI"]

from app import app as flask_app
from models import User, db
from core.practice_type_mastery import (
    build_skill_completion_payload,
    list_practiceable_b1_skills_in_chapter,
    list_required_problem_types,
    record_type_attempt,
    resolve_next_b1_practice_skill,
)
from werkzeug.security import generate_password_hash


def _ok(label: str, cond: bool, detail: str = "") -> dict:
    print(("PASS" if cond else "FAIL"), label, detail)
    return {"label": label, "pass": bool(cond), "detail": detail}


def _master_skill(uid: int, skill_id: str) -> None:
    for pt in list_required_problem_types(skill_id):
        record_type_attempt(
            user_id=uid,
            skill_id=skill_id,
            problem_type_id=pt,
            is_correct=True,
            assisted=False,
            commit=True,
        )


def main() -> int:
    results = []
    with flask_app.app_context():
        from scripts.migrate_b1_problem_type_mastery import DDL
        import sqlite3

        con = sqlite3.connect(str(ISO_DB))
        con.execute(DDL)
        con.commit()
        con.close()

        user = User(
            username=f"b1_nav_{STAMP}",
            password_hash=generate_password_hash("x", method="pbkdf2:sha256"),
            role="student",
            email=f"b1_nav_{STAMP}@audit.local",
        )
        other = User(
            username=f"b1_nav_other_{STAMP}",
            password_hash=generate_password_hash("x", method="pbkdf2:sha256"),
            role="student",
            email=f"b1_nav_other_{STAMP}@audit.local",
        )
        db.session.add_all([user, other])
        db.session.commit()
        uid = int(user.id)
        oid = int(other.id)

        # Structural (no user): AbsoluteValueInequality → Expansion
        structural = resolve_next_b1_practice_skill("vh_數學B1_AbsoluteValueInequality")
        results.append(
            _ok(
                "structural_same_chapter",
                structural.get("skill_id")
                == "vh_數學B1_AbsoluteValueInequalityExpansionAndGeometricMeaning",
                str(structural.get("skill_id")),
            )
        )

        # Mark Expansion complete for this user → skip to Cartesian
        _master_skill(uid, "vh_數學B1_AbsoluteValueInequalityExpansionAndGeometricMeaning")
        skipped = resolve_next_b1_practice_skill(
            "vh_數學B1_AbsoluteValueInequality", user_id=uid
        )
        results.append(
            _ok(
                "skip_completed_next",
                skipped.get("skill_id") == "vh_數學B1_CartesianCoordinateSystemEstablishment"
                and skipped.get("nav_kind") == "same_chapter",
                str(skipped),
            )
        )

        # Other student still sees Expansion (isolation)
        other_nav = resolve_next_b1_practice_skill(
            "vh_數學B1_AbsoluteValueInequality", user_id=oid
        )
        results.append(
            _ok(
                "student_isolation",
                other_nav.get("skill_id")
                == "vh_數學B1_AbsoluteValueInequalityExpansionAndGeometricMeaning",
                str(other_nav.get("skill_id")),
            )
        )

        # Backfill: mark all after AbsoluteValue complete in chapter 1 except AbsoluteValue itself,
        # leave AbsoluteValue incomplete, stand on LinearFunction → should backfill AbsoluteValue
        ch1 = list_practiceable_b1_skills_in_chapter(
            curriculum="vocational", volume="數學B1", chapter="1 坐標系與函數圖形"
        )
        for row in ch1:
            if row["skill_id"] == "vh_數學B1_AbsoluteValue":
                continue
            _master_skill(uid, row["skill_id"])
        backfill = resolve_next_b1_practice_skill(
            "vh_數學B1_LinearFunction", user_id=uid
        )
        results.append(
            _ok(
                "same_chapter_backfill",
                backfill.get("nav_kind") == "same_chapter_backfill"
                and backfill.get("skill_id") == "vh_數學B1_AbsoluteValue"
                and "繼續挑戰：" in str(backfill.get("button_label") or ""),
                str(backfill),
            )
        )

        # Complete AbsoluteValue too → chapter complete → SlopeOfALine
        _master_skill(uid, "vh_數學B1_AbsoluteValue")
        chapter_done = resolve_next_b1_practice_skill(
            "vh_數學B1_LinearFunction", user_id=uid
        )
        results.append(
            _ok(
                "chapter_complete_to_ch2",
                chapter_done.get("nav_kind") == "chapter_complete"
                and chapter_done.get("skill_id") == "vh_數學B1_SlopeOfALine"
                and chapter_done.get("button_label") == "前往下一章"
                and chapter_done.get("celebration_kind") == "chapter",
                str(chapter_done),
            )
        )

        # Celebration payload when finishing last remaining ch1 skill
        # Reset a fresh user path via completion builder on AbsoluteValue after all others done:
        # (AbsoluteValue already complete above; simulate just_completed via payload flags)
        payload = build_skill_completion_payload(
            user_id=uid,
            skill_id="vh_數學B1_AbsoluteValue",
            was_complete_before=False,
            persisted=True,
        )
        # AbsoluteValue already complete → just_completed True only if was_complete_before False
        # and complete True — yes it will fire; next should be chapter_complete
        results.append(
            _ok(
                "celebration_chapter_kind",
                payload.get("skill_just_completed")
                and payload.get("chapter_just_completed")
                and payload.get("celebration_kind") == "chapter",
                str(
                    {
                        "just": payload.get("skill_just_completed"),
                        "chapter": payload.get("chapter_just_completed"),
                        "kind": payload.get("celebration_kind"),
                        "nav": (payload.get("next_nav") or {}).get("nav_kind"),
                    }
                ),
            )
        )

        # Volume complete: master all remaining B1 practiceable skills
        for ch in ("2 直線方程式", "3 式的運算"):
            for row in list_practiceable_b1_skills_in_chapter(
                curriculum="vocational", volume="數學B1", chapter=ch
            ):
                _master_skill(uid, row["skill_id"])
        volume = resolve_next_b1_practice_skill(
            "vh_數學B1_RationalEquation", user_id=uid
        )
        results.append(
            _ok(
                "volume_complete",
                volume.get("nav_kind") == "volume_complete"
                and volume.get("celebration_kind") == "volume"
                and volume.get("button_label") == "返回學習儀表板",
                str(volume),
            )
        )

        # Skips NumberLine / SubSection by construction of practiceable list
        ids_ch1 = {r["skill_id"] for r in ch1}
        results.append(_ok("no_numberline", "vh_數學B1_NumberLine" not in ids_ch1))
        ch3 = list_practiceable_b1_skills_in_chapter(
            curriculum="vocational", volume="數學B1", chapter="3 式的運算"
        )
        results.append(
            _ok(
                "no_subsection332",
                "vh_數學B1_SubSection332" not in {r["skill_id"] for r in ch3},
            )
        )

        html = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
        results.append(_ok("ui_chapter_msg", "太棒了！你完成這一章了！" in html))
        results.append(_ok("ui_volume_msg", "太棒了！你完成本冊了！" in html))
        results.append(_ok("ui_review_link", "b1-review-next-incomplete" in html))
        results.append(_ok("ui_continue_colon", "繼續挑戰：" in html or "next_skill_name" in html))

        # B2 unchanged gate
        b2 = resolve_next_b1_practice_skill("vh_數學B2_Foo", user_id=uid)
        results.append(_ok("b2_fallback", b2.get("nav_kind") == "fallback_dashboard"))

    failed = [r for r in results if not r["pass"]]
    out = {
        "passed": len(results) - len(failed),
        "total": len(results),
        "failed": failed,
        "results": results,
    }
    path = ROOT / "reports/gencode_closed_loop" / f"b1_nav_skip_completed_{STAMP}.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "reports/gencode_closed_loop/b1_nav_skip_completed_latest.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("SUMMARY", out["passed"], "/", out["total"], "wrote", path)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
