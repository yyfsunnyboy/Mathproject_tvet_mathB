# -*- coding: utf-8 -*-
"""Publish PolynomialBasicConcepts V3 components to production."""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config import Config
from core.gencode.services.admin_gencode_action_service import run_admin_v3_publish_for_skill

SKILL = "vh_數學B1_PolynomialBasicConcepts"
OUT = ROOT / "scratch" / "_pbc_publish.json"


def main() -> None:
    conn = sqlite3.connect(Config.db_path)
    try:
        result = run_admin_v3_publish_for_skill(
            conn=conn,
            skill_id=SKILL,
            project_root=str(ROOT),
            staging_root=str(ROOT / "reports" / "gencode_v3_publish_staging"),
            force_publish=True,
            strict_coverage=False,
        )
        conn.commit()
    except Exception as exc:
        conn.rollback()
        result = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str)[:3000])
    conn.close()


if __name__ == "__main__":
    main()
