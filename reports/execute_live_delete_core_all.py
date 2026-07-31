# -*- coding: utf-8 -*-
"""Execute DELETE_CORE textbook+student clear against live instance DB and verify."""
from __future__ import annotations

import shutil
import sqlite3
from collections import Counter
from pathlib import Path

LIVE_DB = Path(r"D:\Python\Mathproject_tvet_mathB\instance\kumon_math.db")
BACKUP = Path(r"D:\Python\Mathproject_tvet_mathB\reports\kumon_math_pre_delete_core_all.bak.db")


def _counts(con: sqlite3.Connection) -> dict:
    c = con.cursor()
    out = {}
    for t in [
        "skill_curriculum",
        "skills_info",
        "textbook_examples",
        "skill_prerequisites",
        "skill_family_bridge",
        "gencode_component_tracker",
        "questions",
        "users",
        "classes",
        "class_students",
    ]:
        try:
            out[t] = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        except Exception:
            out[t] = None
    out["curriculum_by"] = c.execute(
        "SELECT curriculum, COUNT(*) FROM skill_curriculum GROUP BY curriculum"
    ).fetchall()
    out["students"] = c.execute("SELECT COUNT(*) FROM users WHERE role='student'").fetchone()[0]
    out["admins"] = c.execute("SELECT COUNT(*) FROM users WHERE role='admin'").fetchone()[0]
    out["teachers"] = c.execute("SELECT COUNT(*) FROM users WHERE role='teacher'").fetchone()[0]
    return out


def main():
    print("=== BEFORE FK orphans ===")
    con = sqlite3.connect(str(LIVE_DB))
    rows = con.execute("PRAGMA foreign_key_check").fetchall()
    print("fk_total", len(rows), "by_table", dict(Counter(r[0] for r in rows)))
    before = _counts(con)
    print("before", before)
    con.close()

    shutil.copy2(LIVE_DB, BACKUP)
    print("backup", BACKUP)

    import config as _cfg
    from app import create_app
    from models import db, init_db
    from core.routes.admin import _hard_clear_core_data, _core_textbook_remaining_check
    from sqlalchemy import text

    # Point create_app at live DB explicitly
    uri = "sqlite:///" + str(LIVE_DB.resolve()).replace("\\", "/")
    _cfg.Config.SQLALCHEMY_DATABASE_URI = uri
    app = create_app()
    with app.app_context():
        # create_app may have run init_db; with non-empty skills it could reseed bridges.
        # Capture curriculum counts again after app boot.
        boot = {
            "skill_curriculum": db.session.execute(text("SELECT COUNT(*) FROM skill_curriculum")).scalar(),
            "skills_info": db.session.execute(text("SELECT COUNT(*) FROM skills_info")).scalar(),
            "bridge": db.session.execute(text("SELECT COUNT(*) FROM skill_family_bridge")).scalar(),
            "by_curr": db.session.execute(
                text("SELECT curriculum, COUNT(*) FROM skill_curriculum GROUP BY curriculum")
            ).fetchall(),
        }
        print("after_app_boot", boot)

        result = _hard_clear_core_data(execute=True)
        deleted = result["deleted"]
        print("deleted", {k: deleted.get(k) for k in sorted(deleted)})
        remaining = _core_textbook_remaining_check()
        print("remaining", remaining)

        db.session.execute(text("PRAGMA foreign_keys = ON"))
        fk_after = db.session.execute(text("PRAGMA foreign_key_check")).fetchall()
        print("fk_after_clear", len(fk_after), fk_after[:20] if fk_after else [])

        # Simulate restart seed guard
        init_db(db.engine, seed_bridges=False)
        after_restart = {
            "skill_curriculum": db.session.execute(text("SELECT COUNT(*) FROM skill_curriculum")).scalar(),
            "skills_info": db.session.execute(text("SELECT COUNT(*) FROM skills_info")).scalar(),
            "textbook_examples": db.session.execute(text("SELECT COUNT(*) FROM textbook_examples")).scalar(),
            "bridge": db.session.execute(text("SELECT COUNT(*) FROM skill_family_bridge")).scalar(),
            "questions": db.session.execute(text("SELECT COUNT(*) FROM questions")).scalar(),
            "students": db.session.execute(text("SELECT COUNT(*) FROM users WHERE role='student'")).scalar(),
            "admins": db.session.execute(text("SELECT COUNT(*) FROM users WHERE role='admin'")).scalar(),
            "teachers": db.session.execute(text("SELECT COUNT(*) FROM users WHERE role='teacher'")).scalar(),
        }
        print("after_restart_init", after_restart)
        fk_final = db.session.execute(text("PRAGMA foreign_key_check")).fetchall()
        print("fk_final", len(fk_final))
        if fk_final:
            print("FAIL fk residual", dict(Counter(r[0] for r in fk_final)))
            print("sample", fk_final[:30])
        else:
            print("PASS foreign_key_check=0")
        if any(int(v or 0) for v in remaining.values()):
            print("FAIL textbook remaining", remaining)
        else:
            print("PASS all textbook tables empty")


if __name__ == "__main__":
    main()
