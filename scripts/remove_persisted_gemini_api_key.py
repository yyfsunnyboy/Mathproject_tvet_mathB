"""Safely remove the legacy Gemini API key row from system_settings.

This command is dry-run by default.  It refuses to delete anything unless an
operator supplies an already-created backup file as an explicit acknowledgement.
The backup itself is intentionally not created here because legacy full exports
may contain the credential that this migration is designed to remove.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from app import create_app
from core.ai_settings import SETTING_GEMINI_API_KEY
from models import SystemSetting, db


def main() -> int:
    parser = argparse.ArgumentParser(description="Remove legacy persisted Gemini API key")
    parser.add_argument("--execute", action="store_true", help="perform deletion (otherwise dry-run)")
    parser.add_argument("--confirmed-backup", type=Path, help="existing backup created before this migration")
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        row = SystemSetting.query.filter_by(key=SETTING_GEMINI_API_KEY).first()
        print(f"legacy_secret_row_present={bool(row)}")
        if not args.execute:
            print("dry_run=true; no database changes made")
            return 0
        if not args.confirmed_backup or not args.confirmed_backup.is_file():
            parser.error("--execute requires --confirmed-backup pointing to an existing pre-migration backup")
        if row:
            db.session.delete(row)
            db.session.commit()
            print("legacy_secret_row_removed=true")
        else:
            print("legacy_secret_row_removed=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
