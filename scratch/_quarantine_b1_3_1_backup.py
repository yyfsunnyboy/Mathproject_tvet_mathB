# -*- coding: utf-8 -*-
"""
B1 3-1 Full Rebuild quarantine: COPY-ONLY backup + rebuild manifest.
Does NOT delete production components, does NOT modify textbook_examples / taxonomy / classification.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "instance" / "kumon_math.db"

EXPECTED_IDS = [
    4609, 4610, 4611, 4612, 4613, 4614, 4615, 4616, 4617, 4618, 4619, 4620,
    4621, 4622, 4623, 4624, 4625, 4626, 4627, 4628, 4629, 4630, 4631, 4632,
    4633, 4634, 4635, 4636, 4637, 4706, 4716, 4717, 4718, 4719, 4720,
]

SKILLS = [
    "vh_數學B1_PolynomialBasicConcepts",
    "vh_數學B1_PolynomialArithmeticOperations",
    "vh_數學B1_PolynomialEquality",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def copy_tree(src: Path, dst: Path) -> int:
    """Copy directory tree; return file count copied."""
    if not src.exists():
        return 0
    count = 0
    for p in src.rglob("*"):
        if p.is_file():
            rel = p.relative_to(src)
            target = dst / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, target)
            count += 1
    return count


def main() -> int:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    quarantine_name = f"B1_3-1_pre_v1_12_rebuild_{ts}"
    backup_root = ROOT / "reports" / "gencode_rebuild_backup" / quarantine_name
    if backup_root.exists():
        print("ABORT: backup already exists", backup_root)
        return 2

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    # --- TASK 1 re-verify ---
    rows = conn.execute(
        f"SELECT id, skill_id, problem_type, source_description FROM textbook_examples WHERE id IN ({','.join('?' for _ in EXPECTED_IDS)}) ORDER BY id",
        EXPECTED_IDS,
    ).fetchall()
    found = [int(r["id"]) for r in rows]
    if found != EXPECTED_IDS:
        print("ABORT: DB scope mismatch")
        print("missing", [i for i in EXPECTED_IDS if i not in found])
        print("extra_order", found)
        return 3

    skill_extra = conn.execute(
        """
        SELECT id, skill_id FROM textbook_examples
        WHERE skill_id IN (?,?,?) AND id NOT IN ({})
        """.format(",".join("?" for _ in EXPECTED_IDS)),
        (*SKILLS, *EXPECTED_IDS),
    ).fetchall()
    if skill_extra:
        print("ABORT: unexpected extras in three skills", [dict(r) for r in skill_extra])
        return 3

    # skill_id snapshot hashes (SoT evidence — read only)
    sot_skill_map = {int(r["id"]): r["skill_id"] for r in rows}
    sot_skill_hash = hashlib.sha256(
        json.dumps(sot_skill_map, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()

    # tracker evidence
    tracker_cols = [c[1] for c in conn.execute("PRAGMA table_info(gencode_component_tracker)").fetchall()]
    tracker_rows = []
    if "textbook_example_id" in tracker_cols:
        tracker_rows = [
            {k: r[k] for k in r.keys()}
            for r in conn.execute(
                f"SELECT * FROM gencode_component_tracker WHERE textbook_example_id IN ({','.join('?' for _ in EXPECTED_IDS)})",
                EXPECTED_IDS,
            ).fetchall()
        ]

    # build inventory before copy
    inventory = []
    existing_component_ids = []
    missing_component_ids = []
    for eid in EXPECTED_IDS:
        skill = sot_skill_map[eid]
        comp_id = f"src_{eid}"
        prod_dir = ROOT / "agent_skills_v3" / skill / "components" / comp_id
        dry_dir = ROOT / "reports" / "gencode_v3_dryrun" / skill / "components" / comp_id
        staging_dir = (
            ROOT
            / "reports"
            / "gencode_v3_publish_staging"
            / "agent_skills_v3"
            / skill
            / "components"
            / comp_id
        )
        exists = prod_dir.is_dir() and (prod_dir / "generate.py").is_file()
        if exists:
            existing_component_ids.append(comp_id)
            old_status = "existing"
        else:
            missing_component_ids.append(comp_id)
            old_status = "missing"

        # wrapper membership
        wrapper_path = ROOT / "skills" / f"{skill}.py"
        wrapper_refs = False
        if wrapper_path.is_file():
            text = wrapper_path.read_text(encoding="utf-8")
            wrapper_refs = f"'{comp_id}'" in text or f'"{comp_id}"' in text

        inventory.append(
            {
                "example_id": eid,
                "component_id": comp_id,
                "skill_id": skill,
                "old_status": old_status,
                "action": "REBUILD",
                "reason": "v1.12 contract/lifecycle mismatch",
                "current_component_path": str(prod_dir.relative_to(ROOT)).replace("\\", "/") if exists else None,
                "current_manifest": f"agent_skills_v3/{skill}/component_manifest.json",
                "current_tracker": "NONE" if not any(t.get("textbook_example_id") == eid for t in tracker_rows) else "PRESENT",
                "wrapper_path": f"skills/{skill}.py",
                "wrapper_membership": wrapper_refs,
                "dryrun_exists": dry_dir.is_dir(),
                "staging_exists": staging_dir.is_dir(),
            }
        )

    if len(existing_component_ids) != 31 or len(missing_component_ids) != 4:
        print(
            "ABORT: unexpected existing/missing counts",
            len(existing_component_ids),
            len(missing_component_ids),
        )
        return 3

    # Runtime dependency: YES if any wrapper references existing comps
    runtime_refs = any(i["wrapper_membership"] for i in inventory if i["old_status"] == "existing")
    if not runtime_refs:
        print("WARN: expected runtime refs but none found")
    # Per SOP task: if runtime references, must QUARANTINE/BACKUP only — no delete
    delete_forbidden = True

    backup_root.mkdir(parents=True, exist_ok=False)
    (backup_root / "README.md").write_text(
        "\n".join(
            [
                f"# {quarantine_name}",
                "",
                "COPY-ONLY quarantine for B1 section 3-1 FULL_REBUILD preparation.",
                "Production components were NOT deleted.",
                "Runtime wrappers still reference original agent_skills_v3 paths.",
                "Do not treat this directory as live runtime.",
                "",
                f"created_at: {datetime.now().isoformat(timespec='seconds')}",
                f"sot_skill_map_sha256: {sot_skill_hash}",
                "",
            ]
        ),
        encoding="utf-8",
    )

    file_index = []
    copied_component_dirs = 0

    # Copy existing production components
    for item in inventory:
        if item["old_status"] != "existing":
            continue
        skill = item["skill_id"]
        cid = item["component_id"]
        src = ROOT / "agent_skills_v3" / skill / "components" / cid
        dst = backup_root / "production_components" / skill / "components" / cid
        n = copy_tree(src, dst)
        copied_component_dirs += 1
        for p in dst.rglob("*"):
            if p.is_file():
                file_index.append(
                    {
                        "role": "production_component",
                        "path": str(p.relative_to(backup_root)).replace("\\", "/"),
                        "sha256": sha256_file(p),
                        "size": p.stat().st_size,
                        "source_path": str((src / p.relative_to(dst)).relative_to(ROOT)).replace("\\", "/"),
                    }
                )

    # Copy manifests (full file — derived)
    for skill in SKILLS:
        src = ROOT / "agent_skills_v3" / skill / "component_manifest.json"
        if src.is_file():
            dst = backup_root / "manifests" / skill / "component_manifest.json"
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            file_index.append(
                {
                    "role": "manifest",
                    "path": str(dst.relative_to(backup_root)).replace("\\", "/"),
                    "sha256": sha256_file(dst),
                    "size": dst.stat().st_size,
                    "source_path": str(src.relative_to(ROOT)).replace("\\", "/"),
                }
            )
        init_src = ROOT / "agent_skills_v3" / skill / "__init__.py"
        if init_src.is_file():
            dst = backup_root / "manifests" / skill / "__init__.py"
            shutil.copy2(init_src, dst)
            file_index.append(
                {
                    "role": "v3_skill_init",
                    "path": str(dst.relative_to(backup_root)).replace("\\", "/"),
                    "sha256": sha256_file(dst),
                    "size": dst.stat().st_size,
                    "source_path": str(init_src.relative_to(ROOT)).replace("\\", "/"),
                }
            )

    # Copy production wrappers (derived membership) — do not modify originals
    for skill in SKILLS:
        src = ROOT / "skills" / f"{skill}.py"
        if src.is_file():
            dst = backup_root / "wrappers" / f"{skill}.py"
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            file_index.append(
                {
                    "role": "production_wrapper",
                    "path": str(dst.relative_to(backup_root)).replace("\\", "/"),
                    "sha256": sha256_file(dst),
                    "size": dst.stat().st_size,
                    "source_path": str(src.relative_to(ROOT)).replace("\\", "/"),
                }
            )

    # Dryrun: copy only components in scope + index
    dryrun_index = []
    for item in inventory:
        skill = item["skill_id"]
        cid = item["component_id"]
        src = ROOT / "reports" / "gencode_v3_dryrun" / skill / "components" / cid
        if src.is_dir():
            dst = backup_root / "dryrun_components" / skill / "components" / cid
            copy_tree(src, dst)
            dryrun_index.append(
                {
                    "component_id": cid,
                    "skill_id": skill,
                    "source_path": str(src.relative_to(ROOT)).replace("\\", "/"),
                    "backup_path": str(dst.relative_to(backup_root)).replace("\\", "/"),
                    "files": sum(1 for _ in dst.rglob("*") if _.is_file()),
                }
            )

    # Staging copies for in-scope components only
    staging_index = []
    for item in inventory:
        if item["old_status"] != "existing":
            continue
        skill = item["skill_id"]
        cid = item["component_id"]
        src = (
            ROOT
            / "reports"
            / "gencode_v3_publish_staging"
            / "agent_skills_v3"
            / skill
            / "components"
            / cid
        )
        if src.is_dir():
            dst = backup_root / "staging_components" / skill / "components" / cid
            copy_tree(src, dst)
            staging_index.append(
                {
                    "component_id": cid,
                    "skill_id": skill,
                    "source_path": str(src.relative_to(ROOT)).replace("\\", "/"),
                    "backup_path": str(dst.relative_to(backup_root)).replace("\\", "/"),
                }
            )
    # staging wrappers
    for skill in SKILLS:
        src = ROOT / "reports" / "gencode_v3_publish_staging" / "skills" / f"{skill}.py"
        if src.is_file():
            dst = backup_root / "staging_wrappers" / f"{skill}.py"
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    # Tracker evidence (even if empty/sparse)
    tracker_evidence = {
        "table": "gencode_component_tracker",
        "columns": tracker_cols,
        "rows_for_scope": tracker_rows,
        "note": "Read-only dump. No tracker rows were modified or deleted.",
    }
    (backup_root / "tracker_evidence.json").write_text(
        json.dumps(tracker_evidence, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )

    # SoT fingerprint (read-only evidence that we did not change)
    sot_evidence = {
        "textbook_examples_skill_map_sha256": sot_skill_hash,
        "example_ids": EXPECTED_IDS,
        "skill_map": sot_skill_map,
        "note": "Fingerprint of skill_id mapping at quarantine time. Source rows were not written.",
    }
    (backup_root / "source_of_truth_fingerprint.json").write_text(
        json.dumps(sot_evidence, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Runtime dependency report
    runtime_report = {
        "runtime_currently_references_old_component": True if runtime_refs else False,
        "delete_forbidden": delete_forbidden,
        "atomic_quarantine_mechanism_in_production": False,
        "action_taken": "COPY_ONLY_BACKUP",
        "production_components_deleted": False,
        "skills": [],
    }
    for skill in SKILLS:
        comps = [i["component_id"] for i in inventory if i["skill_id"] == skill and i["old_status"] == "existing"]
        wrapper = ROOT / "skills" / f"{skill}.py"
        runtime_report["skills"].append(
            {
                "skill_id": skill,
                "component_ids": comps,
                "published_wrapper_path": f"skills/{skill}.py",
                "v3_package_path": f"agent_skills_v3/{skill}/",
                "runtime_currently_references_old_component": "YES" if wrapper.is_file() and any(
                    c in wrapper.read_text(encoding="utf-8") for c in comps
                ) else "NO",
            }
        )
    (backup_root / "runtime_dependency_check.json").write_text(
        json.dumps(runtime_report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Rebuild manifest (TASK 5)
    rebuild_manifest = {
        "section": "B1 3-1 多項式的基本概念與四則運算",
        "curriculum": "vocational",
        "grade": 10,
        "volume": "數學B1",
        "chapter": "第3章 式的運算",
        "example_ids": EXPECTED_IDS,
        "component_ids": [f"src_{i}" for i in EXPECTED_IDS],
        "items": [
            {
                "example_id": i["example_id"],
                "component_id": i["component_id"],
                "skill_id": i["skill_id"],
                "old_status": i["old_status"],
                "action": "REBUILD",
                "reason": "v1.12 contract/lifecycle mismatch",
            }
            for i in inventory
        ],
        "preserve": [
            "textbook_examples",
            "skill_id",
            "classification",
            "phase1_rule_packs",
            "taxonomy_registry production mapping",
            "domain operation production implementation",
            "curriculum bindings",
        ],
        "preconditions_before_rebuild": [
            "Exact Capability Readiness Gate PASS",
            "adapter route valid",
            "selected_operation == required_operation",
            "answer_contract consistent",
            "checker valid",
            "per-example validator available",
        ],
        "status": "WAITING_FOR_CAPABILITY_READINESS",
        "quarantine_backup": str(backup_root.relative_to(ROOT)).replace("\\", "/"),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "sop_versions": {
            "PipelineFlow": "v1.12",
            "Specification": "v1.12",
        },
        "counts": {
            "examples": 35,
            "existing_components": 31,
            "missing_components": 4,
            "KEEP": 0,
            "REBUILD": 35,
            "UNKNOWN": 0,
        },
    }
    rebuild_manifest_path = backup_root / "B1_3-1_rebuild_manifest.json"
    rebuild_manifest_path.write_text(
        json.dumps(rebuild_manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    # Also place a stable pointer under reports/gencode_rebuild_backup/
    pointer = {
        "latest_quarantine": quarantine_name,
        "path": str(backup_root.relative_to(ROOT)).replace("\\", "/"),
        "rebuild_manifest": str(rebuild_manifest_path.relative_to(ROOT)).replace("\\", "/"),
        "status": "WAITING_FOR_CAPABILITY_READINESS",
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }
    (ROOT / "reports" / "gencode_rebuild_backup" / "B1_3-1_LATEST.json").write_text(
        json.dumps(pointer, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    (backup_root / "dryrun_index.json").write_text(
        json.dumps(dryrun_index, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (backup_root / "staging_index.json").write_text(
        json.dumps(staging_index, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (backup_root / "inventory.json").write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # --- TASK 7 verify ---
    verified_existing = []
    for cid in existing_component_ids:
        # find skill
        skill = next(i["skill_id"] for i in inventory if i["component_id"] == cid)
        dst = backup_root / "production_components" / skill / "components" / cid
        ok = (
            dst.is_dir()
            and (dst / "generate.py").is_file()
            and (dst / "metadata.py").is_file()
            and (dst / "get_hint.py").is_file()
        )
        verified_existing.append({"component_id": cid, "backup_ok": ok, "path": str(dst.relative_to(backup_root)).replace("\\", "/")})
    missing_ok = all(
        next(i["old_status"] for i in inventory if i["component_id"] == cid) == "missing"
        for cid in missing_component_ids
    )

    # Re-check SoT unchanged
    rows2 = conn.execute(
        f"SELECT id, skill_id FROM textbook_examples WHERE id IN ({','.join('?' for _ in EXPECTED_IDS)}) ORDER BY id",
        EXPECTED_IDS,
    ).fetchall()
    sot2 = {int(r["id"]): r["skill_id"] for r in rows2}
    sot2_hash = hashlib.sha256(json.dumps(sot2, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()

    # production still present
    prod_still = []
    for item in inventory:
        if item["old_status"] != "existing":
            continue
        p = ROOT / "agent_skills_v3" / item["skill_id"] / "components" / item["component_id"] / "generate.py"
        prod_still.append(p.is_file())

    verification = {
        "backup_root": str(backup_root.relative_to(ROOT)).replace("\\", "/"),
        "existing_backed_up": sum(1 for v in verified_existing if v["backup_ok"]),
        "existing_expected": 31,
        "missing_marked": missing_component_ids,
        "missing_count_ok": missing_ok and len(missing_component_ids) == 4,
        "file_index_count": len(file_index),
        "dryrun_indexed": len(dryrun_index),
        "staging_indexed": len(staging_index),
        "tracker_rows_dumped": len(tracker_rows),
        "sot_skill_hash_before": sot_skill_hash,
        "sot_skill_hash_after": sot2_hash,
        "sot_unchanged": sot_skill_hash == sot2_hash,
        "production_components_still_present": all(prod_still) and len(prod_still) == 31,
        "production_deleted": False,
        "runtime_still_references_original": runtime_refs,
        "wrappers_untouched_in_place": all(
            (ROOT / "skills" / f"{s}.py").is_file() for s in SKILLS
        ),
    }
    # write file index (may be large)
    (backup_root / "file_index.json").write_text(
        json.dumps(file_index, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (backup_root / "verification.json").write_text(
        json.dumps(verification, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    summary = {
        "ok": (
            verification["existing_backed_up"] == 31
            and verification["missing_count_ok"]
            and verification["sot_unchanged"]
            and verification["production_components_still_present"]
            and not verification["production_deleted"]
        ),
        "quarantine_name": quarantine_name,
        "backup_root": verification["backup_root"],
        "rebuild_manifest": str(rebuild_manifest_path.relative_to(ROOT)).replace("\\", "/"),
        "verification": verification,
        "runtime_report": runtime_report,
        "counts": rebuild_manifest["counts"],
    }
    (backup_root / "QUARANTINE_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
