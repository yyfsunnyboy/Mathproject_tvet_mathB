from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import sys
from pathlib import Path

from flask import Flask


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from config import Config
from models import db
import core.textbook_importer_v3_pipeline as pipeline
import core.textbook_processor_v2 as tp
from core.textbook_mathtype_converter import convert_docx_mathtype_to_latex_docx
from core.textbook_question_anchor import build_anchors_from_block_meta, detect_anchor_id_collisions


OUT = ROOT / "reports" / "b2_1_2_ingestion_audit"
SOURCE = OUT / "第一章 1-2 銳角三角函數-課本.docx"
LATEX = OUT / "第一章 1-2 銳角三角函數-課本_Latex.docx"
PROD = ROOT / "instance" / "kumon_math.db"
TOKEN_RE = re.compile(r"\[MATH_PARSE_FAILED_(\d+)\]")


def main() -> None:
    before = hashlib.sha256(PROD.read_bytes()).hexdigest()
    conversion = convert_docx_mathtype_to_latex_docx(SOURCE, LATEX)

    app = Flask("b2_1_2_ingestion_audit", root_path=str(ROOT))
    app.config.from_object(Config)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    db.init_app(app)

    with app.app_context():
        raw = db.engine.raw_connection()
        with sqlite3.connect(PROD.as_uri() + "?mode=ro", uri=True) as ro:
            ro.backup(raw.driver_connection)
        raw.close()

        info = pipeline.build_curriculum_info_for_v3_import(
            latex_docx_path=LATEX,
            original_docx_filename=SOURCE.name,
            curriculum="vocational",
            publisher="longteng",
            grade=10,
            volume="數學B2",
            apply_policy=False,
        )
        lines = tp.phase1_extract_docx_lines(str(LATEX), curriculum_info=info)
        scope = tp._resolve_import_source_metadata(
            parse_filename=str(info.get("parse_filename") or SOURCE.name),
            lines=lines,
            curriculum_info=info,
        )
        info = pipeline._fill_chapter_section_from_outline_or_lines(scope["curriculum_info"], lines)
        blocks = tp.phase2_deterministic_block_slice(
            lines,
            source_scope=scope["source_scope"],
            curriculum_info=info,
        )
        meta = dict(tp._DOCX_BLOCK_META or {})
        anchors = build_anchors_from_block_meta(meta, info)

        questions = []
        for anchor, (key, item) in zip(anchors, meta.items()):
            problem = tp._sanitize_db_latex_delimiters(
                tp.clean_problem_leading_title(str(item.get("problem_text") or ""))
            )
            solution = tp._sanitize_db_latex_delimiters(str(item.get("detailed_solution") or ""))
            resolved = tp._phase4_resolve_mathb_formal_binding(
                block_meta=item,
                source_type=str(item.get("source_type") or anchor.get("source_type") or ""),
                db_problem_text=problem,
                curriculum_info=info,
                item_sec_code=str(item.get("section_code") or info.get("section_code") or ""),
                coords=tp._import_scope_coords(info),
                source_description=key,
            )
            questions.append(
                {
                    "anchor_id": anchor["anchor_id"],
                    "source_order": anchor["source_order"],
                    "source_description": key,
                    "source_type": str(item.get("source_type") or anchor.get("source_type") or ""),
                    "problem_text": problem,
                    "detailed_solution": solution,
                    "math_parse_failed_tokens": [int(x) for x in TOKEN_RE.findall(problem + "\n" + solution)],
                    "formal_skill_id": str(item.get("formal_skill_id") or "") or None,
                    "resolved_skill_id": resolved[1] if resolved else None,
                    "meta": item,
                }
            )

        prod_rows = []
        con = sqlite3.connect(PROD.as_uri() + "?mode=ro", uri=True)
        con.row_factory = sqlite3.Row
        for row in con.execute(
            "SELECT id, skill_id, source_description, problem_text, detailed_solution, notes "
            "FROM textbook_examples WHERE source_volume=? AND source_section=? ORDER BY id",
            ("數學B2", "1-2 銳角三角函數"),
        ):
            record = dict(row)
            try:
                record["anchor_id"] = json.loads(record.get("notes") or "{}").get("question_anchor", {}).get("anchor_id")
            except Exception:
                record["anchor_id"] = None
            record["math_parse_failed_tokens"] = [
                int(x)
                for x in TOKEN_RE.findall(
                    str(record.get("problem_text") or "") + "\n" + str(record.get("detailed_solution") or "")
                )
            ]
            prod_rows.append(record)
        con.close()

        preview_by_anchor = {q["anchor_id"]: q for q in questions}
        skill_comparison = []
        for row in prod_rows:
            preview = preview_by_anchor.get(row.get("anchor_id"))
            skill_comparison.append(
                {
                    "id": row["id"],
                    "anchor_id": row.get("anchor_id"),
                    "production_skill_id": row["skill_id"],
                    "preview_skill_id": preview.get("resolved_skill_id") if preview else None,
                    "match": bool(preview and preview.get("resolved_skill_id") == row["skill_id"]),
                }
            )
        db.session.rollback()

    after = hashlib.sha256(PROD.read_bytes()).hexdigest()
    result = {
        "production_sha256_before": before,
        "production_sha256_after": after,
        "production_unchanged": before == after,
        "conversion": {
            key: conversion.get(key)
            for key in (
                "original_unchanged",
                "mathtype_ole",
                "equation_native_ok",
                "converted_ok",
                "converted_failed",
                "non_mtef_objects",
                "eq_fields",
                "eq_converted_ok",
                "summary",
            )
        },
        "conversion_failures": [
            {k: f.get(k) for k in ("formula_index", "status", "error", "location")}
            for f in conversion.get("formulas", [])
            if f.get("status") == "failed"
        ],
        "curriculum_info": info,
        "phase1_lines": len(lines),
        "phase2_blocks": len(blocks or {}),
        "anchor_count": len(anchors),
        "anchor_collisions": detect_anchor_id_collisions(anchors),
        "preview_math_parse_failed": sum(len(q["math_parse_failed_tokens"]) for q in questions),
        "preview_rows_with_math_parse_failed": sum(bool(q["math_parse_failed_tokens"]) for q in questions),
        "questions": questions,
        "production_rows": prod_rows,
        "skill_comparison": skill_comparison,
    }
    (OUT / "audit_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "production_unchanged": result["production_unchanged"],
                "conversion": result["conversion"],
                "phase1_lines": result["phase1_lines"],
                "phase2_blocks": result["phase2_blocks"],
                "anchor_count": result["anchor_count"],
                "anchor_collisions": len(result["anchor_collisions"]),
                "preview_math_parse_failed": result["preview_math_parse_failed"],
                "preview_rows_with_math_parse_failed": result["preview_rows_with_math_parse_failed"],
                "skill_matches": sum(x["match"] for x in skill_comparison),
                "skill_total": len(skill_comparison),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
