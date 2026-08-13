# -*- coding: utf-8 -*-
"""One-off inventory for B1 chapter 2 undeveloped probe candidates (readonly)."""
from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "instance" / "kumon_math.db"
OUT = ROOT / "reports" / "gencode_qwen_dryrun" / "_probe_preflight"
OUT.mkdir(parents=True, exist_ok=True)


def sha_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    # Production generate.py hashes
    prod_root = ROOT / "agent_skills_v3"
    prod_hashes = {}
    for p in sorted(prod_root.rglob("generate.py")):
        prod_hashes[p.relative_to(ROOT).as_posix()] = sha_file(p)
    (OUT / "production_generate_sha256_before.json").write_text(
        json.dumps(prod_hashes, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # DB hash
    db_hash = sha_file(DB) if DB.is_file() else None
    # tracker / manifest hashes if present
    extra = {}
    for rel in [
        "instance/kumon_math.db",
        "configs/gencode_taxonomy/k12_component_taxonomy.yaml",
    ]:
        p = ROOT / rel
        if p.is_file():
            extra[rel] = sha_file(p)
    # component manifests under agent_skills_v3
    for p in sorted(prod_root.rglob("component_manifest.json")):
        extra[p.relative_to(ROOT).as_posix()] = sha_file(p)

    (OUT / "system_hashes_before.json").write_text(
        json.dumps({"db": db_hash, "extra": extra, "prod_generate_count": len(prod_hashes)}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    cols = [r[1] for r in con.execute("PRAGMA table_info(textbook_examples)").fetchall()]
    print("COLS", cols)

    # Find chapter/section fields
    sample = con.execute(
        "SELECT * FROM textbook_examples WHERE skill_id LIKE 'vh_數學B1_%' LIMIT 1"
    ).fetchone()
    if sample:
        print("SAMPLE_KEYS", list(sample.keys()))

    # Try common chapter markers
    # Look at skill_info if exists
    tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    print("TABLES", tables)

    skill_meta = {}
    if "skill_info" in tables or "skills_info" in tables:
        tname = "skill_info" if "skill_info" in tables else "skills_info"
        scols = [r[1] for r in con.execute(f"PRAGMA table_info({tname})").fetchall()]
        print("SKILL_META_COLS", scols)
        rows = con.execute(f"SELECT * FROM {tname} WHERE skill_id LIKE 'vh_數學B1_%'").fetchall()
        for r in rows:
            d = dict(r)
            skill_meta[d.get("skill_id")] = d

    # Tracker statuses
    tracker = {}
    if "gencode_component_tracker" in tables:
        for r in con.execute(
            "SELECT textbook_example_id, skill_id, component_id, gencode_status FROM gencode_component_tracker"
        ).fetchall():
            tracker[int(r["textbook_example_id"])] = dict(r)

    # Production component ids
    prod_components = set()
    for p in prod_root.rglob("generate.py"):
        # agent_skills_v3/<skill>/components/src_XXXX/generate.py
        parts = p.parts
        if "components" in parts:
            i = parts.index("components")
            if i + 1 < len(parts):
                prod_components.add(parts[i + 1])

    dryrun_components = set()
    dry = ROOT / "reports" / "gencode_v3_dryrun"
    if dry.is_dir():
        for p in dry.rglob("generate.py"):
            parts = p.parts
            if "components" in parts:
                i = parts.index("components")
                if i + 1 < len(parts):
                    dryrun_components.add(parts[i + 1])

    # Chapter 2 heuristic via skill_info chapter/section or skill naming / curriculum order
    candidates = []
    examples = con.execute(
        """
        SELECT id, skill_id, problem_text, correct_answer, problem_type,
               source_description, source_chapter, source_section, source_volume,
               source_curriculum, notes
        FROM textbook_examples
        WHERE skill_id LIKE 'vh_數學B1_%'
        ORDER BY id
        """
    ).fetchall()

    for ex in examples:
        sid = str(ex["skill_id"] or "")
        meta = skill_meta.get(sid) or {}
        chapter = str(ex["source_chapter"] or meta.get("chapter") or "")
        section = str(ex["source_section"] or meta.get("section") or "")
        ch_name = str(meta.get("skill_ch_name") or "")
        raw_meta = {k: meta.get(k) for k in ("skill_ch_name", "category", "order_index")} if meta else {}
        candidates.append(
            {
                "id": int(ex["id"]),
                "skill_id": sid,
                "problem_type": ex["problem_type"],
                "problem_text": (ex["problem_text"] or "")[:180],
                "correct_answer": (ex["correct_answer"] or "")[:80],
                "source_volume": ex["source_volume"],
                "chapter": chapter,
                "section": section,
                "ch_name": ch_name,
                "meta_sample": raw_meta,
                "tracker": tracker.get(int(ex["id"])),
                "in_production": f"src_{ex['id']}" in prod_components,
                "in_dryrun": f"src_{ex['id']}" in dryrun_components,
            }
        )

    (OUT / "b1_examples_inventory.json").write_text(
        json.dumps(candidates, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Print chapter distribution from meta
    from collections import Counter

    ch_counter = Counter()
    for c in candidates:
        key = (c["chapter"], c["section"], c["ch_name"], c["skill_id"])
        ch_counter[key] += 1
    print("META_DIST_TOP")
    for k, v in list(ch_counter.most_common(40)):
        print(v, k)

    # Print skill_meta keys sample
    if skill_meta:
        first = next(iter(skill_meta.values()))
        print("FIRST_SKILL_META", json.dumps({k: first.get(k) for k in first.keys()}, ensure_ascii=False)[:2000])

    con.close()
    print("DONE prod_generate", len(prod_hashes), "examples", len(candidates))


if __name__ == "__main__":
    main()
