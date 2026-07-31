# -*- coding: utf-8 -*-
"""Re-import the failed job workbook and print validation summary."""
from __future__ import annotations

import shutil
from pathlib import Path

import config as _cfg
from app import create_app
from core.data_importer import import_excel_to_db
from core.session_safety import summarize_import_result
from models import db
from sqlalchemy import text

XLSX = Path(r"C:\Users\Owner\Downloads\kumon_math_backup_20260731_1511.xlsx")
LIVE = Path(r"D:\Python\Mathproject_tvet_mathB\instance\kumon_math.db")
WORKDIR = Path(r"D:\Python\Mathproject_tvet_mathB\reports\reimport_dcafc89d")
WORKDIR.mkdir(parents=True, exist_ok=True)
DB = WORKDIR / "reimport.db"
shutil.copy2(XLSX, WORKDIR / XLSX.name)

_cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(DB.resolve()).replace("\\", "/")
app = create_app()
with app.app_context():
    # Seed a colliding admin like live leftover teacher username=admin with different id.
    db.session.execute(
        text(
            "INSERT INTO users (id, username, password_hash, role) "
            "VALUES (2589, 'admin', 'x', 'teacher')"
        )
    )
    db.session.commit()
    ok, msg = import_excel_to_db(str(WORKDIR / XLSX.name), mode="core")
    summary = summarize_import_result((ok, msg))
    print("ok", ok)
    print("final_status", summary.get("final_status"), summary.get("final_status_reason"))
    print("source_rows", summary.get("source_rows"), "imported", summary.get("imported_rows"))
    print("failed_rows", summary.get("failed_rows"), "fatal", summary.get("fatal_errors"))
    print("warnings", summary.get("warning_count"), "orphan_sc", summary.get("orphan_skill_curriculum_count"))
    print("--- message tail ---")
    for line in msg.splitlines()[-40:]:
        print(line)
    fk = db.session.execute(text("PRAGMA foreign_key_check")).fetchall()
    print("fk_check", len(fk))
    out = WORKDIR / "reimport_message.txt"
    out.write_text(msg, encoding="utf-8")
    print("wrote", out)
