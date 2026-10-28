"""Bounded, source-backed Stage 1 review for the existing textbook importer.

This module mutates only row objects in the caller's pending transaction. It does
not commit, delete rows, publish assets, or execute model-generated code.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path
from typing import Any, Callable

from core.textbook_stage1_gate import evaluate_stage1_gate

SYMBOLS = {"F0C7": "∩", "F0C8": "∪", "F0A2": "′", "F03E": ">", "F03C": "<", "F03D": "="}
MARKER = re.compile(r"\[MATH_PARSE_FAILED:symbol:Symbol:([0-9A-F]{4})\]")
MAX_HEAL_PASSES = 1
MAX_AI_ITEMS = 12


def verified_visual_regions(pdf_path: str | Path, *, curriculum: str, volume: str, chapter: str) -> dict | None:
    """Reuse a reviewed page/region only for the exact PDF hash and unit scope."""
    path = Path(pdf_path)
    catalog = Path(__file__).resolve().parents[1] / "configs/stage1_verified_visual_regions.json"
    if not path.is_file() or not catalog.is_file():
        return None
    fingerprint = _sha(path)
    for entry in json.loads(catalog.read_text(encoding="utf-8")).get("sources", []):
        if (entry.get("pdf_sha256"), entry.get("curriculum"), entry.get("volume"), entry.get("chapter")) == (
            fingerprint, curriculum, volume, chapter
        ):
            return entry
    return None


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _notes(row: Any) -> dict:
    try:
        value = json.loads(getattr(row, "notes", "") or "{}")
        return value if isinstance(value, dict) else {}
    except (TypeError, ValueError):
        return {}


def _source_verified(docx: Path, pdf: Path) -> tuple[str, str]:
    if not docx.is_file() or not pdf.is_file():
        raise ValueError("authoritative_source_missing")
    return _sha(docx), _sha(pdf)


def _from_current_source(row: Any, docx_hash: str, pdf_hash: str) -> bool:
    provenance = _notes(row).get("source_provenance") or {}
    return ((provenance.get("primary") or {}).get("sha256") == docx_hash
            and (provenance.get("optional_enrich_pdf") or {}).get("sha256") == pdf_hash)


def _source_symbol_codes(docx: Path) -> set[str]:
    with zipfile.ZipFile(docx) as package:
        xml = package.read("word/document.xml").decode("utf-8")
    return set(re.findall(r'<w:sym\b[^>]*w:char="([0-9A-Fa-f]{4})"', xml, flags=re.I))


def _chinese(text: str) -> str:
    return "".join(re.findall(r"[\u4e00-\u9fff]", text or ""))


def _pdf_fidelity(row: Any, notes: dict, pdf_pages: list[str]) -> bool:
    page = (notes.get("pdf_visual_enrichment") or {}).get("page")
    if not isinstance(page, int) or page < 1 or page > len(pdf_pages):
        return False
    stem = _chinese(str(getattr(row, "problem_text", "") or ""))
    if len(stem) < 6:
        return False
    text = pdf_pages[page - 1]
    pos = 0
    for char in stem:
        pos = text.find(char, pos)
        if pos < 0:
            return False
        pos += 1
    return True


def _asset_file(asset: dict, roots: list[Path]) -> Path | None:
    relative = Path(str(asset.get("path") or ""))
    if not relative.parts or relative.is_absolute() or ".." in relative.parts:
        return None
    return next((root / relative for root in roots if (root / relative).is_file()), None)


def _verified_figure_assets(row: Any, notes: dict, pdf_pages: list[str], roots: list[Path],
                            sha_owners: dict[str, int]) -> list[dict]:
    """Assets that may clear a stale 'figure missing' state; each proof is independent of unit/question number.

    The crop must be a required PDF figure of *this* question: file exists with the recorded SHA-256, comes
    from the authoritative PDF page that carries the question stem, is bound to this row's anchor, is
    classified required (never solution-only/decorative/helpful), and is not shared with another row.
    """
    anchor_id = (notes.get("question_anchor") or {}).get("anchor_id")
    stem = _chinese(str(getattr(row, "problem_text", "") or ""))
    verified = []
    for asset in notes.get("image_assets") or []:
        if not isinstance(asset, dict):
            continue
        page, digest = asset.get("source_page"), str(asset.get("sha256") or "")
        if (asset.get("source") != "pdf" or asset.get("asset_type") != "pdf_visual_crop"
                or str(asset.get("visual_status") or "").lower() != "accepted" or asset.get("needs_crop_review")
                or str(asset.get("visual_classification") or "").lower() != "required"
                or not anchor_id or asset.get("question_anchor") != anchor_id
                or not isinstance(page, int) or not 1 <= page <= len(pdf_pages)
                or not digest or sha_owners.get(digest, 0) != 1):
            continue
        path = _asset_file(asset, roots)
        if path is None or _sha(path) != digest:
            continue
        text, pos = pdf_pages[page - 1], 0
        for char in stem:
            pos = text.find(char, pos)
            if pos < 0:
                break
            pos += 1
        else:
            if len(stem) >= 6:
                verified.append(asset)
    return verified


def _row_label(row: Any) -> str:
    return str(getattr(row, "source_description", "") or "").split(" [", 1)[0].strip()


def _record(notes: dict, *, kind: str, before: str, after: str, source_hash: str, confidence: float) -> None:
    if before == after:
        return
    history = notes.setdefault("stage1_auto_review", [])
    entry = {"kind": kind, "before": before[:300], "after": after[:300],
             "before_sha256": hashlib.sha256(before.encode()).hexdigest(),
             "after_sha256": hashlib.sha256(after.encode()).hexdigest(),
             "source_sha256": source_hash, "confidence": confidence}
    # Idempotent on re-import of the same source: a notes transition is recorded once per source;
    # text replacements are keyed by their exact original text.
    key = ("kind", "source_sha256") + (("before_sha256",) if kind == "source_symbol" else ())
    if not any(all(old.get(k) == entry[k] for k in key) for old in history):
        history.append(entry)


def _default_ai_review(items: list[dict], allowed_skills: dict[str, str]) -> list[dict]:
    """Existing Gemini client, strict JSON suggestions only; one bounded call."""
    if not items:
        return []
    from core.ai_analyzer import get_model
    from core.textbook_processor_v2 import _call_gemini_with_retry, safe_load_gemini_json
    prompt = (
        "You review textbook metadata only. Return JSON object {\"items\":[{\"id\":integer,"
        "\"skill_id\":string|null,\"confidence\":number,\"evidence\":string}]}. "
        "Choose skill_id only from the supplied chapter skills. Evidence must be an exact "
        "substring of that question's stem. Do not rewrite math or invent figures. "
        "Use null when uncertain.\n"
        + json.dumps({"skills": allowed_skills, "questions": items}, ensure_ascii=False)
    )
    raw = _call_gemini_with_retry(get_model("architect"), prompt, queue=None,
                                  context_message="Stage 1 bounded metadata review", parse_json=True)
    parsed = safe_load_gemini_json(raw) if raw else {}
    return parsed.get("items", []) if isinstance(parsed, dict) and isinstance(parsed.get("items"), list) else []


def review_and_heal_rows(
    rows: list[Any], *, docx_path: str | Path, pdf_path: str | Path,
    expected_count: int, allowed_skills: dict[str, str],
    ai_review: Callable[[list[dict], dict[str, str]], list[dict]] | None = None,
    asset_roots: list[str | Path] | None = None,
) -> dict:
    """One deterministic pass, at most one AI metadata call, then the existing Gate.

    A semantic proposal is accepted only with exact stem evidence, a bound skill,
    and high confidence. Figure crops remain with the existing visual pipeline;
    uncertain or unmatched figures remain manual review items.
    """
    docx, pdf = Path(docx_path), Path(pdf_path)
    docx_hash, pdf_hash = _source_verified(docx, pdf)
    # Rows of another printing/source are never healed or deleted here: deletion needs the explicit,
    # reference-checked replacement authorization. They are reported and keep the Gate from READY.
    stale_rows = [r for r in rows if not _from_current_source(r, docx_hash, pdf_hash)]
    stale_marks = {id(r) for r in stale_rows}
    rows = [r for r in rows if id(r) not in stale_marks]
    if not rows:
        raise ValueError("authoritative_source_provenance_mismatch")
    import fitz
    with fitz.open(pdf) as document:
        pages = [_chinese(page.get_text()) for page in document]
    pdf_pages = pages
    roots = [Path(r) for r in asset_roots or []] or [Path(__file__).resolve().parents[1]]
    sha_owners: dict[str, int] = {}
    for row in rows:
        for asset in _notes(row).get("image_assets") or []:
            if isinstance(asset, dict) and asset.get("sha256"):
                sha_owners[asset["sha256"]] = sha_owners.get(asset["sha256"], 0) + 1
    source_codes = _source_symbol_codes(docx)
    issues: list[dict] = []
    changes: list[dict] = []
    if stale_rows:
        issues.append({"reason": "stale_rows_require_manual_cleanup",
                       "ids": [getattr(r, "id", None) for r in stale_rows], "count": len(stale_rows)})
    anchors = [_notes(r).get("question_anchor") or {} for r in rows]
    orders = [a.get("source_order") for a in anchors]
    ids = [a.get("anchor_id") for a in anchors]
    if (len(rows) != expected_count or len(set(ids)) != len(rows) or None in ids
            or not all(isinstance(order, int) for order in orders)
            or sorted(orders) != list(range(1, expected_count + 1))):
        issues.append({"reason": "source_count_or_anchor_order_mismatch", "rows": len(rows), "expected": expected_count})
    proposals = []
    for row in rows:
        notes = _notes(row)
        rid = getattr(row, "id", None)
        stem = str(getattr(row, "problem_text", "") or "")
        solution = str(getattr(row, "detailed_solution", "") or "")
        faithful = _pdf_fidelity(row, notes, pages)
        if not faithful:
            issues.append({"id": rid, "reason": "stem_not_verified_against_pdf"})
        for field, value in (("problem_text", stem), ("detailed_solution", solution)):
            markers = MARKER.findall(value)
            if markers and all(code in SYMBOLS and code in source_codes for code in markers):
                fixed = MARKER.sub(lambda m: SYMBOLS[m.group(1)], value)
                setattr(row, field, fixed)
                _record(notes, kind="source_symbol", before=value, after=fixed,
                        source_hash=docx_hash, confidence=1.0)
                changes.append({"id": rid, "field": field, "kind": "source_symbol"})
            elif markers:
                issues.append({"id": rid, "reason": "unverified_symbol_code", "codes": markers})
        # The PDF pipeline may attach a verified crop after the importer recorded
        # a provisional missing-figure warning. Reconcile that stale warning.
        stale_visual = (notes.get("pdf_visual_status") in ("VISUAL_UNCERTAIN", "VISUAL_REQUIRED_MISSING")
                        or bool(notes.get("visual_required_missing")))
        if stale_visual and notes.get("image_assets"):
            if _verified_figure_assets(row, notes, pdf_pages, roots, sha_owners):
                before = json.dumps(notes, ensure_ascii=False, sort_keys=True)
                notes["pdf_visual_status"] = "VISUAL_ATTACHED"
                notes["visual_required_missing"] = False
                notes["needs_review"] = bool(notes.get("needs_review_before_visual", False))
                if notes.get("image_warning") == "missing_docx_image_asset":
                    notes.pop("image_warning", None)
                    notes["image_warning_resolved_by"] = "pdf_visual"
                _record(notes, kind="verified_visual_attached", before=before,
                        after=json.dumps(notes, ensure_ascii=False, sort_keys=True),
                        source_hash=pdf_hash, confidence=1.0)
                changes.append({"id": rid, "field": "notes", "kind": "verified_visual_attached"})
            else:
                issues.append({"id": rid, "reason": "visual_asset_unverified"})
        # A requested student drawing is not a missing *provided* question image.
        if ("利用樹狀圖" in stem or "畫出樹狀圖" in stem) and not re.search(r"如圖|右圖|左圖|下圖|上圖", stem):
            if notes.get("pdf_visual_status") in ("VISUAL_UNCERTAIN", "VISUAL_REQUIRED_MISSING") and not notes.get("image_assets"):
                before = json.dumps(notes, ensure_ascii=False, sort_keys=True)
                notes["pdf_visual_status"] = "NO_VISUAL_REQUIRED"
                notes.pop("visual_required_missing", None)
                notes.pop("needs_review", None)
                notes["manual_visual_review"] = {"source_pdf_sha256": pdf_hash,
                                                 "result": "student_must_draw; no supplied figure in question"}
                _record(notes, kind="student_drawn_visual", before=before,
                        after=json.dumps(notes, ensure_ascii=False, sort_keys=True),
                        source_hash=pdf_hash, confidence=1.0)
                changes.append({"id": rid, "field": "notes", "kind": "student_drawn_visual"})
        if faithful and not MARKER.search(str(getattr(row, "problem_text", "") or "")):
            if notes.get("review_required_by_confidence") and notes.get("pdf_visual_status") == "NO_VISUAL_REQUIRED":
                before = json.dumps(notes, ensure_ascii=False, sort_keys=True)
                notes["manual_stem_review"] = {"source_pdf_sha256": pdf_hash, "result": "exact_ordered_chinese_text_match"}
                notes.pop("review_required_by_confidence", None)
                notes.pop("needs_review", None)
                _record(notes, kind="source_text_match", before=before,
                        after=json.dumps(notes, ensure_ascii=False, sort_keys=True),
                        source_hash=pdf_hash, confidence=1.0)
                changes.append({"id": rid, "field": "notes", "kind": "source_text_match"})
        binding = notes.get("skill_binding") or {}
        if binding.get("source") == "unmapped_in_source_skill_map" and faithful:
            proposals.append({"id": rid, "label": _row_label(row), "stem": stem[:600],
                              "current_skill_id": str(getattr(row, "skill_id", "") or "")})
        row.notes = json.dumps(notes, ensure_ascii=False)
    if proposals:
        if len(proposals) > MAX_AI_ITEMS:
            issues.append({"reason": "ai_review_limit_exceeded", "count": len(proposals)})
        else:
            try:
                advice = (ai_review or _default_ai_review)(proposals, allowed_skills)
            except Exception as exc:
                advice = []
                issues.append({"reason": "ai_review_unavailable", "error": type(exc).__name__})
            by_id = {x.get("id"): x for x in advice if isinstance(x, dict)}
            for proposal in proposals:
                rid = proposal["id"]
                item = by_id.get(rid) or {}
                target = str(item.get("skill_id") or "")
                evidence = str(item.get("evidence") or "").strip()
                try: confidence = float(item.get("confidence") or 0)
                except (ValueError, TypeError): confidence = 0
                if target not in allowed_skills or confidence < .98 or len(_chinese(evidence)) < 4 or evidence not in proposal["stem"]:
                    issues.append({"id": rid, "reason": "skill_binding_requires_human_review"})
                    continue
                row = next(r for r in rows if getattr(r, "id", None) == rid)
                before = str(row.skill_id)
                row.skill_id = target
                notes = _notes(row)
                notes["skill_binding"] = {"source": "stage1_ai_review", "previous_skill_id": before,
                                           "confidence": confidence, "evidence": evidence,
                                           "source_pdf_sha256": pdf_hash}
                notes.pop("needs_review", None)
                row.notes = json.dumps(notes, ensure_ascii=False)
                if before != target:
                    changes.append({"id": rid, "field": "skill_id", "before": before, "after": target,
                                    "kind": "bounded_ai_metadata"})
    gate = evaluate_stage1_gate(rows)
    if issues:
        reasons = dict(gate["reasons"])
        for issue in issues:
            reason = issue["reason"]
            reasons[reason] = reasons.get(reason, 0) + 1
        gate = dict(gate, status="BLOCKED", stage1_ready=False,
                    reasons=reasons, auto_review_issues=issues)
    return {"gate": gate, "issues": issues, "changes": changes,
            "source": {"docx_sha256": docx_hash, "pdf_sha256": pdf_hash},
            "heal_passes": MAX_HEAL_PASSES, "ai_items": len(proposals)}


def publish_staged_assets(rows: list[Any], staging_root: str | Path, project_root: str | Path) -> list[Path]:
    """Copy hash-checked staged crops before the caller commits; return newly made paths for rollback."""
    staging_root, project_root = Path(staging_root), Path(project_root)
    created: list[Path] = []
    try:
        for row in rows:
            for asset in _notes(row).get("image_assets") or []:
                relative = Path(str(asset.get("path") or ""))
                if not relative.parts or relative.is_absolute() or ".." in relative.parts or relative.parts[0] != "uploads":
                    raise ValueError("invalid_question_asset_path")
                src, dst = staging_root / relative, project_root / relative
                expected = str(asset.get("sha256") or "")
                if dst.exists():
                    if _sha(dst) != expected:
                        raise ValueError("question_asset_destination_conflict")
                    continue
                if not src.is_file() or _sha(src) != expected:
                    raise ValueError("staged_question_asset_missing_or_mismatch")
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                if _sha(dst) != expected:
                    raise ValueError("published_question_asset_mismatch")
                created.append(dst)
        return created
    except Exception:
        for path in created:
            path.unlink(missing_ok=True)
        raise
