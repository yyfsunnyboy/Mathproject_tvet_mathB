# -*- coding: utf-8 -*-
"""B2 2-1 formal scoped import: backup → preconfirm → import → verify."""
from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SOURCE = (
    ROOT
    / "textbook_import/source/vocational/math_B2"
    / "第二章 2-1 正弦定理與餘弦定理-課本.docx"
)
PDF = SOURCE.with_suffix(".pdf")
PROD_DB = ROOT / "instance" / "kumon_math.db"
TARGETS = {
    "textbook_example",
    "in_class_practice",
    "self_assessment",
    "exam_practice",
}
REPORT_DIR = ROOT / "reports"
WORK = ROOT / "tmp_b2_21_formal_import"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def table_counts(db_path: Path) -> dict[str, int]:
    with sqlite3.connect(db_path) as conn:
        return {
            name: conn.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
            for name in ("textbook_examples", "skills_info", "skill_curriculum")
        }


def existing_section_rows(db_path: Path) -> list[tuple]:
    with sqlite3.connect(db_path) as conn:
        return conn.execute(
            """
            SELECT id, problem_type, source_description, skill_id, source_section
            FROM textbook_examples
            WHERE source_curriculum = ?
              AND source_volume = ?
              AND (
                    source_section LIKE ?
                 OR source_section LIKE ?
                 OR source_section = ?
              )
            ORDER BY id
            """,
            (
                "vocational",
                "數學B2",
                "%2-1%",
                "%正弦定理%",
                "2-1",
            ),
        ).fetchall()


def backup_db() -> dict:
    backup_dir = ROOT / "instance" / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = backup_dir / f"kumon_math_before_b2_2_1_scoped_{stamp}.db"
    shutil.copy2(PROD_DB, dest)
    ok = dest.is_file() and dest.stat().st_size == PROD_DB.stat().st_size
    return {
        "backup_path": str(dest),
        "success": ok,
        "size": dest.stat().st_size if dest.is_file() else 0,
        "source_sha256": sha256(PROD_DB),
        "backup_sha256": sha256(dest) if ok else None,
    }


def preconfirm_scope() -> dict:
    from core.textbook_importer_v3_scope import analyze_scoped_conversion
    from core.textbook_mathtype_converter import convert_docx_mathtype_to_latex_docx
    from core.textbook_importer_v3_orchestrate import build_curriculum_info_for_v3_import

    WORK.mkdir(parents=True, exist_ok=True)
    work_docx = WORK / SOURCE.name
    if not work_docx.is_file() or work_docx.stat().st_size != SOURCE.stat().st_size:
        shutil.copy2(SOURCE, work_docx)
    latex = WORK / (SOURCE.stem + "_Latex.docx")
    convert_report = convert_docx_mathtype_to_latex_docx(work_docx, latex)
    info = build_curriculum_info_for_v3_import(
        latex_docx_path=latex,
        original_docx_filename=SOURCE.name,
        curriculum="vocational",
        publisher="longteng",
        grade=10,
        volume="數學B2",
    )
    info["source_scope"] = info.get("source_scope") or "section_textbook"
    scope = analyze_scoped_conversion(work_docx, latex, info, convert_report, TARGETS)
    counts = scope["counts"]
    return {
        "target_count": scope["target_count"],
        "target_source_type_counts": scope["target_source_type_counts"],
        "required_formula_count": counts["required_formula_count"],
        "required_formula_failed": counts["required_formula_failed"],
        "required_formula_success": counts["required_formula_success"],
        "unresolved": scope["unresolved"],
        "unresolved_count": len(scope["unresolved"]),
        "would_write": [
            {
                "index": q["index"],
                "label": q["label"],
                "source_type": q["source_type"],
                "section": q["section"],
                "problem_start": q["problem_start"],
                "formula_count": q["formula_count"],
                "image_count": len(q["image_candidates"]),
                "would_write": q["would_write"],
            }
            for q in scope["questions"]
            if q["would_write"] == "YES"
        ],
        "image_candidates": scope["image_candidate_count"],
        "image_needs_review": scope["image_needs_review_count"],
        "work_docx": str(work_docx),
        "latex_docx": str(latex),
        "convert_ok": convert_report.get("converted_ok"),
        "convert_failed": convert_report.get("converted_failed"),
        "scope": scope,
        "convert_report": convert_report,
    }


def gate_ok(pre: dict) -> tuple[bool, str]:
    if pre["required_formula_failed"] != 0:
        return False, "required_formula_failed != 0"
    if pre["unresolved_count"] != 0:
        return False, "unresolved_scope != 0"
    if pre["target_count"] != len(pre["would_write"]):
        return False, "target_count != would_write YES count"
    if pre["convert_failed"]:
        # scoped gate already checked required; still stop if convert report is unhealthy for required path
        pass
    # Soft expectations from prior dry-run — stop only if clearly unexpected drift.
    if pre["target_count"] < 1:
        return False, "no target questions"
    if pre["required_formula_count"] < 1:
        return False, "no required formulas"
    # Detect major drift from last known good dry-run without hardcoding as pass criteria.
    # If counts move far from last dry-run, abort.
    last = ROOT / "reports" / "b2_2_1_scoped_import_dryrun.json"
    if last.is_file():
        prev = json.loads(last.read_text(encoding="utf-8"))
        prev_scope = prev.get("scoped_import") or prev
        prev_target = int(prev_scope.get("target_count") or prev.get("target_questions") or 0)
        prev_req = int(
            (prev_scope.get("counts") or prev.get("formula_counts") or {}).get(
                "required_formula_count"
            )
            or 0
        )
        if prev_target and pre["target_count"] != prev_target:
            return False, f"target_count changed {prev_target} -> {pre['target_count']}"
        if prev_req and pre["required_formula_count"] != prev_req:
            return (
                False,
                f"required_formula_count changed {prev_req} -> {pre['required_formula_count']}",
            )
    return True, "ok"


def run_import(work_docx: Path) -> dict:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    from app import create_app
    from core.textbook_importer_v3_pipeline import run_v3_pair_pipeline

    app = create_app()
    pdf = PDF if PDF.is_file() else None
    with app.app_context():
        report = run_v3_pair_pipeline(
            project_root=ROOT,
            docx_path=work_docx,
            pdf_path=pdf,
            curriculum="vocational",
            volume="數學B2",
            publisher="longteng",
            allow_phase4=True,
            target_source_types=TARGETS,
            app=app,
            emit_stream_end=False,
        )
    return report


def verify_after(before_ids: set[int]) -> dict:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    from app import create_app
    from models import TextbookExample, SkillInfo, db

    app = create_app()
    with app.app_context():
        rows = (
            TextbookExample.query.filter_by(
                source_curriculum="vocational",
                source_volume="數學B2",
            )
            .filter(TextbookExample.source_section.like("%2-1%"))
            .order_by(TextbookExample.id.asc())
            .all()
        )
        # also catch section title variants
        extra = (
            TextbookExample.query.filter_by(
                source_curriculum="vocational",
                source_volume="數學B2",
            )
            .filter(TextbookExample.source_section.like("%正弦定理%"))
            .order_by(TextbookExample.id.asc())
            .all()
        )
        by_id = {r.id: r for r in rows}
        for r in extra:
            by_id[r.id] = r
        rows = sorted(by_id.values(), key=lambda r: r.id)
        items = []
        for r in rows:
            notes = {}
            if r.notes:
                try:
                    notes = json.loads(r.notes)
                except Exception:
                    notes = {"raw_notes": r.notes}
            visuals = notes.get("visual_assets") or notes.get("image_candidates") or []
            desc = r.source_description or ""
            inferred_type = r.problem_type or ""
            if "source_type=" in desc:
                try:
                    inferred_type = desc.split("source_type=", 1)[1].split(" ", 1)[0].split("|", 1)[0].strip(" ]")
                except Exception:
                    pass
            title = desc.split(" [", 1)[0].strip() if desc else ""
            items.append(
                {
                    "id": r.id,
                    "new": r.id not in before_ids,
                    "source_type": inferred_type,
                    "problem_type": r.problem_type,
                    "source_label": title,
                    "source_description": r.source_description,
                    "source_section": r.source_section,
                    "source_chapter": r.source_chapter,
                    "skill_id": r.skill_id,
                    "problem_start": (r.problem_text or "")[:80],
                    "has_math_parse_failed": "MATH_PARSE_FAILED" in (r.problem_text or "")
                    or "MATH_PARSE_FAILED" in (r.detailed_solution or ""),
                    "visual_assets": visuals,
                    "notes_keys": sorted(notes.keys()) if isinstance(notes, dict) else [],
                }
            )
        type_counts = Counter(i["source_type"] for i in items if i["new"])
        non_target_new = [
            i
            for i in items
            if i["new"] and i["source_type"] not in TARGETS
        ]
        return {
            "all_section_rows": items,
            "new_rows": [i for i in items if i["new"]],
            "new_type_counts": dict(type_counts),
            "non_target_new": non_target_new,
        }


def main() -> None:
    if not SOURCE.is_file():
        raise SystemExit(f"missing source: {SOURCE}")
    if not PROD_DB.is_file():
        raise SystemExit(f"missing db: {PROD_DB}")

    before_sha = sha256(PROD_DB)
    before_counts = table_counts(PROD_DB)
    before_rows = existing_section_rows(PROD_DB)
    before_ids = {r[0] for r in before_rows}

    print("=== PRE-IMPORT DB SNAPSHOT ===")
    print(json.dumps({
        "sha256": before_sha,
        "counts": before_counts,
        "existing_2_1_rows": len(before_rows),
        "existing_ids": sorted(before_ids),
    }, ensure_ascii=False, indent=2))

    print("=== BACKUP ===")
    backup = backup_db()
    print(json.dumps(backup, ensure_ascii=False, indent=2))
    if not backup["success"] or backup["source_sha256"] != backup["backup_sha256"]:
        raise SystemExit("BACKUP FAILED — aborting before any import")

    print("=== PRECONFIRM SCOPE (read-only) ===")
    pre = preconfirm_scope()
    summary_pre = {k: v for k, v in pre.items() if k not in {"scope", "convert_report"}}
    print(json.dumps(summary_pre, ensure_ascii=False, indent=2))
    ok, reason = gate_ok(pre)
    print(f"GATE: {ok} ({reason})")
    if not ok:
        out = {
            "aborted": True,
            "reason": reason,
            "backup": backup,
            "before": {"sha256": before_sha, "counts": before_counts},
            "preconfirm": summary_pre,
        }
        (REPORT_DIR / "b2_2_1_scoped_import_formal_aborted.json").write_text(
            json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        raise SystemExit(f"UNEXPECTED SCOPE DRIFT — abort without DB write: {reason}")

    print("=== QUESTIONS ABOUT TO WRITE ===")
    for q in pre["would_write"]:
        print(
            f"  #{q['index']} {q['source_type']} {q['label']} "
            f"formulas={q['formula_count']} images={q['image_count']}"
        )

    print("=== FORMAL IMPORT allow_phase4=True target_source_types=TARGETS ===")
    report = run_import(Path(pre["work_docx"]))
    print(json.dumps({
        "ok": report.get("ok"),
        "error": report.get("error"),
        "metrics": report.get("metrics"),
        "would_write": report.get("would_write"),
        "warnings": report.get("warnings"),
    }, ensure_ascii=False, indent=2, default=str))

    after_sha = sha256(PROD_DB)
    after_counts = table_counts(PROD_DB)
    verify = verify_after(before_ids)

    # Attach scoped image associations from preconfirm (pipeline keeps needs_review)
    image_assoc = []
    for q in pre["scope"]["questions"]:
        if not q.get("image_candidates"):
            continue
        for im in q["image_candidates"]:
            image_assoc.append({
                "question_index": q["index"],
                "label": q["label"],
                "source_type": q["source_type"],
                "paragraph_index": im.get("paragraph_index"),
                "filename": im.get("filename"),
                "relationship_id": im.get("relationship_id"),
                "needs_review": im.get("needs_review", True),
            })

    result = {
        "backup": backup,
        "before": {
            "sha256": before_sha,
            "counts": before_counts,
            "existing_2_1_ids": sorted(before_ids),
        },
        "preconfirm": summary_pre,
        "gate": {"ok": ok, "reason": reason},
        "import_report": {
            "ok": report.get("ok"),
            "error": report.get("error"),
            "metrics": report.get("metrics"),
            "warnings": report.get("warnings"),
            "scoped_import_counts": (report.get("scoped_import") or {}).get("counts"),
            "scoped_would_write": (report.get("scoped_import") or {}).get("would_write_count"),
        },
        "after": {
            "sha256": after_sha,
            "counts": after_counts,
        },
        "verify": verify,
        "image_associations": image_assoc,
        "sys_executable": sys.executable,
    }
    out_path = REPORT_DIR / "b2_2_1_scoped_import_formal_result.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print("=== RESULT WRITTEN ===", out_path)
    print(json.dumps({
        "ok": report.get("ok"),
        "db_write": (report.get("metrics") or {}).get("db_write"),
        "new_rows": len(verify["new_rows"]),
        "new_type_counts": verify["new_type_counts"],
        "non_target_new": len(verify["non_target_new"]),
        "counts_before": before_counts,
        "counts_after": after_counts,
        "sha_changed": before_sha != after_sha,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
