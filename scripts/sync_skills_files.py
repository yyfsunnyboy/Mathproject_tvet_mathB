"""Read-only skill inventory for the V3 workflow.

Generation is managed from /skills. This script deliberately does not write
skill files, prompts, or generator data.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sqlite3
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-id", help="Optional skill ID to inspect")
    parser.add_argument("--db", type=Path, default=PROJECT_ROOT / "instance" / "kumon_math.db")
    args = parser.parse_args()

    from core.gencode.services.v3_skill_capability_preflight_service import evaluate_skill_v3_capability

    uri = f"file:{args.db.resolve().as_posix()}?mode=ro"
    with sqlite3.connect(uri, uri=True) as connection:
        if args.skill_id:
            rows = connection.execute("SELECT skill_id FROM skills_info WHERE skill_id = ?", (args.skill_id,))
        else:
            rows = connection.execute("SELECT skill_id FROM skills_info ORDER BY skill_id")
        skill_ids = [row[0] for row in rows if not row[0].startswith("outline_")]
        for skill_id in skill_ids:
            capability = evaluate_skill_v3_capability(connection, skill_id, probe_examples=False)
            print(f"{skill_id}\t{capability['capability_status']}\t{capability['textbook_example_count']} examples")
    print("建立、補全及重建 V3 出題能力：請使用 /skills。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
