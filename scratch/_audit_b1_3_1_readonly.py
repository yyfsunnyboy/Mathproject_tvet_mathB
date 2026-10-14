# -*- coding: utf-8 -*-
"""Read-only audit for B1 section 3-1 Gencode V3 / Phase 2 status."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "instance" / "kumon_math.db"
SKILLS = [
    "vh_數學B1_PolynomialBasicConcepts",
    "vh_數學B1_PolynomialArithmeticOperations",
    "vh_數學B1_PolynomialEquality",
]


def _row_to_dict(row: sqlite3.Row) -> dict:
    return {k: row[k] for k in row.keys()}


def main() -> None:
    conn = sqlite3.connect(str(DB))
    conn.row_factory = sqlite3.Row

    # schema probe
    te_cols = [r[1] for r in conn.execute("PRAGMA table_info(textbook_examples)").fetchall()]
    print("TE_COLS", te_cols)
    tracker_exists = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='gencode_component_tracker'"
    ).fetchone()
    print("TRACKER_EXISTS", bool(tracker_exists))
    if tracker_exists:
        tr_cols = [r[1] for r in conn.execute("PRAGMA table_info(gencode_component_tracker)").fetchall()]
        print("TRACKER_COLS", tr_cols)

    rows = conn.execute(
        f"""
        SELECT *
        FROM textbook_examples
        WHERE skill_id IN ({",".join("?" for _ in SKILLS)})
        ORDER BY skill_id, id
        """,
        SKILLS,
    ).fetchall()
    print("EXAMPLE_COUNT", len(rows))
    by_skill: dict[str, int] = {}
    for r in rows:
        sid = str(r["skill_id"] or "")
        by_skill[sid] = by_skill.get(sid, 0) + 1
    print("BY_SKILL", by_skill)

    # Also check section-related filters if columns exist
    for col in ("chapter", "section", "unit", "volume", "curriculum", "source_description"):
        if col in te_cols:
            sample = conn.execute(
                f"SELECT DISTINCT {col} FROM textbook_examples WHERE skill_id IN ({','.join('?' for _ in SKILLS)}) LIMIT 20",
                SKILLS,
            ).fetchall()
            print(f"DISTINCT_{col}", [x[0] for x in sample])

    inventory = []
    for r in rows:
        d = _row_to_dict(r)
        eid = int(d["id"])
        skill_id = str(d.get("skill_id") or "")
        component_id = f"src_{eid}"

        # tracker
        tracker = None
        if tracker_exists:
            tr = conn.execute(
                "SELECT * FROM gencode_component_tracker WHERE textbook_example_id = ?",
                (eid,),
            ).fetchone()
            if tr is None:
                tr = conn.execute(
                    "SELECT * FROM gencode_component_tracker WHERE component_id = ?",
                    (component_id,),
                ).fetchone()
            if tr is not None:
                tracker = _row_to_dict(tr)

        # filesystem components under agent_skills_v3 and dryrun
        paths = {
            "prod": ROOT / "agent_skills_v3" / skill_id / "components" / component_id,
            "dryrun": ROOT / "reports" / "gencode_v3_dryrun" / skill_id / "components" / component_id,
            "staging": ROOT
            / "reports"
            / "gencode_v3_publish_staging"
            / skill_id
            / "components"
            / component_id,
        }
        fs = {}
        for label, p in paths.items():
            fs[label] = {
                "exists": p.is_dir(),
                "generate": (p / "generate.py").is_file(),
                "metadata": (p / "metadata.py").is_file(),
                "get_hint": (p / "get_hint.py").is_file(),
                "path": str(p) if p.is_dir() else None,
            }

        # induced / phase1 artifacts
        induced = ROOT / "reports" / "gencode_closed_loop" / "induced_specs" / f"{skill_id}.json"
        inventory.append(
            {
                "textbook_example_id": eid,
                "component_id": component_id,
                "skill_id": skill_id,
                "problem_type": d.get("problem_type"),
                "problem_text_preview": str(d.get("problem_text") or "")[:120].replace("\n", " "),
                "source_description": d.get("source_description"),
                "correct_answer_preview": str(d.get("correct_answer") or "")[:80],
                "tracker": {
                    "found": tracker is not None,
                    "gencode_status": (tracker or {}).get("gencode_status"),
                    "component_id": (tracker or {}).get("component_id"),
                    "problem_type_id": (tracker or {}).get("problem_type_id"),
                    "induced_spec_payload_preview": str((tracker or {}).get("induced_spec_payload") or "")[:200],
                    "keys": sorted((tracker or {}).keys()),
                }
                if tracker_exists
                else {"found": False},
                "filesystem": fs,
                "induced_spec_exists": induced.is_file(),
            }
        )

    out = ROOT / "scratch" / "_b1_3_1_readonly_inventory.json"
    out.write_text(json.dumps(inventory, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print("WROTE", out)

    # summarize statuses
    status_counts: dict[str, int] = {}
    for item in inventory:
        st = (item.get("tracker") or {}).get("gencode_status") or "NO_TRACKER"
        status_counts[st] = status_counts.get(st, 0) + 1
    print("STATUS_COUNTS", status_counts)

    prod_components = sum(1 for i in inventory if i["filesystem"]["prod"]["exists"])
    dryrun_components = sum(1 for i in inventory if i["filesystem"]["dryrun"]["exists"])
    print("PROD_COMPONENT_DIRS", prod_components)
    print("DRYRUN_COMPONENT_DIRS", dryrun_components)

    # print compact table lines
    for item in inventory:
        tr = item["tracker"]
        fs = item["filesystem"]
        print(
            f"{item['textbook_example_id']}\t{item['component_id']}\t{item['skill_id']}\t"
            f"pt={item.get('problem_type')}\ttracker={tr.get('gencode_status')}\t"
            f"prod={fs['prod']['exists']}\tdryrun={fs['dryrun']['exists']}\t"
            f"preview={item['problem_text_preview'][:60]}"
        )

    conn.close()


if __name__ == "__main__":
    main()
