# -*- coding: utf-8 -*-
"""V3 教材匯入：DOCX 唯讀結構解析（Phase 2A）。"""

from __future__ import annotations

import hashlib
import io
import os
import zipfile
from pathlib import Path
from typing import Any, BinaryIO

from lxml import etree

try:
    import olefile
except ImportError:  # pragma: no cover - optional at runtime
    olefile = None

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "o": "urn:schemas-microsoft-com:office:office",
    "v": "urn:schemas-microsoft-com:vml",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
}

REL_NS = NS["r"]
W_NS = NS["w"]
INDEPENDENT_IMAGE_EXTS = {".jpg", ".jpeg", ".png"}
FORMULA_PREVIEW_EXTS = {".wmf", ".emf"}

REFERENCE_SOURCE_REL_DIR = Path("textbook_import") / "source" / "vocational" / "math_B2"
REFERENCE_BASENAME_FRAGMENT = "第一章 1-1 角度的基本性質-課本"

REFERENCE_STATISTICS = {
    "mathtype_ole": 142,
    "mathtype_ole_in_table_cells": 81,
    "eq_fields": 5,
    "eq_fields_in_table_cells": 4,
    "tables": 14,
    "table_cells": 71,
    "independent_images": 24,
    "independent_jpeg": 19,
    "independent_png": 5,
    "media_physical_files": 156,
    "media_wmf": 132,
    "media_jpeg": 19,
    "media_png": 5,
    "ole_embeddings": 142,
}


def find_reference_docx_in_storage(project_root: str | os.PathLike[str]) -> Path | None:
    """Locate reference DOCX under textbook_import/source/vocational/math_B2/."""
    base = Path(project_root) / REFERENCE_SOURCE_REL_DIR
    if not base.is_dir():
        return None
    matches = sorted(
        path
        for path in base.glob("*.docx")
        if REFERENCE_BASENAME_FRAGMENT in path.stem
    )
    return matches[0] if matches else None


def _local_name(tag: str | bytes | None) -> str:
    if not tag:
        return ""
    text = tag.decode("utf-8") if isinstance(tag, bytes) else str(tag)
    return text.split("}", 1)[-1] if "}" in text else text


def _read_source_bytes(source: str | os.PathLike[str] | BinaryIO | bytes) -> tuple[bytes, str]:
    filename = ""
    if isinstance(source, (str, os.PathLike)):
        path = os.fspath(source)
        filename = os.path.basename(path)
        with open(path, "rb") as fh:
            return fh.read(), filename
    if isinstance(source, bytes):
        return source, filename
    if hasattr(source, "read"):
        raw = source.read()
        filename = os.path.basename(str(getattr(source, "filename", "") or ""))
        if hasattr(source, "seek"):
            try:
                source.seek(0)
            except Exception:
                pass
        return raw, filename
    raise TypeError(f"Unsupported DOCX source type: {type(source)!r}")


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _rels_path_for_part(part_path: str) -> str:
    folder, basename = os.path.split(part_path.replace("\\", "/"))
    return f"{folder}/_rels/{basename}.rels"


def _load_relationship_maps(zf: zipfile.ZipFile) -> dict[str, dict[str, str]]:
    rels: dict[str, dict[str, str]] = {}
    for name in zf.namelist():
        normalized = name.replace("\\", "/")
        if not normalized.endswith(".rels"):
            continue
        try:
            root = etree.fromstring(zf.read(name))
        except Exception:
            continue
        mapping: dict[str, str] = {}
        for rel in root.findall(f".//{{{NS['rel']}}}Relationship"):
            rel_id = rel.get("Id")
            target = rel.get("Target", "")
            rel_type = rel.get("Type", "")
            if not rel_id:
                continue
            mapping[rel_id] = target
            mapping[f"__type__:{rel_id}"] = rel_type
        rels[normalized] = mapping
    return rels


def _resolve_relationship_target(
    part_path: str,
    rel_id: str,
    rel_maps: dict[str, dict[str, str]],
) -> tuple[str | None, str | None]:
    rels_path = _rels_path_for_part(part_path.replace("\\", "/"))
    mapping = rel_maps.get(rels_path, {})
    target = mapping.get(rel_id)
    rel_type = mapping.get(f"__type__:{rel_id}")
    if not target:
        return None, rel_type
    part_dir = os.path.dirname(part_path.replace("\\", "/"))
    if target.startswith("/"):
        return target.lstrip("/"), rel_type
    resolved = os.path.normpath(os.path.join(part_dir, target)).replace("\\", "/")
    return resolved, rel_type


def _collect_media_paths(zf: zipfile.ZipFile) -> list[str]:
    return sorted(
        name.replace("\\", "/")
        for name in zf.namelist()
        if name.replace("\\", "/").startswith("word/media/")
    )


def _collect_embedding_paths(zf: zipfile.ZipFile) -> list[str]:
    return sorted(
        name.replace("\\", "/")
        for name in zf.namelist()
        if name.replace("\\", "/").startswith("word/embeddings/")
        and not name.endswith("/")
    )


def _extract_plain_text(element: etree._Element) -> str:
    parts: list[str] = []
    for node in element.xpath(".//w:t", namespaces=NS):
        if node.text:
            parts.append(node.text)
    return "".join(parts)


def _element_xml_path(element: etree._Element, *, root_tag: str = "body") -> str:
    parts: list[str] = []
    current: etree._Element | None = element
    while current is not None:
        parent = current.getparent()
        if parent is None:
            break
        local = _local_name(current.tag)
        siblings = [child for child in parent if _local_name(child.tag) == local]
        if len(siblings) > 1:
            index = siblings.index(current)
            parts.append(f"{local}[{index}]")
        else:
            parts.append(local)
        current = parent
        if _local_name(current.tag) == root_tag:
            parts.append(root_tag)
            break
    return "/".join(reversed(parts))


def _paragraph_has_image(paragraph_elem: etree._Element) -> bool:
    if paragraph_elem.xpath(".//v:imagedata", namespaces=NS):
        return True
    if paragraph_elem.xpath(".//a:blip", namespaces=NS):
        return True
    if paragraph_elem.xpath(".//w:drawing", namespaces=NS):
        return True
    if paragraph_elem.xpath(".//w:pict", namespaces=NS):
        return True
    return False


def _iter_run_elements(parent: etree._Element):
    for child in parent:
        local = _local_name(child.tag)
        if local == "r":
            yield child
        elif local in {"hyperlink", "smartTag", "ins", "del", "sdt"}:
            content = child
            if local == "sdt":
                content = child.find("w:sdtContent", namespaces=NS)
                if content is None:
                    continue
            yield from _iter_run_elements(content)


def _validate_ole_cfb(zf: zipfile.ZipFile, embedding_path: str | None) -> bool | None:
    if not embedding_path or olefile is None:
        return None
    normalized = embedding_path.replace("\\", "/")
    try:
        data = zf.read(normalized)
    except KeyError:
        return False
    try:
        return bool(olefile.isOleFile(io.BytesIO(data)))
    except Exception:
        return False


class _DocxStructureParser:
    def __init__(self, zf: zipfile.ZipFile, *, filename: str, include_blocks: bool, source_bytes: bytes) -> None:
        self.zf = zf
        self.filename = filename
        self.include_blocks = include_blocks
        self.source_bytes = source_bytes
        self.rel_maps = _load_relationship_maps(zf)
        self.blocks: list[dict[str, Any]] = []
        self.mathtype_oles: list[dict[str, Any]] = []
        self.eq_fields: list[dict[str, Any]] = []
        self.media: list[dict[str, Any]] = []
        self._mathtype_counter = 0
        self._eq_counter = 0
        self._block_index = -1
        self._paragraph_counter = 0
        self._table_counter = -1
        self._paragraph_block_counter = 0
        self._ole_preview_media_paths: set[str] = set()
        self._formula_run_index: dict[str, int] = {}
        self._summary: dict[str, Any] = {
            "paragraphs": 0,
            "paragraph_blocks": 0,
            "tables": 0,
            "table_cells": 0,
            "mathtype_ole": 0,
            "mathtype_ole_in_table_cells": 0,
            "ole_embeddings_resolved": 0,
            "ole_cfb_validated": 0,
            "eq_fields": 0,
            "eq_fields_in_table_cells": 0,
            "independent_images": 0,
            "formula_preview_media_refs": 0,
            "media_physical_files": 0,
            "media_extension_counts": {},
            "ole_embeddings": 0,
        }

    def parse(self) -> dict[str, Any]:
        document_xml = self.zf.read("word/document.xml")
        root = etree.fromstring(document_xml)
        body = root.find("w:body", namespaces=NS)
        if body is None:
            raise ValueError("word/document.xml missing w:body")

        for child in body:
            local = _local_name(child.tag)
            if local == "p":
                self._parse_body_paragraph(child)
            elif local == "tbl":
                self._parse_table(child)

        self._classify_media()
        self._summary["ole_embeddings"] = len(_collect_embedding_paths(self.zf))
        formulas = self.mathtype_oles + self.eq_fields
        return {
            "filename": self.filename,
            "sha256": _sha256_hex(self.source_bytes),
            "summary": dict(self._summary),
            "blocks": self.blocks if self.include_blocks else [],
            "mathtype_oles": self.mathtype_oles,
            "eq_fields": self.eq_fields,
            "formulas": formulas,
            "media": self.media,
        }

    def _next_formula_index(self) -> int:
        self._mathtype_counter += 1
        return self._mathtype_counter

    def _next_field_index(self) -> int:
        self._eq_counter += 1
        return self._eq_counter

    def _location(
        self,
        *,
        paragraph_index: int | None,
        table_index: int | None = None,
        row: int | None = None,
        col: int | None = None,
        run_index: int | None = None,
    ) -> dict[str, Any]:
        in_table_cell = table_index is not None
        return {
            "block_index": self._block_index,
            "paragraph_index": paragraph_index,
            "table_index": table_index,
            "row": row,
            "col": col,
            "run_index": run_index,
            "in_table_cell": in_table_cell,
        }

    def _parse_body_paragraph(self, paragraph_elem: etree._Element) -> None:
        self._block_index += 1
        self._paragraph_block_counter += 1
        paragraph_index = self._paragraph_counter
        self._paragraph_counter += 1
        self._summary["paragraphs"] += 1

        parsed = self._parse_paragraph_element(
            paragraph_elem,
            paragraph_index=paragraph_index,
            table_index=None,
            row=None,
            col=None,
        )
        if self.include_blocks:
            self.blocks.append(
                {
                    "type": "paragraph",
                    "block_index": self._block_index,
                    "paragraph_block_index": self._paragraph_block_counter - 1,
                    **parsed,
                }
            )

    def _parse_table(self, table_elem: etree._Element) -> None:
        self._block_index += 1
        self._table_counter += 1
        table_index = self._table_counter
        self._summary["tables"] += 1

        rows_out: list[dict[str, Any]] = []
        for row_idx, row_elem in enumerate(table_elem.findall("w:tr", namespaces=NS)):
            cells_out: list[dict[str, Any]] = []
            for col_idx, cell_elem in enumerate(row_elem.findall("w:tc", namespaces=NS)):
                self._summary["table_cells"] += 1
                paragraphs_out: list[dict[str, Any]] = []
                for paragraph_elem in cell_elem.findall("w:p", namespaces=NS):
                    paragraph_index = self._paragraph_counter
                    self._paragraph_counter += 1
                    self._summary["paragraphs"] += 1
                    parsed = self._parse_paragraph_element(
                        paragraph_elem,
                        paragraph_index=paragraph_index,
                        table_index=table_index,
                        row=row_idx,
                        col=col_idx,
                    )
                    paragraphs_out.append(parsed)
                cells_out.append(
                    {
                        "row_index": row_idx,
                        "col_index": col_idx,
                        "paragraphs": paragraphs_out,
                    }
                )
            rows_out.append({"row_index": row_idx, "cells": cells_out})

        if self.include_blocks:
            self.blocks.append(
                {
                    "type": "table",
                    "block_index": self._block_index,
                    "table_index": table_index,
                    "rows": rows_out,
                }
            )

    def _parse_paragraph_element(
        self,
        paragraph_elem: etree._Element,
        *,
        paragraph_index: int,
        table_index: int | None,
        row: int | None,
        col: int | None,
    ) -> dict[str, Any]:
        run_elements = list(_iter_run_elements(paragraph_elem))
        runs: list[dict[str, Any]] = []

        for run_index, run_elem in enumerate(run_elements):
            runs.append(
                {
                    "run_index": run_index,
                    "text": _extract_plain_text(run_elem),
                    "has_image": bool(
                        run_elem.xpath(".//v:imagedata", namespaces=NS)
                        or run_elem.xpath(".//a:blip", namespaces=NS)
                        or run_elem.xpath(".//w:drawing", namespaces=NS)
                        or run_elem.xpath(".//w:pict", namespaces=NS)
                    ),
                    "formula_refs": [],
                    "eq_field_refs": [],
                }
            )

        formula_refs = self._discover_mathtype_ole_in_paragraph(
            paragraph_elem,
            run_elements=run_elements,
            paragraph_index=paragraph_index,
            table_index=table_index,
            row=row,
            col=col,
        )
        for formula_id in formula_refs:
            run_index = self._formula_run_index.get(formula_id)
            if run_index is not None and run_index < len(runs):
                runs[run_index]["formula_refs"].append(formula_id)

        eq_field_refs: list[str] = []
        eq_records = self._parse_eq_fields(
            run_elements,
            paragraph_index=paragraph_index,
            table_index=table_index,
            row=row,
            col=col,
        )
        for eq_field in eq_records:
            eq_field_refs.append(eq_field["field_id"])
            begin_run = eq_field["location"].get("run_index")
            if begin_run is not None and begin_run < len(runs):
                runs[begin_run]["eq_field_refs"].append(eq_field["field_id"])

        text = _extract_plain_text(paragraph_elem)
        return {
            "paragraph_index": paragraph_index,
            "text": text,
            "plain_text": text,
            "runs": runs,
            "has_mathtype_ole": bool(formula_refs),
            "has_eq_field": bool(eq_field_refs),
            "has_image": _paragraph_has_image(paragraph_elem),
            "formula_refs": formula_refs,
            "eq_field_refs": eq_field_refs,
            "xml_path": _element_xml_path(paragraph_elem),
            "xml_sourceline": getattr(paragraph_elem, "sourceline", None),
        }

    def _discover_mathtype_ole_in_paragraph(
        self,
        paragraph_elem: etree._Element,
        *,
        run_elements: list[etree._Element],
        paragraph_index: int,
        table_index: int | None,
        row: int | None,
        col: int | None,
    ) -> list[str]:
        refs: list[str] = []
        seen_ole_ids: set[int] = set()
        for ole_elem in paragraph_elem.xpath(".//o:OLEObject", namespaces=NS):
            ole_key = id(ole_elem)
            if ole_key in seen_ole_ids:
                continue
            seen_ole_ids.add(ole_key)

            prog_id = str(ole_elem.get("ProgID") or "").strip()
            rel_id = ole_elem.get(f"{{{REL_NS}}}id")
            embedding_path, _ = _resolve_relationship_target("word/document.xml", rel_id or "", self.rel_maps)
            preview_rel_id = self._find_preview_image_rel_id(ole_elem)
            preview_path = None
            if preview_rel_id:
                preview_path, _ = _resolve_relationship_target("word/document.xml", preview_rel_id, self.rel_maps)
                if preview_path:
                    self._ole_preview_media_paths.add(preview_path.replace("\\", "/"))

            run_index = self._run_index_for_node(run_elements, ole_elem)
            formula_index = self._next_formula_index()
            formula_id = f"formula_{formula_index:04d}"
            self._formula_run_index[formula_id] = run_index if run_index is not None else 0
            location = self._location(
                paragraph_index=paragraph_index,
                table_index=table_index,
                row=row,
                col=col,
                run_index=run_index,
            )
            cfb_valid = _validate_ole_cfb(self.zf, embedding_path)
            record = {
                "formula_id": formula_id,
                "formula_index": formula_index,
                "kind": "mathtype_ole",
                "prog_id": prog_id or None,
                "relationship_id": rel_id,
                "embedding_path": embedding_path,
                "preview_media_path": preview_path,
                "preview_relationship_id": preview_rel_id,
                "cfb_valid": cfb_valid,
                "location": location,
                "xml_sourceline": getattr(ole_elem, "sourceline", None),
            }
            self.mathtype_oles.append(record)
            refs.append(formula_id)
            self._summary["mathtype_ole"] += 1
            if table_index is not None:
                self._summary["mathtype_ole_in_table_cells"] += 1
            if embedding_path:
                self._summary["ole_embeddings_resolved"] += 1
            if cfb_valid:
                self._summary["ole_cfb_validated"] += 1
        return refs

    @staticmethod
    def _run_index_for_node(run_elements: list[etree._Element], target: etree._Element) -> int | None:
        for run_index, run_elem in enumerate(run_elements):
            for node in run_elem.iter():
                if node is target:
                    return run_index
        return None

    def _find_preview_image_rel_id(self, ole_elem: etree._Element) -> str | None:
        object_parent = ole_elem.getparent()
        search_roots = [object_parent, ole_elem]
        while object_parent is not None and _local_name(object_parent.tag) != "p":
            search_roots.append(object_parent)
            object_parent = object_parent.getparent()
        for root in search_roots:
            if root is None:
                continue
            for imagedata in root.xpath(".//v:imagedata", namespaces=NS):
                rel_id = imagedata.get(f"{{{REL_NS}}}id")
                if rel_id:
                    return rel_id
            for blip in root.xpath(".//a:blip", namespaces=NS):
                rel_id = blip.get(f"{{{REL_NS}}}embed")
                if rel_id:
                    return rel_id
        return None

    def _parse_eq_fields(
        self,
        run_elements: list[etree._Element],
        *,
        paragraph_index: int,
        table_index: int | None,
        row: int | None,
        col: int | None,
    ) -> list[dict[str, Any]]:
        discovered: list[dict[str, Any]] = []
        in_field = False
        after_separate = False
        instr_parts: list[str] = []
        result_parts: list[str] = []
        begin_run_index: int | None = None

        for run_index, run_elem in enumerate(run_elements):
            for fld_char in run_elem.findall("w:fldChar", namespaces=NS):
                fld_type = fld_char.get(f"{{{W_NS}}}fldCharType")
                if fld_type == "begin":
                    in_field = True
                    after_separate = False
                    instr_parts = []
                    result_parts = []
                    begin_run_index = run_index
                elif fld_type == "separate" and in_field:
                    after_separate = True
                elif fld_type == "end" and in_field:
                    instruction = "".join(instr_parts).strip()
                    result_text = "".join(result_parts).strip()
                    if self._is_eq_instruction(instruction):
                        field_index = self._next_field_index()
                        field_id = f"eq_{field_index:04d}"
                        location = self._location(
                            paragraph_index=paragraph_index,
                            table_index=table_index,
                            row=row,
                            col=col,
                            run_index=begin_run_index,
                        )
                        record = {
                            "field_id": field_id,
                            "field_index": field_index,
                            "formula_id": field_id,
                            "kind": "eq_field",
                            "instruction": instruction,
                            "result_text": result_text or None,
                            "display_text": result_text or None,
                            "location": location,
                            "xml_sourceline": getattr(fld_char, "sourceline", None),
                        }
                        self.eq_fields.append(record)
                        discovered.append(record)
                        self._summary["eq_fields"] += 1
                        if table_index is not None:
                            self._summary["eq_fields_in_table_cells"] += 1
                    in_field = False
                    after_separate = False
                    instr_parts = []
                    result_parts = []
                    begin_run_index = None

            if not in_field:
                continue

            if not after_separate:
                for instr in run_elem.findall("w:instrText", namespaces=NS):
                    if instr.text:
                        instr_parts.append(instr.text)
            else:
                for text_node in run_elem.xpath(".//w:t", namespaces=NS):
                    if text_node.text:
                        result_parts.append(text_node.text)

        return discovered

    @staticmethod
    def _is_eq_instruction(instruction: str) -> bool:
        text = str(instruction or "").strip()
        if not text:
            return False
        upper = text.upper()
        return upper.startswith("EQ") or upper.startswith(" EQ") or " EQ " in f" {upper} "

    def _classify_media(self) -> None:
        extension_counts: dict[str, int] = {}
        formula_preview_refs = 0
        independent_images = 0

        for media_path in _collect_media_paths(self.zf):
            ext = os.path.splitext(media_path)[1].lower()
            ext_key = ext.lstrip(".") or "unknown"
            extension_counts[ext_key] = extension_counts.get(ext_key, 0) + 1
            normalized = media_path.replace("\\", "/")

            if normalized in self._ole_preview_media_paths:
                media_type = "formula_preview"
                formula_preview_refs += 1
            elif ext in INDEPENDENT_IMAGE_EXTS:
                media_type = "independent_image"
                independent_images += 1
            elif ext in FORMULA_PREVIEW_EXTS:
                media_type = "formula_preview"
            else:
                media_type = "other"

            self.media.append(
                {
                    "path": normalized,
                    "extension": ext_key,
                    "type": media_type,
                }
            )

        self._summary["media_physical_files"] = len(self.media)
        self._summary["media_extension_counts"] = extension_counts
        self._summary["formula_preview_media_refs"] = formula_preview_refs
        self._summary["independent_images"] = independent_images
        self._summary["paragraph_blocks"] = self._paragraph_block_counter


def parse_docx_structure(
    source: str | os.PathLike[str] | BinaryIO | bytes,
    *,
    filename: str | None = None,
    include_blocks: bool = True,
) -> dict[str, Any]:
    """Parse DOCX package into ordered blocks, formulas, and media metadata."""
    data, inferred_name = _read_source_bytes(source)
    final_name = filename or inferred_name or "upload.docx"
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        parser = _DocxStructureParser(
            zf,
            filename=final_name,
            include_blocks=include_blocks,
            source_bytes=data,
        )
        result = parser.parse()
    result["sha256"] = _sha256_hex(data)
    return result


def parse_docx_summary(
    source: str | os.PathLike[str] | BinaryIO | bytes,
    *,
    filename: str | None = None,
) -> dict[str, Any]:
    """Return filename + summary only (no blocks) for lightweight API responses."""
    parsed = parse_docx_structure(source, filename=filename, include_blocks=False)
    return {
        "filename": parsed["filename"],
        "sha256": parsed["sha256"],
        "summary": parsed["summary"],
        "mathtype_oles": parsed["mathtype_oles"],
        "eq_fields": parsed["eq_fields"],
        "formulas": parsed["formulas"],
        "media": parsed["media"],
    }


def compare_reference_statistics(summary: dict[str, Any]) -> list[dict[str, Any]]:
    """Compare parser summary against known reference values."""
    ext_counts = summary.get("media_extension_counts") or {}
    actual_map = {
        "mathtype_ole": summary.get("mathtype_ole"),
        "mathtype_ole_in_table_cells": summary.get("mathtype_ole_in_table_cells"),
        "eq_fields": summary.get("eq_fields"),
        "eq_fields_in_table_cells": summary.get("eq_fields_in_table_cells"),
        "tables": summary.get("tables"),
        "table_cells": summary.get("table_cells"),
        "independent_images": summary.get("independent_images"),
        "independent_jpeg": ext_counts.get("jpg", 0) + ext_counts.get("jpeg", 0),
        "independent_png": ext_counts.get("png", 0),
        "media_physical_files": summary.get("media_physical_files"),
        "media_wmf": ext_counts.get("wmf", 0),
        "media_jpeg": ext_counts.get("jpg", 0) + ext_counts.get("jpeg", 0),
        "media_png": ext_counts.get("png", 0),
        "ole_embeddings": summary.get("ole_embeddings"),
    }
    diffs: list[dict[str, Any]] = []
    for key, expected in REFERENCE_STATISTICS.items():
        actual = actual_map.get(key)
        if actual != expected:
            diffs.append(
                {
                    "metric": key,
                    "expected": expected,
                    "actual": actual,
                    "difference": None if actual is None else actual - expected,
                }
            )
    return diffs


def format_parse_summary_text(parsed: dict[str, Any]) -> str:
    """Human-readable parse summary for console / reports."""
    summary = parsed.get("summary") or {}
    ext_counts = summary.get("media_extension_counts") or {}
    jpeg_count = ext_counts.get("jpg", 0) + ext_counts.get("jpeg", 0)
    png_count = ext_counts.get("png", 0)
    wmf_count = ext_counts.get("wmf", 0)

    lines = [
        "DOCX Parse Summary",
        "------------------",
        f"Source:",
        f"{parsed.get('filename', '')}",
        "",
        "Ordered blocks:",
        f"Paragraph blocks: {summary.get('paragraph_blocks', 0)}",
        f"Tables: {summary.get('tables', 0)}",
        f"Table cells: {summary.get('table_cells', 0)}",
        f"Paragraphs (incl. table cells): {summary.get('paragraphs', 0)}",
        "",
        "MathType OLE:",
        f"Total: {summary.get('mathtype_ole', 0)}",
        f"Inside tables: {summary.get('mathtype_ole_in_table_cells', 0)}",
        f"Embeddings resolved: {summary.get('ole_embeddings_resolved', 0)}",
        f"CFB validated: {summary.get('ole_cfb_validated', 0)}",
        "",
        "EQ fields:",
        f"Total: {summary.get('eq_fields', 0)}",
        f"Inside tables: {summary.get('eq_fields_in_table_cells', 0)}",
        "",
        "Media:",
        f"Physical files: {summary.get('media_physical_files', 0)}",
        f"WMF: {wmf_count}",
        f"JPEG: {jpeg_count}",
        f"PNG: {png_count}",
        f"Formula preview refs: {summary.get('formula_preview_media_refs', 0)}",
        f"Independent images: {summary.get('independent_images', 0)}",
        f"OLE embeddings (package): {summary.get('ole_embeddings', 0)}",
    ]
    return "\n".join(lines)


def parse_reference_docx_from_storage(project_root: str | os.PathLike[str]) -> dict[str, Any]:
    """Parse the reference textbook DOCX from V3 source storage."""
    path = find_reference_docx_in_storage(project_root)
    if path is None:
        raise FileNotFoundError(
            f"Reference DOCX not found under {REFERENCE_SOURCE_REL_DIR.as_posix()} "
            f"matching {REFERENCE_BASENAME_FRAGMENT!r}"
        )
    return parse_docx_structure(path, filename=path.name, include_blocks=False)
