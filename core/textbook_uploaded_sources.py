"""Permanent, hash-verified sources for general web textbook imports."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from pathlib import Path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_part(value: str) -> str:
    return re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "_", str(value or "").strip()) or "unknown"


def retain_uploaded_pair(project_root: Path, files: list[tuple[Path, str]], curriculum: str, volume: str) -> dict:
    """Publish complete originals, then an atomic pending manifest; never overwrite a version."""
    root = Path(project_root).resolve()
    directory = root / "textbook_import" / "uploaded_sources" / _safe_part(curriculum) / _safe_part(volume)
    prepared = []
    for source, original_name in files:
        source = Path(source)
        if source.suffix.lower() not in {".docx", ".pdf"}:
            raise ValueError("unsupported_source_extension")
        digest = _sha256(source)
        name = f"{digest[:12]}_{_safe_part(Path(original_name).name)}"
        prepared.append((source, directory / name, digest, original_name))
    if len({src.suffix.lower() for src, *_ in prepared}) != 2 or len(prepared) != 2:
        raise ValueError("docx_pdf_pair_required")
    if len({dest.name for _, dest, _, _ in prepared}) != 2:
        raise ValueError("source_name_collision")
    directory.mkdir(parents=True, exist_ok=True)
    for source, dest, digest, _ in prepared:
        if dest.exists():
            if _sha256(dest) != digest:
                raise ValueError("source_hash_conflict")
            continue
        fd, staging = tempfile.mkstemp(prefix=".source-", dir=directory)
        try:
            with os.fdopen(fd, "wb") as out, source.open("rb") as inp:
                for chunk in iter(lambda: inp.read(1024 * 1024), b""):
                    out.write(chunk)
                out.flush()
                os.fsync(out.fileno())
            if _sha256(Path(staging)) != digest:
                raise ValueError("source_copy_mismatch")
            try:
                os.rename(staging, dest)  # atomic; Windows rejects an existing destination
            except FileExistsError:
                if _sha256(dest) != digest:
                    raise ValueError("source_hash_conflict")
        finally:
            Path(staging).unlink(missing_ok=True)
    records = {}
    for source, dest, digest, original in prepared:
        records[source.suffix.lower().lstrip(".")] = {
            "filename": source.name,
            "original_filename": original,
            "stored_path": dest.relative_to(root).as_posix(),
            "size_bytes": dest.stat().st_size,
            "sha256": digest,
        }
    manifest = {"status": "retained_pending_import", "curriculum": curriculum, "volume": volume, "sources": records}
    identity = hashlib.sha256(json.dumps(manifest["sources"], sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    manifest_path = directory / f"{identity}.json"
    if not manifest_path.exists():
        fd, staging = tempfile.mkstemp(prefix=".manifest-", dir=directory)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as out:
                json.dump(manifest, out, ensure_ascii=False, indent=2)
                out.flush()
                os.fsync(out.fileno())
            try:
                os.rename(staging, manifest_path)
            except FileExistsError:
                pass
        finally:
            Path(staging).unlink(missing_ok=True)
    return records


def resolve_recorded_source(project_root: Path, provenance: dict) -> Path:
    """Resolve one DB recorded source by identity and full hash, without filename guessing."""
    root = Path(project_root).resolve()
    digest = str(provenance.get("sha256") or "").lower()
    if not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ValueError("missing_source_hash")
    stored = provenance.get("stored_path")
    if stored:
        candidate = (root / stored).resolve()
        allowed = root / "textbook_import" / "uploaded_sources"
        if not candidate.is_relative_to(allowed):
            raise ValueError("invalid_source_path")
        candidates = [candidate]
    else:
        # Legacy records have a temporary filename and hash, but no permanent path.
        # Scope must come from the DB row's curriculum and volume.
        curriculum, volume = provenance.get("curriculum"), provenance.get("volume")
        if not curriculum or not volume:
            raise ValueError("missing_source_scope")
        directory = root / "textbook_import" / "uploaded_sources" / _safe_part(curriculum) / _safe_part(volume)
        candidates = list(directory.glob(f"{digest[:12]}_*")) if directory.is_dir() else []
    matches = [p for p in candidates if p.is_file() and _sha256(p) == digest and (not provenance.get("size_bytes") or p.stat().st_size == provenance["size_bytes"])]
    if len(matches) != 1:
        raise ValueError("source_missing_or_ambiguous")
    return matches[0]


def resolve_db_source_pair(project_root: Path, notes: str | dict, curriculum: str, volume: str) -> tuple[Path, Path]:
    data = json.loads(notes) if isinstance(notes, str) else notes
    provenance = data.get("source_provenance") or {}
    def resolve(item):
        record = dict(provenance.get(item) or {})
        record.setdefault("curriculum", curriculum)
        record.setdefault("volume", volume)
        return resolve_recorded_source(project_root, record)
    return resolve("primary"), resolve("optional_enrich_pdf")


def resolve_stage1_source_pair(project_root: Path, notes: str | dict, curriculum: str, volume: str, section: str) -> tuple[Path, Path]:
    """Use recorded web provenance first; preserve the existing manual-source resolver."""
    data = json.loads(notes) if isinstance(notes, str) else (notes or {})
    if data.get("source_provenance"):
        return resolve_db_source_pair(project_root, data, curriculum, volume)
    from core.textbook_importer_v3_storage import resolve_project_textbook_source_pair
    pair = resolve_project_textbook_source_pair(project_root, curriculum, volume, section)
    if pair is None:
        raise ValueError("source_missing_or_ambiguous")
    return pair
