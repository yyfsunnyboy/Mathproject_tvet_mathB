"""Read-only repair plan for B2 chapter 2 outline-bound textbook questions."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = PROJECT_ROOT / "instance" / "kumon_math.db"

PLAN = {
    11698: ("vh_數學B2_SubSection_2_2_3", "high", "仰角與斜邊構成直角三角形"),
    11699: ("vh_數學B2_SubSection_2_2_3", "high", "塔高與水平距離為直角三角形測量"),
    11700: ("vh_數學B2_SubSection_2_2_3", "high", "梯子、地面、樹構成直角三角形"),
    11701: ("vh_數學B2_SubSection_2_2_3", "high", "兩次仰角測高的直角三角形問題"),
    11702: ("vh_數學B2_SubSection_2_2_4", "high", "已知非直角三角形兩角一邊求邊"),
    11703: ("vh_數學B2_SubSection_2_2_4", "high", "已知兩邊及非直角夾角求第三邊"),
    11704: ("vh_數學B2_SubSection_2_2_3", "high", "折樹、地面構成直角三角形"),
    11705: ("vh_數學B2_SubSection_2_2_5", "high", "平面方位三角形結合樓高仰角的立體測量"),
    11706: ("", "unresolved", "同一題同時評量正弦定理與餘弦定理，無唯一 leaf"),
    11707: ("vh_數學B2_SubSection_2_1_1", "high", "兩邊夾角面積公式位於正弦定理單元"),
    11708: ("vh_數學B2_SubSection_2_1_1", "high", "兩角一邊與外接圓半徑使用正弦定理"),
    11709: ("vh_數學B2_SubSection_2_1_1", "high", "SSA 求角使用正弦定理"),
    11710: ("vh_數學B2_SubSection_2_1_1", "high", "SSA 求角使用正弦定理"),
    11711: ("vh_數學B2_SubSection_2_1_2", "high", "三邊求角使用餘弦定理"),
    11712: ("vh_數學B2_SubSection_2_1_2", "high", "三邊求角使用餘弦定理"),
    11714: ("vh_數學B2_SubSection_2_1_2", "high", "兩邊夾角求第三邊使用餘弦定理"),
    11715: ("vh_數學B2_SubSection_2_1_1", "high", "三邊求外接圓半徑使用擴充正弦定理"),
}


def build_plan(db_path: Path) -> list[dict[str, object]]:
    uri = f"file:{db_path.resolve().as_posix()}?mode=ro"
    with sqlite3.connect(uri, uri=True) as connection:
        connection.row_factory = sqlite3.Row
        placeholders = ",".join("?" for _ in PLAN)
        rows = connection.execute(
            f"SELECT id, skill_id, source_description FROM textbook_examples "
            f"WHERE id IN ({placeholders}) ORDER BY id",
            tuple(PLAN),
        ).fetchall()
    found = {int(row["id"]) for row in rows}
    missing = sorted(set(PLAN) - found)
    if missing:
        raise RuntimeError(f"Expected production rows are missing: {missing}")
    result = []
    for row in rows:
        question_id = int(row["id"])
        proposed, confidence, reason = PLAN[question_id]
        old_skill = str(row["skill_id"] or "")
        if not old_skill.startswith("outline_"):
            action = "NO_ACTION_ALREADY_LEAF"
        elif proposed and confidence == "high":
            action = "WOULD_REBIND"
        else:
            action = "KEEP_UNRESOLVED"
        result.append({
            "question_id": question_id,
            "old_skill": old_skill,
            "proposed_leaf": proposed,
            "confidence": confidence,
            "reason": reason,
            "action": action,
        })
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    args = parser.parse_args()
    rows = build_plan(args.db)
    print("question_id | old_skill | proposed_leaf | confidence/reason | action")
    for row in rows:
        print(
            f"{row['question_id']} | {row['old_skill']} | {row['proposed_leaf']} | "
            f"{row['confidence']}: {row['reason']} | {row['action']}"
        )
    print(f"rows={len(rows)} would_rebind={sum(r['action'] == 'WOULD_REBIND' for r in rows)} "
          f"unresolved={sum(r['action'] == 'KEEP_UNRESOLVED' for r in rows)} db_changes=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
