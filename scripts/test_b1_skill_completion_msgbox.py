# -*- coding: utf-8 -*-
"""B1 skill-completion celebration payload tests (transition only)."""
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
ISO_DIR = ROOT / "tmp" / f"b1_skill_completion_{STAMP}"
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
    list_required_problem_types,
    record_type_attempt,
    resolve_next_b1_practice_skill,
)
from werkzeug.security import generate_password_hash


def _ok(label: str, cond: bool, detail: str = "") -> dict:
    print(("PASS" if cond else "FAIL"), label, detail)
    return {"label": label, "pass": bool(cond), "detail": detail}


def main() -> int:
    results = []
    skill = "vh_數學B1_AbsoluteValueInequality"
    with flask_app.app_context():
        from scripts.migrate_b1_problem_type_mastery import DDL
        import sqlite3

        con = sqlite3.connect(str(ISO_DB))
        con.execute(DDL)
        con.commit()
        con.close()

        types = list_required_problem_types(skill)
        results.append(_ok("has_four_types", len(types) >= 4, f"n={len(types)}"))

        user = User(
            username=f"b1_complete_{STAMP}",
            password_hash=generate_password_hash("x", method="pbkdf2:sha256"),
            role="student",
            email=f"b1_complete_{STAMP}@audit.local",
        )
        db.session.add(user)
        db.session.commit()
        uid = int(user.id)

        # Master all but last
        for pt in types[:-1]:
            record_type_attempt(
                user_id=uid, skill_id=skill, problem_type_id=pt, is_correct=True, commit=True
            )

        before = build_skill_completion_payload(
            user_id=uid, skill_id=skill, was_complete_before=False, persisted=True
        )
        results.append(
            _ok(
                "not_complete_before_last",
                not before["skill_complete"] and not before["skill_just_completed"],
                f"{before['progress']['mastered_count']}/{before['progress']['total_types']}",
            )
        )

        # Wrong answer on last type → no celebration
        record_type_attempt(
            user_id=uid, skill_id=skill, problem_type_id=types[-1], is_correct=False, commit=True
        )
        wrong = build_skill_completion_payload(
            user_id=uid, skill_id=skill, was_complete_before=False, persisted=True
        )
        results.append(
            _ok(
                "wrong_no_completion",
                not wrong["skill_complete"] and not wrong["skill_just_completed"],
                str(wrong["progress"]["mastered_count"]),
            )
        )

        # Assisted correct on last → no completion
        record_type_attempt(
            user_id=uid,
            skill_id=skill,
            problem_type_id=types[-1],
            is_correct=True,
            assisted=True,
            commit=True,
        )
        assisted = build_skill_completion_payload(
            user_id=uid, skill_id=skill, was_complete_before=False, persisted=True
        )
        results.append(
            _ok(
                "assisted_no_completion",
                not assisted["skill_complete"] and not assisted["skill_just_completed"],
                str(assisted["progress"]["mastered_count"]),
            )
        )

        # Independent correct → just completed
        record_type_attempt(
            user_id=uid,
            skill_id=skill,
            problem_type_id=types[-1],
            is_correct=True,
            assisted=False,
            commit=True,
        )
        done = build_skill_completion_payload(
            user_id=uid, skill_id=skill, was_complete_before=False, persisted=True
        )
        results.append(
            _ok(
                "just_completed_true",
                done["skill_complete"] and done["skill_just_completed"],
                done["progress"]["display_label"],
            )
        )

        # Persist failure must not celebrate
        not_persisted = build_skill_completion_payload(
            user_id=uid, skill_id=skill, was_complete_before=False, persisted=False
        )
        results.append(
            _ok(
                "unpersisted_no_just_completed",
                not_persisted["skill_complete"] and not not_persisted["skill_just_completed"],
                "",
            )
        )

        # Already complete → no re-trigger
        again = build_skill_completion_payload(
            user_id=uid, skill_id=skill, was_complete_before=True, persisted=True
        )
        results.append(
            _ok(
                "already_complete_no_retrigger",
                again["skill_complete"] and not again["skill_just_completed"],
                "",
            )
        )

        # Same type again after complete
        record_type_attempt(
            user_id=uid,
            skill_id=skill,
            problem_type_id=types[0],
            is_correct=True,
            assisted=False,
            commit=True,
        )
        same = build_skill_completion_payload(
            user_id=uid, skill_id=skill, was_complete_before=True, persisted=True
        )
        results.append(
            _ok(
                "repeat_type_no_retrigger",
                same["skill_complete"] and not same["skill_just_completed"],
                str(same["progress"]["mastered_count"]),
            )
        )

        nxt = resolve_next_b1_practice_skill(skill)
        results.append(
            _ok(
                "next_skill_resolved_or_dashboard",
                isinstance(nxt, dict)
                and nxt.get("nav_kind") in {
                    "same_chapter",
                    "next_chapter",
                    "volume_complete",
                    "fallback_dashboard",
                },
                str(nxt),
            )
        )

        # UI markers present
        html = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
        results.append(_ok("modal_markup", "skillCompletionModal" in html))
        results.append(_ok("modal_title", "太棒了！你完成這個單元了！" in html))
        results.append(_ok("modal_primary_btn", "繼續挑戰下一個技能" in html))
        results.append(_ok("modal_stay_btn", "留在目前技能" in html))
        results.append(_ok("js_just_completed_gate", "skill_just_completed" in html))
        results.append(_ok("js_no_autoload_on_complete", "maybeShowB1SkillCompletion" in html))

        # B2 gate
        from core.practice_type_mastery import is_b1_type_mastery_skill

        results.append(_ok("b2_not_gated", not is_b1_type_mastery_skill("vh_數學B2_Foo")))

    failed = [r for r in results if not r["pass"]]
    out = {
        "passed": len(results) - len(failed),
        "total": len(results),
        "failed": failed,
        "results": results,
    }
    path = ROOT / "reports/gencode_closed_loop" / f"b1_skill_completion_msgbox_{STAMP}.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "reports/gencode_closed_loop/b1_skill_completion_msgbox_latest.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("SUMMARY", out["passed"], "/", out["total"], "wrote", path)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
