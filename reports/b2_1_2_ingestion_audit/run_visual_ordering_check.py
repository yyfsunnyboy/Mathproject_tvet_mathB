from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from core.textbook_pdf_visual import enrich_textbook_examples_with_pdf_visuals, parse_notes_dict


OUT = Path(__file__).resolve().parent
PDF = OUT / "第一章 1-2 銳角三角函數-課本.pdf"
PROD = ROOT / "instance" / "kumon_math.db"
AUDIT = OUT / "audit_result.json"
TARGETS = {"例2": 1, "隨堂練習2": 1, "例3": 1, "例4": 1, "例6": 2}
TOKEN_RE = re.compile(r"\[MATH_PARSE_FAILED_\d+\]")


def main():
    production_before = hashlib.sha256(PROD.read_bytes()).hexdigest()
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    production_by_anchor = {
        row["anchor_id"]: row for row in audit["production_rows"]
    }
    rows = []
    for question in audit["questions"]:
        prod = production_by_anchor[question["anchor_id"]]
        rows.append(
            SimpleNamespace(
                id=prod["id"],
                skill_id=prod["skill_id"],
                source_description=question["source_description"],
                problem_text=question["problem_text"],
                detailed_solution=question["detailed_solution"],
                problem_type=question["source_type"],
                source_curriculum="vocational",
                source_volume="數學B2",
                source_chapter="第1章 三角函數",
                source_section="1-2 銳角三角函數",
                notes=json.dumps(
                    {
                        "question_anchor": {
                            "anchor_id": question["anchor_id"],
                            "source_order": question["source_order"],
                            "source_type": question["source_type"],
                        }
                    },
                    ensure_ascii=False,
                ),
            )
        )

    original_skills = {row.id: row.skill_id for row in rows}
    visual = enrich_textbook_examples_with_pdf_visuals(
        pdf_path=PDF,
        examples=rows,
        curriculum_info=audit["curriculum_info"],
        project_root=OUT / "visual_preview_root",
        debug_dir=OUT / "visual_debug",
        write_notes=True,
        dpi=160,
    )

    checks = []
    for label, expected_assets in TARGETS.items():
        row = next(r for r in rows if r.source_description.replace(" ", "") == label)
        notes = parse_notes_dict(row.notes)
        assets = notes.get("image_assets") or []
        valid_assets = [
            asset
            for asset in assets
            if (OUT / "visual_preview_root" / asset["path"]).is_file()
            and not asset.get("needs_crop_review")
        ]
        checks.append(
            {
                "id": row.id,
                "source_description": row.source_description,
                "expected_assets": expected_assets,
                "mounted_assets": len(valid_assets),
                "asset_paths": [asset["path"] for asset in valid_assets],
                "ok": len(valid_assets) == expected_assets,
            }
        )

    ordered = sorted(
        rows,
        key=lambda row: (
            int(parse_notes_dict(row.notes)["question_anchor"]["source_order"]),
            row.id,
        ),
    )
    row_11586 = next(row for row in rows if row.id == 11586)
    order_11586 = int(parse_notes_dict(row_11586.notes)["question_anchor"]["source_order"])
    position_11586 = ordered.index(row_11586) + 1

    exercise_rows = [
        row for row in rows
        if int(parse_notes_dict(row.notes)["question_anchor"]["source_order"]) >= 22
    ]
    skill_mapping_issues = sum(
        row.skill_id != original_skills[row.id] for row in exercise_rows
    )
    math_failures = sum(
        len(TOKEN_RE.findall((row.problem_text or "") + "\n" + (row.detailed_solution or "")))
        for row in rows
    )
    production_after = hashlib.sha256(PROD.read_bytes()).hexdigest()
    result = {
        "visual": {
            "checked": len(checks),
            "actual_issues": sum(not item["ok"] for item in checks),
            "fixed": sum(item["ok"] for item in checks),
            "remaining": [item["source_description"] for item in checks if not item["ok"]],
            "checks": checks,
            "pipeline_summary": visual,
        },
        "ordering": {
            "11586_source_order": order_11586,
            "preview_position": position_11586,
            "ordering_issue": order_11586 != 18 or position_11586 != 18,
        },
        "skill_mapping_issues": skill_mapping_issues,
        "exercise_skill_ids_preserved": len(exercise_rows),
        "final_dry_run": {
            "questions": len(rows),
            "math_parse_failed": math_failures,
            "segmentation_issues": len(audit.get("anchor_collisions") or []),
            "ordering_issues": int(order_11586 != 18 or position_11586 != 18),
            "visual_actual_issues": sum(not item["ok"] for item in checks),
        },
        "production_unchanged": production_before == production_after,
    }
    (OUT / "visual_ordering_final.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
