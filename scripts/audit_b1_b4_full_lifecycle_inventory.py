# -*- coding: utf-8 -*-
"""Full read-only inventory of vocational math B1-B4 textbook examples."""
from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.gencode.services.component_tracker_service import derive_component_id
from core.gencode.services.gencode_status_query_service import (
    build_admin_examples_gencode_status_map,
    build_admin_skills_gencode_status_map,
    _parse_payload_dict,
)

VOLUMES = ("數學B1", "數學B2", "數學B3", "數學B4")
DRYRUN = "reports/gencode_v3_dryrun"
PROD = "agent_skills_v3"


def _sha(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _classify(row: dict) -> str:
    status = str(row.get("tracker_status") or "")
    has_dry = bool(row.get("dryrun_generate_exists"))
    has_prod = bool(row.get("production_generate_exists"))
    hash_ok = bool(row.get("dryrun_prod_hash_match"))
    stale = bool(row.get("hash_evidence_stale"))
    has_tracker = bool(row.get("tracker_exists"))
    teacher = str(row.get("teacher_status_key") or "")

    if status in {"generating", "running", "queued"} or teacher == "generating":
        return "真正生成中"
    if status == "failed" or teacher == "failed":
        return "驗證失敗"
    if has_dry and has_prod and not hash_ok:
        return "dryrun／production不一致"
    if has_prod and has_tracker and status in {"verified", "smoke_passed"} and not stale and hash_ok:
        return "已驗證且已上線"
    if has_prod and has_tracker and status in {"verified", "smoke_passed"} and stale:
        return "已部署，待重新驗證"
    if has_prod and not has_tracker:
        return "tracker缺失"
    if has_dry and not has_prod:
        return "只有dryrun"
    if has_prod and has_tracker and status not in {"verified", "smoke_passed", "failed", "generating"}:
        # draft_written / pending / etc with production present
        return "已部署，待重新驗證"
    if not has_dry and not has_prod:
        if has_tracker and status not in {"", "not_created", "None"}:
            return "產物缺失"
        return "尚未開發"
    if has_prod:
        return "已部署，待重新驗證"
    return "產物缺失"


def main() -> int:
    db = ROOT / "instance" / "kumon_math.db"
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row

    # Explicit B2/B3 absence check
    volume_presence = {}
    for vol in VOLUMES:
        volume_presence[vol] = {
            "examples": int(
                conn.execute(
                    "SELECT COUNT(*) c FROM textbook_examples WHERE source_volume = ?",
                    (vol,),
                ).fetchone()["c"]
            ),
            "curriculum_skills": int(
                conn.execute(
                    "SELECT COUNT(DISTINCT skill_id) c FROM skill_curriculum WHERE volume = ?",
                    (vol,),
                ).fetchone()["c"]
            ),
            "skills_info": int(
                conn.execute(
                    "SELECT COUNT(*) c FROM skills_info WHERE skill_id LIKE ?",
                    (f"vh_{vol}_%",),
                ).fetchone()["c"]
            ),
        }

    rows = conn.execute(
        """
        SELECT
            te.id AS textbook_example_id,
            te.skill_id,
            te.source_volume,
            te.source_chapter,
            te.source_section,
            te.source_description,
            te.problem_type,
            sc.curriculum,
            sc.grade,
            sc.display_order
        FROM textbook_examples te
        LEFT JOIN skill_curriculum sc
          ON sc.skill_id = te.skill_id
        WHERE te.source_volume IN ('數學B1', '數學B2', '數學B3', '數學B4')
           OR te.skill_id LIKE 'vh_數學B1_%'
           OR te.skill_id LIKE 'vh_數學B2_%'
           OR te.skill_id LIKE 'vh_數學B3_%'
           OR te.skill_id LIKE 'vh_數學B4_%'
        ORDER BY te.source_volume, te.source_chapter, te.source_section, te.id
        """
    ).fetchall()

    # Deduplicate by textbook_example_id (skill_curriculum join may multiply)
    by_id: dict[int, dict] = {}
    for r in rows:
        eid = int(r["textbook_example_id"])
        if eid in by_id:
            continue
        skill_id = str(r["skill_id"])
        component_id = derive_component_id(eid)
        dry = ROOT / DRYRUN / skill_id / "components" / component_id / "generate.py"
        prod = ROOT / PROD / skill_id / "components" / component_id / "generate.py"
        wrapper = ROOT / "skills" / f"{skill_id}.py"
        manifest = ROOT / PROD / skill_id / "component_manifest.json"
        dry_hash = _sha(dry)
        prod_hash = _sha(prod)
        tracker = conn.execute(
            """
            SELECT gencode_status, induced_spec_payload, updated_at, component_id
            FROM gencode_component_tracker
            WHERE textbook_example_id = ?
            """,
            (eid,),
        ).fetchone()
        payload = _parse_payload_dict(tracker["induced_spec_payload"] if tracker else None)
        verified_hash = str(payload.get("verified_generate_sha256") or "").strip() or None
        published_hash = str(payload.get("published_generate_sha256") or "").strip() or None
        tracker_status = str(tracker["gencode_status"]) if tracker else None
        hash_evidence_stale = False
        if tracker_status in {"verified", "smoke_passed"}:
            if verified_hash and dry_hash and verified_hash != dry_hash:
                hash_evidence_stale = True
            if published_hash and prod_hash and published_hash != prod_hash:
                hash_evidence_stale = True

        item = {
            "textbook_example_id": eid,
            "source_id": f"src_{eid}",
            "component_id": component_id,
            "skill_id": skill_id,
            "volume": str(r["source_volume"] or ""),
            "chapter": str(r["source_chapter"] or ""),
            "section": str(r["source_section"] or ""),
            "source_description": str(r["source_description"] or ""),
            "problem_type": str(r["problem_type"] or ""),
            "tracker_exists": tracker is not None,
            "tracker_status": tracker_status,
            "tracker_updated_at": tracker["updated_at"] if tracker else None,
            "dryrun_generate_exists": dry.is_file(),
            "production_generate_exists": prod.is_file(),
            "wrapper_exists": wrapper.is_file(),
            "manifest_exists": manifest.is_file(),
            "dryrun_hash": dry_hash,
            "production_hash": prod_hash,
            "verified_generate_sha256": verified_hash,
            "published_generate_sha256": published_hash,
            "dryrun_prod_hash_match": bool(dry_hash and prod_hash and dry_hash == prod_hash),
            "hash_evidence_stale": hash_evidence_stale,
        }
        by_id[eid] = item

    # Batch teacher-facing status (examples page semantics)
    examples = [(eid, item["skill_id"]) for eid, item in by_id.items()]
    # Process in chunks to keep memory reasonable
    chunk = 200
    for i in range(0, len(examples), chunk):
        part = examples[i : i + chunk]
        emap = build_admin_examples_gencode_status_map(conn, part, project_root=ROOT)
        for eid, _skill in part:
            view = emap.get(eid) or {}
            ts = view.get("teacher_status") or {}
            by_id[eid]["teacher_status_key"] = ts.get("status_key")
            by_id[eid]["teacher_status_label"] = ts.get("label")
            by_id[eid]["production_contains_latest"] = bool(view.get("production_contains_latest"))

    for item in by_id.values():
        item["classification"] = _classify(item)

    items = list(by_id.values())
    items.sort(key=lambda x: (x["volume"], x["chapter"], x["section"], x["textbook_example_id"]))

    # Skill-level summary
    skill_ids = sorted({item["skill_id"] for item in items})
    skill_map = build_admin_skills_gencode_status_map(conn, skill_ids, project_root=ROOT)

    # Stats
    by_volume = Counter(item["volume"] for item in items)
    by_class = Counter(item["classification"] for item in items)
    by_volume_class: dict[str, Counter] = defaultdict(Counter)
    by_chapter: dict[str, dict] = {}
    for item in items:
        key = f"{item['volume']}||{item['chapter']}||{item['section']}"
        by_volume_class[item["volume"]][item["classification"]] += 1
        slot = by_chapter.setdefault(
            key,
            {
                "volume": item["volume"],
                "chapter": item["chapter"],
                "section": item["section"],
                "total": 0,
                "classifications": Counter(),
                "example_ids": [],
            },
        )
        slot["total"] += 1
        slot["classifications"][item["classification"]] += 1
        slot["example_ids"].append(item["textbook_example_id"])

    repairable = [
        item
        for item in items
        if item["classification"] in {"tracker缺失", "已部署，待重新驗證"}
        and item["dryrun_generate_exists"]
        and item["production_generate_exists"]
        and item["dryrun_prod_hash_match"]
    ]
    blocked = [
        item
        for item in items
        if item["classification"]
        in {
            "產物缺失",
            "只有dryrun",
            "dryrun／production不一致",
            "驗證失敗",
            "尚未開發",
            "真正生成中",
        }
    ]

    chapter_rows = []
    for key in sorted(by_chapter.keys()):
        slot = by_chapter[key]
        chapter_rows.append(
            {
                "volume": slot["volume"],
                "chapter": slot["chapter"],
                "section": slot["section"],
                "total": slot["total"],
                "classifications": dict(slot["classifications"]),
            }
        )

    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "volume_presence": volume_presence,
        "total_examples": len(items),
        "by_volume": dict(by_volume),
        "by_classification": dict(by_class),
        "by_volume_classification": {
            vol: dict(counter) for vol, counter in by_volume_class.items()
        },
        "chapters": chapter_rows,
        "skill_status": {
            sid: {
                "teacher_status_key": (skill_map.get(sid) or {}).get("teacher_status", {}).get("status_key"),
                "teacher_status_label": (skill_map.get(sid) or {}).get("teacher_status", {}).get("label"),
                "verified_count": (skill_map.get(sid) or {}).get("verified_count"),
                "published_count": (skill_map.get(sid) or {}).get("published_count"),
                "total_examples": (skill_map.get(sid) or {}).get("total_examples"),
                "missing_tracker_count": (skill_map.get(sid) or {}).get("missing_tracker_count"),
                "stale_hash_count": (skill_map.get(sid) or {}).get("stale_hash_count"),
            }
            for sid in skill_ids
        },
        "repairable_count": len(repairable),
        "repairable_ids": [item["textbook_example_id"] for item in repairable],
        "repairable_by_skill": {
            skill: [i["textbook_example_id"] for i in repairable if i["skill_id"] == skill]
            for skill in sorted({i["skill_id"] for i in repairable})
        },
        "blocked_count": len(blocked),
        "blocked_by_classification": {
            cls: [i["textbook_example_id"] for i in blocked if i["classification"] == cls]
            for cls in sorted({i["classification"] for i in blocked})
        },
        "items": items,
    }

    out = ROOT / "reports" / "gencode_closed_loop" / "b1_b4_full_lifecycle_inventory.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    # Compact summary for stdout
    summary = {
        "report": str(out),
        "volume_presence": volume_presence,
        "total_examples": len(items),
        "by_volume": dict(by_volume),
        "by_classification": dict(by_class),
        "by_volume_classification": report["by_volume_classification"],
        "chapter_count": len(chapter_rows),
        "repairable_count": len(repairable),
        "blocked_count": len(blocked),
        "skills_scanned": len(skill_ids),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
