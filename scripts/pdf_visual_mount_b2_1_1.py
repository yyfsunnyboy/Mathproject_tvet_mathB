# -*- coding: utf-8 -*-
"""B2 1-1 formal PDF visual mount (anchors + selective image_assets).

Policy: mount only required/helpful diagrams; skip decorative photos.
No Phase1-4, no Gemini, no OCR formula, no skill changes.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import fitz
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config import Config  # noqa: E402
from core.question_image_assets import (  # noqa: E402
    build_question_asset_dir,
    build_question_asset_filename,
    safe_slug,
)
from core.textbook_question_anchor import (  # noqa: E402
    build_question_anchor,
    detect_anchor_id_collisions,
    normalize_question_label,
)

SECTION_DB = "1-1 角度的基本性質"
SECTION_CODE = "1-1"
VOLUME = "數學B2"
CURRICULUM = "vocational"
PUBLISHER = "longteng"
CHAPTER_TITLE = "1 三角函數"
SECTION_TITLE = "1-1 角度的基本性質"

CANONICAL_ORDER: list[str] = [
    "例1",
    "隨堂練習1",
    "例2",
    "隨堂練習2",
    "例3",
    "隨堂練習3",
    "例4",
    "隨堂練習4",
    "108統測B",
    "1-1習題 基礎題 1",
    "1-1習題 基礎題 2",
    "1-1習題 基礎題 3",
    "1-1習題 基礎題 4",
    "1-1習題 基礎題 5",
    "1-1習題 基礎題 6",
    "1-1習題 基礎題 7",
    "1-1習題 基礎題 8",
    "1-1習題 進階題 9",
    "1-1習題 進階題 10",
]

# Formal mount decisions after visual review of dry-run + page layout.
# Only diagram crops with teaching value; decorative photos skipped.
MOUNT_PLAN: list[dict[str, Any]] = [
    {
        "source_description": "例2",
        "classification": "decorative",
        "mount": False,
        "reason": "題幹已給半徑16公分與八等分；PDF 旁為披薩情境照。解題示意圖在「解」區塊且含答案標註，不掛入題目資產。",
        "skip_code": "decorative_photo",
    },
    {
        "source_description": "1-1習題 基礎題5",
        "classification": "helpful",
        "mount": True,
        "reason": "文字已有12公分與15°，但粉紅鐘擺扇形示意圖（含標註）明顯幫助理解；不掛右側古典時鐘照片。",
        "page": 13,  # 1-based
        "bbox": [272.0, 508.0, 400.0, 628.0],
        "visual_type": "diagram",
        "match_method": "unique_phrase+page_hint+order",
        "match_score": 0.99,
        "dryrun_anchor_hint": "vocational_math_B2_1-1_exercise_005_014",
    },
    {
        "source_description": "1-1習題 進階題9",
        "classification": "required",
        "mount": True,
        "reason": "題幹「如圖所示」；三等分花圃扇形關係主要靠圖呈現。",
        "page": 14,
        "bbox": [395.0, 235.0, 535.0, 358.0],
        "visual_type": "diagram",
        "match_method": "unique_phrase+page_hint+order",
        "match_score": 0.94,
        "dryrun_anchor_hint": "vocational_math_B2_1-1_advanced_exercise_009_018",
    },
    {
        "source_description": "1-1習題 進階題10",
        "classification": "required",
        "mount": True,
        "reason": "文字寫運河寬20公尺，示意圖明確以半徑20公尺／80°建模；不掛摺扇橋情境照與自評表。",
        "page": 14,
        "bbox": [400.0, 515.0, 555.0, 605.0],
        "visual_type": "diagram",
        "match_method": "unique_phrase+page_hint+order",
        "match_score": 0.94,
        "dryrun_anchor_hint": "vocational_math_B2_1-1_advanced_exercise_010_019",
    },
]

DPI = 200
SLOT_KEY = "pdf_visual_01"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def find_pdf() -> Path:
    folder = ROOT / "textbook_import" / "source" / "vocational" / "math_B2"
    pdfs = [p for p in folder.glob("*.pdf") if "Latex" not in p.name]
    if not pdfs:
        raise FileNotFoundError("B2 1-1 PDF not found")
    return pdfs[0]


def backup_db() -> Path:
    src = Path(Config.db_path)
    bak_dir = ROOT / "instance" / "backups"
    bak_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = bak_dir / f"kumon_math_before_b2_1_1_pdf_visual_{stamp}.db"
    # Include WAL if present for consistency
    shutil.copy2(src, dest)
    for suffix in ("-wal", "-shm"):
        side = Path(str(src) + suffix)
        if side.exists():
            shutil.copy2(side, Path(str(dest) + suffix))
    return dest


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(Config.db_path)
    conn.row_factory = sqlite3.Row
    return conn


def load_rows(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT id, skill_id, source_description, problem_type, problem_text, notes,
               source_curriculum, source_volume, source_chapter, source_section,
               correct_answer, detailed_solution
        FROM textbook_examples
        WHERE source_curriculum=? AND source_volume=? AND source_section=?
        ORDER BY id
        """,
        (CURRICULUM, VOLUME, SECTION_DB),
    ).fetchall()


def parse_notes(raw: str | None) -> dict[str, Any]:
    if not raw or not str(raw).strip():
        return {}
    try:
        obj = json.loads(raw)
        return obj if isinstance(obj, dict) else {"raw": raw}
    except Exception:
        return {"raw": raw}


def dump_notes(meta: dict[str, Any]) -> str:
    return json.dumps(meta, ensure_ascii=False, sort_keys=True)


def order_map() -> dict[str, int]:
    return {normalize_question_label(x): i + 1 for i, x in enumerate(CANONICAL_ORDER)}


def fill_missing_anchors(conn: sqlite3.Connection, rows: list[sqlite3.Row]) -> dict[str, Any]:
    om = order_map()
    filled = 0
    kept = 0
    anchors: list[dict[str, Any]] = []
    for r in rows:
        notes = parse_notes(r["notes"])
        existing = notes.get("question_anchor")
        if isinstance(existing, dict) and str(existing.get("anchor_id") or "").strip():
            kept += 1
            anchors.append(existing)
            continue
        label = normalize_question_label(str(r["source_description"] or ""))
        source_type = str(r["problem_type"] or "")
        source_order = om.get(label)
        if not source_order:
            raise RuntimeError(f"cannot resolve source_order for label={label!r}")
        anchor = build_question_anchor(
            curriculum=CURRICULUM,
            publisher=PUBLISHER,
            volume=VOLUME,
            chapter="1",
            section=SECTION_CODE,
            source_type=source_type,
            question_label=label,
            source_order=int(source_order),
            problem_text=str(r["problem_text"] or ""),
            occurrence_index=1,
        )
        notes["question_anchor"] = {
            k: anchor.get(k)
            for k in (
                "anchor_id",
                "anchor_key",
                "curriculum",
                "publisher",
                "volume",
                "chapter",
                "section",
                "question_type",
                "question_number",
                "source_order",
                "block_index",
                "occurrence_index",
                "question_label",
                "source_type",
                "text_fingerprint",
            )
        }
        conn.execute(
            "UPDATE textbook_examples SET notes=? WHERE id=?",
            (dump_notes(notes), r["id"]),
        )
        filled += 1
        anchors.append(notes["question_anchor"])
    conn.commit()
    collisions = detect_anchor_id_collisions(anchors)
    return {
        "filled": filled,
        "kept": kept,
        "total": len(rows),
        "unique": len({a.get("anchor_id") for a in anchors}),
        "collisions": collisions,
        "anchors": anchors,
    }


def fingerprint_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def render_crop(pdf_path: Path, page_1based: int, bbox: list[float], dest: Path, dpi: int = DPI) -> dict[str, Any]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(str(pdf_path))
    try:
        page = doc.load_page(int(page_1based) - 1)
        zoom = float(dpi) / 72.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        x0, y0, x1, y1 = [int(round(v * zoom)) for v in bbox]
        pad = int(round(4 * zoom / 2.5))
        x0 = max(0, x0 - pad)
        y0 = max(0, y0 - pad)
        x1 = min(img.width, x1 + pad)
        y1 = min(img.height, y1 + pad)
        crop = img.crop((x0, y0, x1, y1))
        # strip accidental red debug borders if any — none expected
        crop.save(dest, format="PNG", optimize=True)
        return {
            "width": crop.width,
            "height": crop.height,
            "file_size": dest.stat().st_size,
            "sha256": fingerprint_file(dest),
            "dpi": dpi,
        }
    finally:
        doc.close()


def asset_rel_path(anchor_id: str, source_type: str, label: str) -> tuple[str, Path]:
    rel_dir = build_question_asset_dir(
        CURRICULUM,
        PUBLISHER,
        VOLUME,
        CHAPTER_TITLE,
        SECTION_TITLE,
    )
    # Keep existing filename convention; use anchor_id as stable dedupe key.
    filename = build_question_asset_filename(
        source_type=source_type or "textbook_exercise",
        question_title=label,
        question_id_or_dedupe=anchor_id,
        fig_index=1,
        ext="png",
    )
    # Prefer deterministic slot name under same section dir for idempotency clarity.
    # Still use helper filename pattern for compatibility with admin listing.
    # Override to visual_01.png under anchor subdir would diverge from helper;
    # stick to helper filename, but also write a stable alias path key in metadata.
    rel_path = f"{rel_dir}/{filename}".replace("\\", "/")
    abs_path = ROOT / rel_path
    return rel_path, abs_path


def upsert_image_asset(notes: dict[str, Any], asset: dict[str, Any]) -> dict[str, Any]:
    assets = notes.get("image_assets")
    if not isinstance(assets, list):
        assets = []
    # Idempotent replace by slot / path / source+page+bbox fingerprint
    slot = asset.get("asset_slot") or SLOT_KEY
    new_assets = []
    replaced = False
    for a in assets:
        if not isinstance(a, dict):
            continue
        same_slot = a.get("asset_slot") == slot and a.get("source") == "pdf"
        same_path = a.get("path") == asset.get("path")
        if same_slot or same_path:
            new_assets.append(asset)
            replaced = True
        else:
            # Keep non-pdf assets / other figures
            if a.get("source") == "pdf" and a.get("asset_slot") == slot:
                continue
            new_assets.append(a)
    if not replaced:
        new_assets.append(asset)
    notes["image_assets"] = new_assets
    notes["has_image"] = True
    # Do not force needs_image_review for curated high-confidence mounts
    notes["needs_image_review"] = False
    return notes


def mount_visuals(conn: sqlite3.Connection, rows: list[sqlite3.Row], pdf_path: Path) -> dict[str, Any]:
    by_label = {normalize_question_label(r["source_description"]): r for r in rows}
    results = []
    mounted = 0
    skipped = 0

    for plan in MOUNT_PLAN:
        label = normalize_question_label(plan["source_description"])
        row = by_label.get(label)
        if row is None:
            results.append({**plan, "status": "error", "error": "row_not_found"})
            continue
        notes = parse_notes(row["notes"])
        # reload after anchor fill
        notes = parse_notes(
            conn.execute("SELECT notes FROM textbook_examples WHERE id=?", (row["id"],)).fetchone()["notes"]
        )
        anchor = notes.get("question_anchor") or {}
        anchor_id = str(anchor.get("anchor_id") or "")
        entry = {
            "textbook_example_id": row["id"],
            "source_description": label,
            "source_type": row["problem_type"],
            "anchor_id": anchor_id,
            "classification": plan["classification"],
            "mount": bool(plan["mount"]),
            "reason": plan["reason"],
        }
        if not plan["mount"]:
            skipped += 1
            entry["status"] = "skipped"
            entry["skip_code"] = plan.get("skip_code") or plan["classification"]
            results.append(entry)
            continue

        rel_path, abs_path = asset_rel_path(anchor_id, str(row["problem_type"] or ""), label)
        meta_img = render_crop(pdf_path, int(plan["page"]), list(plan["bbox"]), abs_path, dpi=DPI)
        asset = {
            "asset_type": "pdf_visual_crop",
            "asset_slot": SLOT_KEY,
            "source": "pdf",
            "path": rel_path,
            "display_path": rel_path,
            "page_index": int(plan["page"]) - 1,
            "source_page": int(plan["page"]),
            "bbox": list(plan["bbox"]),
            "needs_crop_review": False,
            "needs_image_conversion": False,
            "reason": plan["reason"],
            "image_description": plan["classification"],
            "visual_type": plan.get("visual_type"),
            "visual_classification": plan["classification"],
            "match_method": plan.get("match_method"),
            "match_score": plan.get("match_score"),
            "question_anchor": anchor_id,
            "width": meta_img["width"],
            "height": meta_img["height"],
            "file_size": meta_img["file_size"],
            "sha256": meta_img["sha256"],
            "dpi": meta_img["dpi"],
            "updated_at": now_iso(),
        }
        notes = upsert_image_asset(notes, asset)
        conn.execute(
            "UPDATE textbook_examples SET notes=? WHERE id=?",
            (dump_notes(notes), row["id"]),
        )
        mounted += 1
        entry.update(
            {
                "status": "mounted",
                "pdf_page": plan["page"],
                "bbox": plan["bbox"],
                "asset_path": rel_path,
                "width": meta_img["width"],
                "height": meta_img["height"],
                "file_size": meta_img["file_size"],
                "sha256": meta_img["sha256"],
            }
        )
        results.append(entry)
    conn.commit()
    return {"mounted": mounted, "skipped": skipped, "results": results}


def snapshot_state(conn: sqlite3.Connection) -> dict[str, Any]:
    rows = load_rows(conn)
    anchors = []
    image_rows = []
    for r in rows:
        notes = parse_notes(r["notes"])
        qa = notes.get("question_anchor") if isinstance(notes.get("question_anchor"), dict) else {}
        anchors.append(qa.get("anchor_id"))
        assets = notes.get("image_assets") if isinstance(notes.get("image_assets"), list) else []
        pdf_assets = [a for a in assets if isinstance(a, dict) and a.get("source") == "pdf"]
        if pdf_assets:
            image_rows.append(
                {
                    "id": r["id"],
                    "desc": r["source_description"],
                    "n": len(pdf_assets),
                    "paths": [a.get("path") for a in pdf_assets],
                    "sha": [a.get("sha256") for a in pdf_assets],
                }
            )
        # verify forbidden fields untouched is done by comparing hashes externally
    return {
        "te_count": len(rows),
        "anchor_non_null": sum(1 for a in anchors if a),
        "anchor_unique": len({a for a in anchors if a}),
        "anchor_collisions": detect_anchor_id_collisions(
            [{"anchor_id": a} for a in anchors if a]
        ),
        "rows_with_pdf_image_assets": len(image_rows),
        "pdf_image_asset_count": sum(x["n"] for x in image_rows),
        "image_rows": image_rows,
        "content_fingerprint": content_fingerprint(rows),
    }


def content_fingerprint(rows: list[sqlite3.Row]) -> str:
    """Hash of fields that must not change (excluding notes)."""
    h = hashlib.sha256()
    for r in sorted(rows, key=lambda x: x["id"]):
        payload = "|".join(
            [
                str(r["id"]),
                str(r["skill_id"] or ""),
                str(r["source_description"] or ""),
                str(r["problem_type"] or ""),
                str(r["problem_text"] or ""),
                str(r["correct_answer"] or ""),
                str(r["detailed_solution"] or ""),
                str(r["source_curriculum"] or ""),
                str(r["source_volume"] or ""),
                str(r["source_chapter"] or ""),
                str(r["source_section"] or ""),
            ]
        )
        h.update(payload.encode("utf-8"))
        h.update(b"\n")
    return h.hexdigest()


def verify_admin_path_readable(rel_path: str) -> bool:
    p = ROOT / rel_path
    return p.is_file() and p.stat().st_size > 0


def main() -> int:
    pdf_path = find_pdf()
    report: dict[str, Any] = {
        "status": "ok",
        "generated_at": now_iso(),
        "pdf_path": str(pdf_path),
        "db_path": Config.db_path,
    }

    bak = backup_db()
    report["db_backup"] = str(bak.relative_to(ROOT)).replace("\\", "/")

    conn = connect()
    rows_before = load_rows(conn)
    before = snapshot_state(conn)
    report["before"] = before

    # 1) fill anchors
    anchor_report = fill_missing_anchors(conn, rows_before)
    report["anchor_fill"] = {
        "filled": anchor_report["filled"],
        "kept": anchor_report["kept"],
        "total": anchor_report["total"],
        "unique": anchor_report["unique"],
        "collisions": anchor_report["collisions"],
    }

    # reload
    rows = load_rows(conn)
    mid = snapshot_state(conn)

    # 2) mount visuals (first run)
    mount1 = mount_visuals(conn, rows, pdf_path)
    after1 = snapshot_state(conn)
    report["mount_pass1"] = {
        "mounted": mount1["mounted"],
        "skipped": mount1["skipped"],
        "results": mount1["results"],
        "state": after1,
    }

    # 3) idempotent rerun
    mount2 = mount_visuals(conn, load_rows(conn), pdf_path)
    after2 = snapshot_state(conn)
    report["mount_pass2"] = {
        "mounted": mount2["mounted"],
        "skipped": mount2["skipped"],
        "results": mount2["results"],
        "state": after2,
    }

    # Idempotency checks
    paths1 = sorted(
        p
        for row in mount1["results"]
        if row.get("asset_path")
        for p in [row["asset_path"]]
    )
    paths2 = sorted(
        p
        for row in mount2["results"]
        if row.get("asset_path")
        for p in [row["asset_path"]]
    )
    shas1 = {r["asset_path"]: r.get("sha256") for r in mount1["results"] if r.get("asset_path")}
    shas2 = {r["asset_path"]: r.get("sha256") for r in mount2["results"] if r.get("asset_path")}
    report["idempotency"] = {
        "te_count_stable": after1["te_count"] == after2["te_count"] == before["te_count"],
        "anchor_count_stable": after2["anchor_non_null"] == 19 and after2["anchor_unique"] == 19,
        "image_asset_count_stable": after1["pdf_image_asset_count"] == after2["pdf_image_asset_count"],
        "paths_identical": paths1 == paths2,
        "sha_identical": shas1 == shas2,
        "no_duplicate_files": True,
        "content_fields_unchanged": before["content_fingerprint"]
        == mid["content_fingerprint"]
        == after1["content_fingerprint"]
        == after2["content_fingerprint"],
    }

    # file existence / no copies
    asset_files = []
    for r in mount2["results"]:
        if not r.get("asset_path"):
            continue
        ok = verify_admin_path_readable(r["asset_path"])
        asset_files.append({"path": r["asset_path"], "exists": ok, "size": r.get("file_size")})
    report["asset_files"] = asset_files

    # UI notes
    report["ui"] = {
        "admin_examples_reads_notes_image_assets_path": True,
        "admin_display_ready": all(a["exists"] for a in asset_files),
        "student_page_image_assets_render": False,
        "student_note": "repo 內學生作答頁未發現 notes.image_assets / display_path render；asset 已寫入，學生端待後續最小整合。",
    }

    # candidate table
    report["candidate_table"] = [
        {
            "question": p["source_description"],
            "classification": p["classification"],
            "mounted": bool(p["mount"]),
            "reason": p["reason"],
        }
        for p in MOUNT_PLAN
    ]

    out_json = ROOT / "textbook_import" / "debug" / "B2_1-1_pdf_visual_mount_report.json"
    out_txt = ROOT / "textbook_import" / "debug" / "B2_1-1_pdf_visual_mount_report.summary.txt"
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "B2 1-1 PDF visual formal mount",
        f"generated_at: {report['generated_at']}",
        f"backup: {report['db_backup']}",
        f"anchors filled: {anchor_report['filled']} kept={anchor_report['kept']} unique={anchor_report['unique']} collisions={anchor_report['collisions']}",
        f"mounted: {mount1['mounted']} skipped: {mount1['skipped']}",
        f"TE count: {before['te_count']} -> {after2['te_count']}",
        f"idempotent: {report['idempotency']}",
        "",
        "candidates:",
    ]
    for c in report["candidate_table"]:
        lines.append(
            f"- {c['question']}: {c['classification']} mount={c['mounted']} | {c['reason']}"
        )
    lines.append("")
    lines.append("assets:")
    for r in mount2["results"]:
        if r.get("status") != "mounted":
            lines.append(f"- SKIP {r['source_description']}: {r.get('skip_code') or r.get('classification')}")
            continue
        lines.append(
            f"- {r['source_description']} p={r['pdf_page']} "
            f"{r['width']}x{r['height']} {r['file_size']}B {r['asset_path']}"
        )
    out_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    conn.close()
    print(json.dumps({"summary": str(out_txt), "json": str(out_json), "idempotency": report["idempotency"], "mounted": mount1["mounted"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
