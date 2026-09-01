"""Read-only: export core backup from production DB and validate."""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
from sqlalchemy import create_engine, inspect, text

from core.backup.backup_registry import get_core_table_names
from core.backup.backup_validator import (
    MANIFEST_SHEET,
    build_and_validate_export,
    collect_source_counts,
    ensure_dataframe_columns,
    validate_legacy_workbook_structure,
)
from core.data_importer import ensure_core_export_dataframes

DB_PATH = Path("instance/kumon_math.db")
OUT_PATH = Path("reports/prod_core_backup_validated.xlsx")


def main():
    if not DB_PATH.exists():
        print("DB missing:", DB_PATH)
        return 1
    conn = sqlite3.connect(DB_PATH)
    print("integrity_check", conn.execute("PRAGMA integrity_check").fetchone()[0])
    print("fk_check_rows", len(conn.execute("PRAGMA foreign_key_check").fetchall()))
    conn.close()

    engine = create_engine("sqlite:///" + str(DB_PATH.resolve()).replace("\\", "/"))
    export_tables = get_core_table_names(include="export")
    source_counts = collect_source_counts(engine, export_tables)
    frames = {}
    for table in export_tables:
        try:
            df = pd.read_sql_table(table, engine)
        except Exception:
            df = pd.read_sql_query(f"SELECT * FROM {table}", engine)
        frames[table] = ensure_dataframe_columns(table, df, engine)
    ensure_core_export_dataframes(frames)

    payload, summary = build_and_validate_export(
        mode="core",
        engine=engine,
        frames=frames,
        expected_tables=export_tables,
        source_counts=source_counts,
        source_database_name=DB_PATH.name,
    )
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_bytes(payload)
    sheets = pd.read_excel(OUT_PATH, sheet_name=None, engine="openpyxl")
    print("VALID", summary)
    print("expected_tables", len(export_tables))
    print("actual_sheets", len(sheets))
    print("manifest", MANIFEST_SHEET in sheets)
    for key in ("users", "classes", "class_students", "practice_attempts"):
        db_n = source_counts.get(key, -1)
        sheet = sheets.get(key)
        xl_n = 0 if sheet is None else len(sheet.dropna(how="all"))
        cols = list(sheet.columns) if sheet is not None else []
        print(f"{key}: db={db_n} excel={xl_n} cols={cols[:8]}{'...' if len(cols)>8 else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
