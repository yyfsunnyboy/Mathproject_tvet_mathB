from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from core.textbook_pdf_visual import (
    enrich_textbook_examples_with_pdf_visuals,
    merge_notes_preserve_image_assets,
    parse_notes_dict,
)


OUT = Path(__file__).resolve().parent
PROD = ROOT / "instance" / "kumon_math.db"
AUDIT = OUT / "audit_result.json"
PDF = OUT / "第一章 1-2 銳角三角函數-課本.pdf"
TOKEN_RE = re.compile(r"\[MATH_PARSE_FAILED_\d+\]")
TARGET_VISUALS = {"例2": 1, "隨堂練習2": 1, "例3": 1, "例4": 1, "例6": 2}
SECTION = ("數學B2", "1-2 銳角三角函數")


def _anchor(notes):
    data = parse_notes_dict(notes)
    anchor = data.get("question_anchor")
    return anchor if isinstance(anchor, dict) else {}


def _backup_database() -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = OUT / f"production_backup_pre_b2_1_2_reimport_{stamp}.db"
    source = sqlite3.connect(str(PROD), timeout=30)
    target = sqlite3.connect(str(path))
    try:
        source.backup(target)
    finally:
        target.close()
        source.close()
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not args.apply:
        raise SystemExit("Refusing production write without --apply")

    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    if audit.get("preview_math_parse_failed") != 0 or audit.get("phase2_blocks") != 31:
        raise RuntimeError("Dry-run gate is not clean")
    questions = audit["questions"]
    if len(questions) != 31 or len({q["anchor_id"] for q in questions}) != 31:
        raise RuntimeError("Preview anchors are not exactly 31 unique identities")

    backup = _backup_database()
    before_hash = hashlib.sha256(backup.read_bytes()).hexdigest()
    connection = sqlite3.connect(str(PROD), timeout=30)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("BEGIN IMMEDIATE")
        db_rows = [
            dict(row)
            for row in connection.execute(
                "SELECT id, skill_id, source_description, problem_text, detailed_solution, "
                "correct_answer, problem_type, source_curriculum, source_volume, source_chapter, "
                "source_section, notes FROM textbook_examples "
                "WHERE source_volume=? AND source_section=? ORDER BY id",
                SECTION,
            )
        ]
        if len(db_rows) != 31:
            raise RuntimeError(f"Expected 31 production rows, found {len(db_rows)}")
        by_anchor = {_anchor(row["notes"]).get("anchor_id"): row for row in db_rows}
        if None in by_anchor or len(by_anchor) != 31:
            raise RuntimeError("Production anchor identities are missing or duplicated")
        if set(by_anchor) != {q["anchor_id"] for q in questions}:
            raise RuntimeError("Preview and production anchor sets differ")

        original_identity = {
            anchor_id: (row["id"], row["skill_id"])
            for anchor_id, row in by_anchor.items()
        }
        objects = []
        for question in questions:
            row = by_anchor[question["anchor_id"]]
            incoming_notes = json.dumps(
                {"question_anchor": _anchor(row["notes"])}, ensure_ascii=False
            )
            objects.append(
                SimpleNamespace(
                    id=row["id"],
                    skill_id=row["skill_id"],
                    source_description=row["source_description"],
                    problem_text=question["problem_text"],
                    detailed_solution=question["detailed_solution"] or None,
                    correct_answer=row["correct_answer"],
                    problem_type=row["problem_type"],
                    source_curriculum=row["source_curriculum"],
                    source_volume=row["source_volume"],
                    source_chapter=row["source_chapter"],
                    source_section=row["source_section"],
                    notes=merge_notes_preserve_image_assets(row["notes"], incoming_notes),
                )
            )

        visual = enrich_textbook_examples_with_pdf_visuals(
            pdf_path=PDF,
            examples=objects,
            curriculum_info=audit["curriculum_info"],
            project_root=ROOT,
            debug_dir=OUT / "production_visual_debug",
            write_notes=True,
            dpi=200,
        )
        if visual.get("errors"):
            raise RuntimeError(f"Visual enrichment errors: {visual['errors']}")

        for obj in objects:
            anchor_id = _anchor(obj.notes).get("anchor_id")
            expected_id, expected_skill = original_identity[anchor_id]
            if obj.id != expected_id or obj.skill_id != expected_skill:
                raise RuntimeError(f"Identity or skill changed for {anchor_id}")
            cursor = connection.execute(
                "UPDATE textbook_examples SET problem_text=?, detailed_solution=?, notes=? "
                "WHERE id=? AND skill_id=?",
                (obj.problem_text, obj.detailed_solution, obj.notes, obj.id, obj.skill_id),
            )
            if cursor.rowcount != 1:
                raise RuntimeError(f"Scoped update failed for id={obj.id}")

        stored = [
            dict(row)
            for row in connection.execute(
                "SELECT id, skill_id, source_description, problem_text, detailed_solution, notes "
                "FROM textbook_examples WHERE source_volume=? AND source_section=?",
                SECTION,
            )
        ]
        anchors = [_anchor(row["notes"]) for row in stored]
        duplicate_examples = len(stored) - len({a.get("anchor_id") for a in anchors})
        math_failed = sum(
            len(TOKEN_RE.findall((row["problem_text"] or "") + "\n" + (row["detailed_solution"] or "")))
            for row in stored
        )
        ordered = sorted(stored, key=lambda row: (int(_anchor(row["notes"])["source_order"]), row["id"]))
        row_11586 = next(row for row in stored if row["id"] == 11586)
        source_order_11586 = int(_anchor(row_11586["notes"])["source_order"])
        display_position_11586 = next(i for i, row in enumerate(ordered, 1) if row["id"] == 11586)
        skill_issues = sum(
            original_identity[_anchor(row["notes"])["anchor_id"]][1] != row["skill_id"]
            for row in stored
        )
        visual_issues = 0
        visual_checks = []
        for label, expected in TARGET_VISUALS.items():
            row = next(r for r in stored if r["source_description"].replace(" ", "") == label)
            assets = parse_notes_dict(row["notes"]).get("image_assets") or []
            valid = [a for a in assets if (ROOT / a.get("path", "")).is_file()]
            ok = len(valid) == expected and all(not a.get("needs_crop_review") for a in valid)
            visual_issues += int(not ok)
            visual_checks.append({"id": row["id"], "label": label, "assets": len(valid), "ok": ok})

        gates = {
            "total_examples": len(stored),
            "math_parse_failed": math_failed,
            "duplicate_examples": duplicate_examples,
            "segmentation_issues": len(stored) - len({a.get("source_order") for a in anchors}),
            "ordering_issues": int(source_order_11586 != 18 or display_position_11586 != 18),
            "visual_issues": visual_issues,
            "skill_mapping_issues": skill_issues,
            "11586_source_order": source_order_11586,
            "11586_display_position": display_position_11586,
        }
        expected = {
            "total_examples": 31,
            "math_parse_failed": 0,
            "duplicate_examples": 0,
            "segmentation_issues": 0,
            "ordering_issues": 0,
            "visual_issues": 0,
            "skill_mapping_issues": 0,
            "11586_source_order": 18,
            "11586_display_position": 18,
        }
        if gates != expected:
            raise RuntimeError(f"Production gates failed: {gates}")
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    result = {
        **gates,
        "visual_checks": visual_checks,
        "visual_assets_mounted": visual.get("mounted"),
        "backup": str(backup),
        "backup_sha256": before_hash,
        "production_changed": True,
    }
    (OUT / "production_reimport_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
