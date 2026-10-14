"""Read-only question scope for the optional V3 importer mode."""

from __future__ import annotations

import sys
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any

from lxml import etree

from core.textbook_importer_v3_docx import (
    NS, REL_NS, _element_xml_path, _load_relationship_maps, _resolve_relationship_target,
    parse_docx_structure,
)
from core.textbook_question_anchor import infer_source_type_from_label


def _near_text_for_paragraph(paragraph_xml: list[etree._Element], paragraph_index: int | None) -> str:
    if paragraph_index is None or paragraph_index < 0 or paragraph_index >= len(paragraph_xml):
        return ""
    text = "".join(paragraph_xml[paragraph_index].itertext())
    text = " ".join(text.split())
    if len(text) <= 100:
        return text
    return text[:50] + " … " + text[-50:]


def _source_scope_from_location(location: dict[str, Any], paragraph_index: int | None) -> dict[str, Any] | None:
    """Build a non-question source scope from the formula's DOCX anchor."""
    if not isinstance(location, dict):
        location = {}
    scope: dict[str, Any] = {}
    if paragraph_index is not None:
        scope["kind"] = "paragraph"
        scope["paragraph_index"] = paragraph_index
    if location.get("table_index") is not None:
        scope["kind"] = "table_cell"
        scope["table_index"] = location.get("table_index")
        scope["row"] = location.get("row")
        scope["col"] = location.get("col")
        if paragraph_index is not None:
            scope["paragraph_index"] = paragraph_index
    if location.get("block_index") is not None:
        scope["block_index"] = location.get("block_index")
    if location.get("run_index") is not None:
        scope["run_index"] = location.get("run_index")
    if location.get("in_table_cell"):
        scope["in_table_cell"] = True
    return scope or None


def _log_formula_scope_error(
    *,
    source_docx: Path,
    kind: str | None,
    formula_index: Any,
    item: dict[str, Any],
    location: dict[str, Any],
    paragraph_index: int | None,
    question_scope: Any,
    source_scope: dict[str, Any] | None,
    near_text: str,
    reason: str,
) -> None:
    print(
        "[FORMULA_SCOPE_ERROR]\n"
        f"file={source_docx.name}\n"
        f"stage=FORMULA_CONVERSION\n"
        f"object_index={formula_index}\n"
        f"kind={kind}\n"
        f"progId={item.get('prog_id') or item.get('progId') or (item.get('classification') or '')}\n"
        f"object_type={item.get('status') or item.get('classification') or kind}\n"
        f"paragraph_index={paragraph_index}\n"
        f"table_index={location.get('table_index')}\n"
        f"row={location.get('row')}\n"
        f"col={location.get('col')}\n"
        f"question_scope={question_scope!r}\n"
        f"source_scope={source_scope!r}\n"
        f"near_text={near_text!r}\n"
        f"reason={reason}",
        flush=True,
    )


def analyze_scoped_conversion(
    source_docx: Path,
    converted_docx: Path,
    curriculum_info: dict[str, Any],
    conversion_report: dict[str, Any],
    target_source_types: set[str],
) -> dict[str, Any]:
    """Use existing Phase 2 classifications and source line provenance; never write DB."""
    import core.textbook_processor_v2 as tpv2
    import core.textbook_mathtype_converter as converter

    locations: list[int] = []
    lines = tpv2.phase1_extract_docx_lines(
        str(converted_docx), curriculum_info=curriculum_info, locations=locations
    )
    source_scope = str(curriculum_info.get("source_scope") or "section_textbook")
    self_assessment_target = (
        source_scope == "chapter_self_assessment"
        and "self_assessment" in target_source_types
    )
    blocks = tpv2.phase2_deterministic_block_slice(
        lines, source_scope=source_scope, curriculum_info=curriculum_info,
        read_only=True,
    )
    metadata = dict(tpv2._DOCX_BLOCK_META)
    source_structure = parse_docx_structure(source_docx.read_bytes(), include_blocks=True)
    paragraph_by_path = {
        str(p.get("xml_path") or ""): p["paragraph_index"]
        for block in source_structure.get("blocks") or []
        for p in ([block] if block.get("type") == "paragraph" else [
            para for row in block.get("rows") or []
            for cell in row.get("cells") or []
            for para in cell.get("paragraphs") or []
        ])
    }
    source_paragraphs = set(paragraph_by_path.values())
    questions: list[dict[str, Any]] = []
    owner_by_paragraph: dict[int, list[int]] = {}
    unresolved: list[dict[str, Any]] = []
    for index, (label, block) in enumerate(metadata.items(), 1):
        source_type = str(block.get("source_type") or infer_source_type_from_label(label))
        paragraph_ids = set()
        for line_index in block.get("source_line_indices") or []:
            if line_index < 0 or line_index >= len(locations) or locations[line_index] < 0:
                unresolved.append({"question": label, "line_index": line_index, "reason": "line_location_missing"})
                continue
            paragraph_ids.add(locations[line_index])
        if not paragraph_ids or not paragraph_ids.issubset(source_paragraphs):
            unresolved.append({"question": label, "reason": "question_paragraph_unresolved"})
        question = {
            "index": index, "label": label, "source_type": source_type,
            "target": source_type in target_source_types,
            "paragraph_indices": sorted(paragraph_ids),
            "problem_start": str(block.get("problem_text") or "")[:80],
            "section": block.get("section_title") or curriculum_info.get("section"),
            "skill_id": block.get("formal_skill_id") or None,
            "formula_count": 0, "formula_failed": 0,
            "image_candidates": [],
        }
        questions.append(question)
        for paragraph_index in paragraph_ids:
            owner_by_paragraph.setdefault(paragraph_index, []).append(index)

    counts = Counter({
        "required_formula_count": 0, "required_formula_success": 0,
        "required_formula_failed": 0, "non_required_formula_count": 0,
        "non_required_formula_success": 0, "non_required_formula_failed": 0,
        "non_formula_object_skipped": 0,
    })
    failures: list[dict[str, Any]] = []
    body_formula_scopes: list[dict[str, Any]] = []
    formula_items = [
        ("mathtype_ole", item.get("formula_index"), item)
        for item in conversion_report.get("formulas") or []
    ] + [
        ("word_eq", item.get("field_index"), item)
        for item in conversion_report.get("eq_field_results") or []
    ]

    with zipfile.ZipFile(source_docx) as package:
        root = etree.fromstring(package.read("word/document.xml"))
        rel_maps = _load_relationship_maps(package)
        paragraph_xml = root.xpath(".//w:p", namespaces=NS)

        for kind, formula_index, item in formula_items:
            location = item.get("location") or {}
            paragraph_index = location.get("paragraph_index")
            source_anchor = _source_scope_from_location(location, paragraph_index)
            near_text = _near_text_for_paragraph(paragraph_xml, paragraph_index)

            # Embedded Office packages / non-MathType OLE are not formulas.
            if item.get("status") == "not_mtef" or item.get("classification") == "embedded_ooxml":
                counts["non_formula_object_skipped"] += 1
                continue

            if paragraph_index not in source_paragraphs:
                # Table/cell/run anchors still count as a resolvable source scope.
                if source_anchor and (
                    source_anchor.get("table_index") is not None
                    or source_anchor.get("block_index") is not None
                    or source_anchor.get("run_index") is not None
                ):
                    owners = []
                    question_scope = None
                else:
                    reason = "formula_location_missing"
                    unresolved_item = {
                        "formula_index": formula_index,
                        "kind": kind,
                        "reason": reason,
                        "location": location,
                        "question_scope": None,
                        "source_scope": source_anchor,
                        "near_text": near_text,
                        "prog_id": item.get("prog_id"),
                    }
                    unresolved.append(unresolved_item)
                    _log_formula_scope_error(
                        source_docx=source_docx,
                        kind=kind,
                        formula_index=formula_index,
                        item=item,
                        location=location,
                        paragraph_index=paragraph_index,
                        question_scope=None,
                        source_scope=source_anchor,
                        near_text=near_text,
                        reason=reason,
                    )
                    continue
            else:
                owners = owner_by_paragraph.get(paragraph_index, [])
                question_scope = owners[0] if len(owners) == 1 else (owners or None)

            target_owners = [owner for owner in owners if questions[owner - 1]["target"]]
            if self_assessment_target and not owners:
                reason = "unresolved_formula_scope"
                unresolved.append({
                    "formula_index": formula_index, "kind": kind,
                    "paragraph_index": paragraph_index,
                    "reason": reason,
                    "question_scope": None,
                    "source_scope": source_anchor,
                    "near_text": near_text,
                })
                _log_formula_scope_error(
                    source_docx=source_docx,
                    kind=kind,
                    formula_index=formula_index,
                    item=item,
                    location=location,
                    paragraph_index=paragraph_index,
                    question_scope=None,
                    source_scope=source_anchor,
                    near_text=near_text,
                    reason=reason,
                )
                continue
            if not owners and any(
                q["target"] and q["paragraph_indices"]
                and min(q["paragraph_indices"]) <= paragraph_index <= max(q["paragraph_indices"])
                for q in questions
            ):
                reason = "formula_inside_target_span_without_owner"
                unresolved.append({
                    "formula_index": formula_index, "kind": kind,
                    "reason": reason,
                    "paragraph_index": paragraph_index,
                    "question_scope": None,
                    "source_scope": source_anchor,
                    "near_text": near_text,
                })
                _log_formula_scope_error(
                    source_docx=source_docx,
                    kind=kind,
                    formula_index=formula_index,
                    item=item,
                    location=location,
                    paragraph_index=paragraph_index,
                    question_scope=None,
                    source_scope=source_anchor,
                    near_text=near_text,
                    reason=reason,
                )
                continue
            if len(owners) > 1:
                reason = "overlapping_question_blocks"
                unresolved.append({
                    "formula_index": formula_index, "kind": kind,
                    "reason": reason, "owners": owners,
                    "question_scope": owners,
                    "source_scope": source_anchor,
                    "near_text": near_text,
                })
                _log_formula_scope_error(
                    source_docx=source_docx,
                    kind=kind,
                    formula_index=formula_index,
                    item=item,
                    location=location,
                    paragraph_index=paragraph_index,
                    question_scope=owners,
                    source_scope=source_anchor,
                    near_text=near_text,
                    reason=reason,
                )
                continue

            # Body / definition formulas may have no question owner. A valid DOCX
            # paragraph/table/run anchor is enough for source fidelity.
            required = bool(target_owners)
            if not required:
                body_formula_scopes.append({
                    "formula_index": formula_index,
                    "kind": kind,
                    "question_scope": None,
                    "source_scope": source_anchor,
                    "status": item.get("status"),
                })

            prefix = "required" if required else "non_required"
            counts[prefix + "_formula_count"] += 1
            if item.get("status") == "ok":
                counts[prefix + "_formula_success"] += 1
            else:
                counts[prefix + "_formula_failed"] += 1
                failures.append({
                    "formula_index": formula_index, "kind": kind,
                    "question_index": target_owners[0] if target_owners else None,
                    "location": location, "error": item.get("error"),
                    "converted": item.get("latex"),
                    "source_scope": source_anchor,
                })
            if owners:
                questions[owners[0] - 1]["formula_count"] += 1
                if item.get("status") != "ok":
                    questions[owners[0] - 1]["formula_failed"] += 1

        # OMML is not converted by the MathType converter; target OMML needs review.
        previews = {f.get("preview_media_path") for f in source_structure.get("mathtype_oles") or []}
        for paragraph in paragraph_xml:
            paragraph_index = paragraph_by_path.get(_element_xml_path(paragraph))
            if paragraph_index is None:
                continue
            owners = owner_by_paragraph.get(paragraph_index, [])
            omml = paragraph.xpath(".//m:oMath", namespaces={"m": "http://schemas.openxmlformats.org/officeDocument/2006/math"})
            if omml and any(questions[o - 1]["target"] for o in owners):
                unresolved.append({"paragraph_index": paragraph_index, "reason": "target_omml_not_converted", "count": len(omml)})
            if len(owners) != 1 or not questions[owners[0] - 1]["target"]:
                continue
            for node, attr in [
                *((n, "id") for n in paragraph.xpath(".//v:imagedata", namespaces=NS)),
                *((n, "embed") for n in paragraph.xpath(".//a:blip", namespaces=NS)),
            ]:
                rel_id = node.get(f"{{{REL_NS}}}{attr}")
                path, _ = _resolve_relationship_target("word/document.xml", rel_id or "", rel_maps)
                if not path or path in previews or Path(path).suffix.lower() in {".wmf", ".emf"}:
                    continue
                questions[owners[0] - 1]["image_candidates"].append({
                    "paragraph_index": paragraph_index, "relationship_id": rel_id,
                    "filename": Path(path).name, "needs_review": True,
                })

    for question in questions:
        question["would_write"] = (
            "NO" if not question["target"] else
            "BLOCKED_FORMULA" if question["formula_failed"] else "YES"
        )
    target_type_counts = Counter({source_type: 0 for source_type in target_source_types})
    target_type_counts.update(q["source_type"] for q in questions if q["target"])
    return {
        "questions": questions, "question_count": len(blocks),
        "target_count": sum(q["target"] for q in questions),
        "target_source_type_counts": dict(sorted(target_type_counts.items())),
        "counts": dict(counts), "failures": failures, "unresolved": unresolved,
        "body_formula_scopes": body_formula_scopes,
        "image_candidate_count": sum(len(q["image_candidates"]) for q in questions),
        "image_needs_review_count": sum(
            im["needs_review"] for q in questions for im in q["image_candidates"]
        ),
        "would_write_count": sum(q["would_write"] == "YES" for q in questions),
        "runtime": {
            "sys_executable": sys.executable,
            "olefile": getattr(converter.olefile, "__file__", None),
            "converter": converter.__file__,
        },
    }
