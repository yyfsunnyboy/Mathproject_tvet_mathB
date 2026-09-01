# -*- coding: utf-8 -*-
"""Backup production DB and apply practice_attempts schema."""
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from models import PracticeAttempt, db, init_db

DB_PATH = PROJECT_ROOT / "instance" / "kumon_math.db"
BACKUP_DIR = PROJECT_ROOT / "instance" / "backups"


def main() -> None:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"kumon_math_before_practice_attempts_{stamp}.db"
    shutil.copy2(DB_PATH, backup)
    if not backup.exists() or backup.stat().st_size < 1000:
        raise RuntimeError(f"Backup failed: {backup}")
    print(f"backup: {backup}")
    print(f"backup_size: {backup.stat().st_size}")

    app = create_app()
    with app.app_context():
        init_db(db.engine)
        cnt = PracticeAttempt.query.count()
        print(f"practice_attempts_count: {cnt}")

    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='practice_attempts'"
    ).fetchone()
    print(f"table_exists: {bool(row)}")
    conn.close()


if __name__ == "__main__":
    main()
