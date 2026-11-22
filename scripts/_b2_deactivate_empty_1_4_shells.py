# -*- coding: utf-8 -*-
"""Deactivate B2 SubSection_1_4_1/1_4_2 empty active shells (no TE/facade/Y).

Does not delete curriculum, examples, or student history. Requires prior DB backup.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import app
from models import SkillInfo, db

TARGETS = (
    "vh_數學B2_SubSection_1_4_1",
    "vh_數學B2_SubSection_1_4_2",
)


def main() -> int:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    changed = []
    with app.app_context():
        for sid in TARGETS:
            info = SkillInfo.query.filter_by(skill_id=sid).first()
            if info is None:
                changed.append({"skill_id": sid, "status": "missing"})
                continue
            before = bool(info.is_active)
            if before:
                info.is_active = False
                changed.append(
                    {
                        "skill_id": sid,
                        "status": "deactivated",
                        "name": info.skill_ch_name,
                        "before_active": before,
                        "after_active": False,
                        "reason": "active_shell_no_te_no_facade_no_usable_types",
                    }
                )
            else:
                changed.append(
                    {
                        "skill_id": sid,
                        "status": "already_inactive",
                        "name": info.skill_ch_name,
                    }
                )
        db.session.commit()
    out = {
        "stamp": stamp,
        "changed": changed,
        "backup_hint": "instance/backups/kumon_math_pre_b2_phase2_*.db",
    }
    path = ROOT / "reports/gencode_closed_loop" / f"b2_deactivate_1_4_shells_{stamp}.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))
    print("WROTE", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
