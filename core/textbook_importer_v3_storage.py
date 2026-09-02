# -*- coding: utf-8 -*-
"""V3 教材匯入：來源檔案儲存（textbook_import/source/）。"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from werkzeug.datastructures import FileStorage

from core.textbook_importer_v3_source import (
    ALLOWED_DOCX_EXT,
    ALLOWED_PDF_EXT,
    build_file_map,
    validate_textbook_source_batch,
)

SOURCE_ROOT = Path("textbook_import") / "source"

CURRICULUM_DIRECTORY_MAP: dict[str, str] = {
    "vocational": "vocational",
}

VOLUME_DIRECTORY_MAP: dict[str, str] = {
    "數學B1": "math_B1",
    "數學B2": "math_B2",
    "數學B3": "math_B3",
    "數學B4": "math_B4",
}

CURRICULUM_DISPLAY_MAP: dict[str, str] = {
    "vocational": "技高",
}

VOLUME_DISPLAY_MAP: dict[str, str] = {
    "數學B1": "數學B1",
    "數學B2": "數學B2",
    "數學B3": "數學B3",
    "數學B4": "數學B4",
}


def resolve_source_directory(project_root: Path, curriculum: str, volume: str) -> tuple[Path, str]:
    """
    Resolve whitelist-mapped source directory.

    Returns:
        (absolute_directory_path, relative_directory_posix)

    Raises:
        ValueError: with machine-readable error code as first argument.
    """
    curriculum_key = str(curriculum or "").strip()
    volume_key = str(volume or "").strip()

    if curriculum_key not in CURRICULUM_DIRECTORY_MAP:
        raise ValueError(
            "invalid_curriculum",
            "課綱不在允許清單內。",
        )
    if volume_key not in VOLUME_DIRECTORY_MAP:
        raise ValueError(
            "invalid_volume",
            "冊別不在允許清單內。",
        )

    relative = SOURCE_ROOT / CURRICULUM_DIRECTORY_MAP[curriculum_key] / VOLUME_DIRECTORY_MAP[volume_key]
    absolute = Path(project_root) / relative
    return absolute, relative.as_posix()


def _read_upload_bytes(upload: FileStorage) -> bytes:
    data = upload.read()
    if hasattr(upload, "seek"):
        try:
            upload.seek(0)
        except Exception:
            pass
    if data is None:
        return b""
    return bytes(data)


def _planned_save_items(
    pairs: list[dict[str, Any]],
    docx_map: dict[str, FileStorage],
    pdf_map: dict[str, FileStorage],
    destination_dir: Path,
    relative_dir: str,
) -> list[dict[str, Any]]:
    planned: list[dict[str, Any]] = []
    for pair in pairs:
        base_name = str(pair.get("base_name") or "").strip()
        docx_upload = docx_map.get(base_name)
        pdf_upload = pdf_map.get(base_name)
        if not docx_upload or not pdf_upload:
            continue

        docx_filename = os.path.basename(str(docx_upload.filename or ""))
        pdf_filename = os.path.basename(str(pdf_upload.filename or ""))
        docx_dest = destination_dir / docx_filename
        pdf_dest = destination_dir / pdf_filename
        docx_rel = f"{relative_dir}/{docx_filename}"
        pdf_rel = f"{relative_dir}/{pdf_filename}"

        planned.append(
            {
                "base_name": base_name,
                "docx_filename": docx_filename,
                "pdf_filename": pdf_filename,
                "docx_dest": docx_dest,
                "pdf_dest": pdf_dest,
                "docx_rel": docx_rel,
                "pdf_rel": pdf_rel,
                "docx_upload": docx_upload,
                "pdf_upload": pdf_upload,
            }
        )
    return planned


def _preflight_existing_files(planned_items: list[dict[str, Any]]) -> list[str]:
    conflicts: list[str] = []
    seen: set[str] = set()
    for item in planned_items:
        for key in ("docx_dest", "pdf_dest"):
            dest: Path = item[key]
            rel = dest.name
            if dest.exists() and rel not in seen:
                conflicts.append(rel)
                seen.add(rel)
    return conflicts


def save_textbook_source_batch(
    *,
    project_root: Path,
    pairs: list[dict[str, Any]],
    docx_map: dict[str, FileStorage],
    pdf_map: dict[str, FileStorage],
    curriculum: str,
    volume: str,
) -> tuple[dict[str, Any], int]:
    try:
        destination_dir, relative_dir = resolve_source_directory(project_root, curriculum, volume)
    except ValueError as exc:
        error_code = str(exc.args[0]) if exc.args else "invalid_source_directory"
        message = str(exc.args[1]) if len(exc.args) > 1 else "來源目錄解析失敗。"
        return {
            "ok": False,
            "error": error_code,
            "message": message,
        }, 400

    planned_items = _planned_save_items(pairs, docx_map, pdf_map, destination_dir, relative_dir)
    if not planned_items:
        return {
            "ok": False,
            "error": "source_save_plan_empty",
            "message": "沒有可儲存的教材來源檔案。",
        }, 400

    conflicts = _preflight_existing_files(planned_items)
    if conflicts:
        return {
            "ok": False,
            "error": "source_file_already_exists",
            "message": "部分教材來源檔案已存在，未執行本次上傳。",
            "files": conflicts,
        }, 409

    destination_dir.mkdir(parents=True, exist_ok=True)

    written_files: list[Path] = []
    saved_pairs: list[dict[str, Any]] = []
    files_saved = 0

    try:
        for item in planned_items:
            for upload_key, dest_key, rel_key, filename_key in (
                ("docx_upload", "docx_dest", "docx_rel", "docx_filename"),
                ("pdf_upload", "pdf_dest", "pdf_rel", "pdf_filename"),
            ):
                upload: FileStorage = item[upload_key]
                dest_path: Path = item[dest_key]
                payload = _read_upload_bytes(upload)
                dest_path.write_bytes(payload)
                written_files.append(dest_path)
                files_saved += 1

            saved_pairs.append(
                {
                    **{
                        key: item[key]
                        for key in ("base_name",)
                        if key in item
                    },
                    "docx": item["docx_filename"],
                    "pdf": item["pdf_filename"],
                    "docx_path": item["docx_rel"],
                    "pdf_path": item["pdf_rel"],
                }
            )
    except Exception as exc:
        for path in written_files:
            try:
                if path.exists():
                    path.unlink()
            except Exception:
                pass
        return {
            "ok": False,
            "error": "source_save_failed",
            "message": "教材來源儲存失敗，已回滾本次寫入。",
            "details": str(exc),
        }, 500

    return {
        "ok": True,
        "storage": {
            "directory": relative_dir,
            "files_saved": files_saved,
            "curriculum_label": CURRICULUM_DISPLAY_MAP.get(str(curriculum or "").strip(), curriculum),
            "volume_label": VOLUME_DISPLAY_MAP.get(str(volume or "").strip(), volume),
        },
        "pairs": saved_pairs,
    }, 200


def upload_textbook_source_batch(
    *,
    project_root: Path,
    docx_files: list[FileStorage],
    pdf_files: list[FileStorage],
    curriculum: str,
    publisher: str,
    grade: Any,
    volume: str,
) -> tuple[dict[str, Any], int]:
    """
    Full preflight + save pipeline.

    Order:
    1. metadata / extension / pairing / duplicate validation
    2. resolve destination directory
    3. existing-file conflict check
    4. save with rollback on failure
    """
    payload, status_code = validate_textbook_source_batch(
        docx_files=docx_files,
        pdf_files=pdf_files,
        curriculum=curriculum,
        publisher=publisher,
        grade=grade,
        volume=volume,
    )
    if not payload.get("ok"):
        return payload, status_code

    docx_list = [f for f in (docx_files or []) if f and f.filename]
    pdf_list = [f for f in (pdf_files or []) if f and f.filename]

    docx_map, docx_error = build_file_map(docx_list, ALLOWED_DOCX_EXT)
    if docx_error:
        return docx_error, 400

    pdf_map, pdf_error = build_file_map(pdf_list, ALLOWED_PDF_EXT)
    if pdf_error:
        return pdf_error, 400

    save_payload, save_status = save_textbook_source_batch(
        project_root=project_root,
        pairs=payload.get("pairs") or [],
        docx_map=docx_map,
        pdf_map=pdf_map,
        curriculum=str(payload["batch"]["curriculum"]),
        volume=str(payload["batch"]["volume"]),
    )
    if not save_payload.get("ok"):
        return save_payload, save_status

    enriched_pairs = []
    saved_by_base = {p["base_name"]: p for p in save_payload.get("pairs") or []}
    for pair in payload.get("pairs") or []:
        saved = saved_by_base.get(pair["base_name"], {})
        enriched_pairs.append(
            {
                **pair,
                "docx_path": saved.get("docx_path"),
                "pdf_path": saved.get("pdf_path"),
            }
        )

    payload["pairs"] = enriched_pairs
    payload["storage"] = save_payload["storage"]
    return payload, 200
