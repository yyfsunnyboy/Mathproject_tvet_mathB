from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.gencode.services.component_tracker_service import save_tracker_record

SKILL_ID = "vh_數學B1_DivisionPointCoordinates"
SOURCE_IDS = (4420, 4423, 4427, 4438, 4512, 4513)
SPEC_PATH = (
    PROJECT_ROOT
    / "reports"
    / "gencode_closed_loop"
    / "drafts"
    / f"{SKILL_ID}_phase2_generator_specs.json"
)


def _status_rows(conn: sqlite3.Connection, source_ids: tuple[int, ...]) -> dict[int, str]:
    placeholders = ",".join("?" for _ in source_ids)
    rows = conn.execute(
        f"""
        SELECT textbook_example_id, gencode_status
        FROM gencode_component_tracker
        WHERE textbook_example_id IN ({placeholders})
        """,
        source_ids,
    ).fetchall()
    return {int(row[0]): str(row[1]) for row in rows}


def main() -> int:
    specs = json.loads(SPEC_PATH.read_text(encoding="utf-8"))["generator_specs"]
    specs_by_source = {int(row["source_id"]): row for row in specs}
    conn = sqlite3.connect(PROJECT_ROOT / "instance" / "kumon_math.db")
    try:
        before = _status_rows(conn, (*SOURCE_IDS, 4421))
        for source_id in SOURCE_IDS:
            spec = dict(specs_by_source[source_id])
            payload = {
                "phase": "phase3",
                "phase3_validation": {
                    "status": "PASS",
                    "seeds": 10,
                    "component_id": f"src_{source_id}",
                },
                "generator_spec": spec,
                "publication": {
                    "published": False,
                    "publish_candidate": True,
                },
            }
            save_tracker_record(
                conn,
                textbook_example_id=source_id,
                skill_id=SKILL_ID,
                gencode_status="verified",
                induced_spec_payload=payload,
                gencode_error_log=None,
            )
        after = _status_rows(conn, (*SOURCE_IDS, 4421))
    finally:
        conn.close()
    print(
        json.dumps(
            {
                "before": {str(key): before.get(key) for key in (*SOURCE_IDS, 4421)},
                "after": {str(key): after.get(key) for key in (*SOURCE_IDS, 4421)},
                "updated_source_ids": list(SOURCE_IDS),
                "untouched_source_ids": [4421],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
